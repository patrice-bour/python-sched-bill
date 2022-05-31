from flask import current_app, g, request, jsonify
from mongoengine import ValidationError, DoesNotExist
from bson import ObjectId
from bson.errors import InvalidId
from models import User, EMail, Invoice
from controllers import UserController, EMailController, InvoiceController
import logging

logger = logging.getLogger()


def load():
    """Setup routes using the Flask app context"""

    #
    # Home and static routes
    #
    @current_app.route('/')
    def home():
        return 'The documentation would fit here'

    #
    # User routes
    #

    # GET user by oid
    @current_app.route('/users/<string:oid>', methods=['GET'])
    def get_user(oid):
        """This route retrieves a user using its _id"""
        user = UserController.find(oid)
        logger.debug(f"{request} responded with user with id '{oid}'")
        return jsonify(data=user), 200

    # GET user by email
    @current_app.route('/users/emailAddress/<string:email>', methods=['GET'])
    def get_user_by_email(email):
        """This route retrieves a user using its email address"""
        user = UserController.find_by_email(email)
        logger.debug(f"{request} responded with user with email '{email}'")
        return jsonify(data=user), 200

    # POST new user
    @current_app.route('/users', methods=['POST'])
    def new_user():
        """This route creates a new user in the database"""
        user = UserController.create_user()
        logger.debug(f"{request} successfully created a new user'")
        return jsonify(data=user), 201

    # PUT (update) user by oid
    @current_app.route('/users/<string:oid>', methods=['PUT'])
    def update_user(oid):
        """This route updates a user, identified by its oid, in the database"""
        user = UserController.update_user(oid)
        logger.debug(f"{request} successfully updated user with id {oid}'")
        return jsonify(data=user), 200

    # DELETE user by oid
    @current_app.route('/users/<string:oid>', methods=['DELETE'])
    def delete_user(oid):
        """This route deletes a user, identified by its oid, in the database"""
        UserController.delete_user(oid)
        logger.debug(f"{request} successfully deleted user with id {oid}'")
        return jsonify({}), 204

    #
    # EMail routes
    #

    # GET email by id
    @current_app.route('/emails/<string:oid>', methods=['GET'])
    def get_email(oid):
        """This route retrieves an email using its _id"""
        email = EMailController.find(oid)

        logger.debug(f"{request} responded with email with id '{oid}'")
        return jsonify(data=email), 200

    # POST new email
    @current_app.route('/emails', methods=['POST'])
    def new_email():
        """This route creates a new email in the database"""
        email = EMailController.create_email()

        logger.debug(f"{request} successfully created a new email'")
        return jsonify(data=email), 201

    # PUT (update) email by id
    @current_app.route('/emails/<string:oid>', methods=['PUT'])
    def update_email(oid):
        """This route updates an email, identified by its id, in the database"""
        email = EMailController.update_email(oid)
        logger.debug(f"{request} successfully updated email with id {oid}'")
        return jsonify(data=email), 200

    # DELETE email by id
    @current_app.route('/emails/<string:oid>', methods=['DELETE'])
    def delete_email(oid):
        """This route deletes an email, identified by its id, in the database"""
        EMailController.delete_email(oid)

        logger.debug(f"{request} successfully deleted email with id {oid}'")
        return jsonify({}), 204

    #
    # Invoice routes
    #

    # GET invoice by id
    @current_app.route('/invoices/<string:oid>', methods=['GET'])
    def get_invoice(oid):
        """This route retrieves an invoice using its _id"""
        invoice = InvoiceController.find(oid)

        logger.debug(f"{request} responded with invoice with ObjectId '{oid}'")
        return jsonify(data=invoice), 200

    # POST new invoice
    @current_app.route('/invoices', methods=['POST'])
    def new_invoice():
        """This route creates a new invoice in the database"""
        invoice = InvoiceController.create_invoice()

        logger.debug(f"{request} successfully created a new invoice'")
        return jsonify(data=invoice), 201

    # PUT (update) invoice by id
    @current_app.route('/invoices/<string:oid>', methods=['PUT'])
    def update_invoice(oid):
        """This route updates an invoice, identified by its id, in the database"""
        invoice = InvoiceController.update_invoice(oid)
        logger.debug(f"{request} successfully updated invoice with id {id}'")
        return jsonify(data=invoice), 200

    # DELETE invoice by id
    @current_app.route('/invoices/<string:oid>', methods=['DELETE'])
    def delete_invoice(oid):
        """This route deletes an invoice, identified by its id, in the database"""
        InvoiceController.delete_invoice(oid)
        logger.debug(f"{request} successfully deleted invoice with id {id}'")
        return jsonify({}), 204