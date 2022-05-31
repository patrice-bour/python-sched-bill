import mongoengine
from flask import current_app, g
from flask_mongoengine import MongoEngine
import logging
import config
from pymongo import monitoring
from pymongo.monitoring import CommandStartedEvent, CommandSucceededEvent, CommandFailedEvent


logger = logging.getLogger()


# class CommandLogger(monitoring.CommandListener):
#     """This class extends a utility class provided by pymongo.monitoring.
#      It is going to monitor and log the MongoDB driver events."""
#
#     def started(self, event: "CommandStartedEvent") -> None:
#         """"""
#         logger.debug(
#             "Command {0.command_name} (0.request_id) started on server {0.connection_id}".format(
#                 event
#             )
#         )
#
#     def succeeded(self, event: "CommandSucceededEvent") -> None:
#         """"""
#         logger.debug(
#             "Command {0.command_name} (0.request_id) started on server {0.connection_id} "
#             "succeeded in {0.duration_micros} microseconds.".format(
#                 event
#             )
#         )
#
#     def failed(self, event: "CommandFailedEvent") -> None:
#         """"""
#         logger.debug(
#             "Command {0.command_name} (0.request_id) started on server {0.connection_id} "
#             "failed in {0.duration_micros} microseconds.".format(
#                 event
#             )
#         )

def get_db() -> MongoEngine:
    """Set or return the MongoEngine connection to the MongoDB driver"""
    if 'db' not in g:
        current_app.config['MONGODB_SETTINGS'] = {
            'host': current_app.config.get('DB_URI_FORMAT').format(
                user=current_app.config.get('DB_USER'),
                secret=current_app.config.get('DB_SECRET'),
                host=current_app.config.get('DB_HOST'),
                db=current_app.config.get('DB_NAME')
            )
        }
        try:
            g.db = MongoEngine(current_app)
        except Exception as exc:
            logger.error(f"Can not connect to Mongo DB {str(exc)}")
    return g.db


def connect_db(conf=config.DevelopmentConfiguration) -> MongoEngine:
    """"""
    conn = None
    host_config = conf.DB_URI_FORMAT.format(
        user=conf.DB_USER,
        secret=conf.DB_SECRET,
        host=conf.DB_HOST,
        db=conf.DB_NAME
    )
    try:
        conn = mongoengine.connect(host=host_config)
    except Exception as exc:
        logger.error(f"Can not connect to Mongo DB {str(exc)}")
    return conn

# monitoring.register(CommandLogger())
