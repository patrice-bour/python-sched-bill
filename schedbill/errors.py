from flask import current_app, jsonify, request
from flask.app import BadRequest
from bson.errors import InvalidId
from mongoengine import ValidationError, DoesNotExist
import logging

logger = logging.getLogger()


def load():
    """Setup generic error handlers"""

    @current_app.errorhandler(Exception)
    def handle_exception(e):
        """Generic Exception handler"""

        logger.error(f"{request} Exception met : {str(e)}")
        return jsonify(error=f"Exception met : {str(e)}"), 500

    @current_app.errorhandler(AttributeError)
    def handle_exception(e):
        """Generic Exception handler"""

        logger.error(f"{request} Attribute error : {str(e)}")
        return jsonify(error=f"Attribute error : {str(e)}"), 500

    @current_app.errorhandler(BadRequest)
    def handle_bad_request(e):
        """Bad Request handler"""

        logger.error(f"{request}  {str(e)}")
        return jsonify(error=f"{str(e)}"), 400

    @current_app.errorhandler(InvalidId)
    def handle_invalid_id(e):
        """Handler for invalid bson ObjectId"""

        logger.error(f"{request} {str(e)}")
        return jsonify(error=f"{str(e)} in request"), 400

    @current_app.errorhandler(DoesNotExist)
    def handle_does_not_exist(e):
        """Handler for not existent documents"""

        logger.error(f"{request} : {str(e)}")
        return jsonify(error=f"{str(e)}"), 404

    @current_app.errorhandler(ValidationError)
    def handle_validation_error(e):
        """Handler for validation errors"""

        logger.error(f"{request} : {str(e)}")
        return jsonify(error=f"{str(e)}"), 500
