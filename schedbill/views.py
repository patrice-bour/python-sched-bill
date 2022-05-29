from flask import current_app, g, request, jsonify
from mongoengine import ValidationError, DoesNotExist
from bson import ObjectId
from bson.errors import InvalidId
from models import User, EMail, Invoice
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

    # GET user by id
    @current_app.route('/users/<string:id>', methods=['GET'])
    def get_user(id):
        """This route retrieves a user using its _id"""
        user = {}
        # validation of the ObjectId
        if not ObjectId.is_valid(id):
            logger.error(f"{request} invalid ObjectId '{id}'")
            return jsonify(error=f"Invalid ObjectId '{id}' in request"), 400

        try:
            user = User.objects.get(id=id)
        except DoesNotExist as exc:
            logger.error(f"{request} : {str(exc)}")
            return jsonify(error=f"{str(exc)}"), 404
        except Exception as exc:
            logger.error(f"{request} Exception met while retrieving user '{id}' : {str(exc)}")
            return jsonify(error=f"{request} Exception met while retrieving user _id '{id}'"), 500

        logger.debug(f"{request} responded with user with ObjectId '{id}'")
        return jsonify(data=user), 200

    # GET user by email
    @current_app.route('/users/emailAddress/<string:email>', methods=['GET'])
    def get_user_by_email(email):
        """This route retrieves a user using its email address"""
        user = {}

        try:
            user = User.objects.get(emailAddress=email)
        except DoesNotExist as exc:
            logger.error(f"{request} User '{email}' : {str(exc)}")
            return jsonify(error=f"{str(exc)}"), 404
        except Exception as exc:
            logger.error(f"{request} Exception met while retrieving User email address '{email}' : {str(exc)}")
            return jsonify(error=f"{request} Exception met while retrieving User with email address '{email}'"), 500

        logger.debug(f"{request} responded with user with email '{email}'")
        return jsonify(data=user), 200

    # POST new user
    @current_app.route('/users', methods=['POST'])
    def new_user():
        """This route creates a new user in the database"""
        raw_user = None
        user = None

        # First, check that the request can be decoded as JSON
        try:
            raw_user = request.get_json()
        except Exception as exc:
            logger.error(f"Error decoding {request} : {str(exc)}")
            return jsonify(error=f"{str(exc)}"), 400

        # Instantiate a new User
        try:
            user = User(**raw_user)
        except Exception as exc:
            logger.error(f"{request} Exception met while instantiating User : {str(exc)}")
            return jsonify(error=f"{str(exc)}"), 500

        # Save the new user
        try:
            user.save()
        except ValidationError as exc:
            logger.error(f"{request} Exception met while saving a new user : {str(exc)}")
            return jsonify(error=f"{str(exc)}"), 500
        except Exception as exc:
            logger.error(f"{request} Exception met while saving a new user : {str(exc)}")
            return jsonify(error=f"Can not save user : {raw_user}"), 500

        logger.debug(f"{request} successfully created a new user'")
        return jsonify(data=user), 201

    # PUT (update) user by id
    @current_app.route('/users/<string:id>', methods=['PUT'])
    def update_user(id):
        """This route updates a user, identified by its id, in the database"""
        updated_user = None
        user = None
        success = False

        # First, check that the request can be decoded as JSON
        try:
            updated_user = request.get_json()
        except Exception as exc:
            logger.error(f"Error decoding {request} : {str(exc)}")
            return jsonify(error=f"{str(exc)}"), 400

        # validation of the ObjectId
        if not ObjectId.is_valid(id):
            logger.error(f"{request} invalid ObjectId '{id}'")
            return jsonify(error=f"Invalid ObjectId '{id}' in request"), 400

        try:
            success = User.objects(id=id).modify(**updated_user)
        except DoesNotExist as exc:
            logger.error(f"{request} : {str(exc)}")
            return jsonify(error=f"{str(exc)}"), 404
        except Exception as exc:
            logger.error(f"{request} Exception met while updating User '{id}' : {str(exc)}")
            return jsonify(error=f"{request} Exception met while updating User _id '{id}'"), 500

        if success:
            logger.debug(f"{request} successfully updated user with id {id}'")
            return jsonify(data=user), 200
        else:
            logger.error(f"{request} Can not find user with id '{id}' to modify")
            return jsonify(error="Can not find user with id '{id}' to modify"), 404

    # DELETE user by id
    @current_app.route('/users/<string:id>', methods=['DELETE'])
    def delete_user(id):
        """This route deletes a user, identified by its id, in the database"""
        user = {}
        # validation of the ObjectId
        if not ObjectId.is_valid(id):
            logger.error(f"{request} invalid ObjectId '{id}'")
            return jsonify(error=f"Invalid ObjectId '{id}' in request"), 400

        try:
            user = User.objects.get(id=id)
        except DoesNotExist as exc:
            logger.error(f"{request} : {str(exc)}")
            return jsonify(error=f"{str(exc)}"), 404
        except Exception as exc:
            logger.error(f"{request} Exception met while retrieving User '{id}' : {str(exc)}")
            return jsonify(error=f"{request} Exception met while retrieving User _id '{id}'"), 500

        try:
            user.delete()
        except Exception as exc:
            logger.error(f"{request} Exception met while deleting User '{id}' : {str(exc)}")
            return jsonify(error=f"{request} Exception met while deleting User _id '{id}'"), 500

        logger.debug(f"{request} successfully deleted user with id {id}'")
        return jsonify({}), 204

    #
    # EMail routes
    #

    # GET email by id
    @current_app.route('/emails/<string:id>', methods=['GET'])
    def get_email(id):
        """This route retrieves an email using its _id"""
        email = {}
        # validation of the ObjectId
        if not ObjectId.is_valid(id):
            logger.error(f"{request} invalid ObjectId '{id}'")
            return jsonify(error=f"Invalid ObjectId '{id}' in request"), 400

        try:
            email = EMail.objects.no_dereference().get(id=id)
        except DoesNotExist as exc:
            logger.error(f"{request} : {str(exc)}")
            return jsonify(error=f"{str(exc)}"), 404
        except Exception as exc:
            logger.error(f"{request} Exception met while retrieving email '{id}' : {str(exc)}")
            return jsonify(error=f"{request} Exception met while retrieving email _id '{id}'"), 500

        logger.debug(f"{request} responded with email with ObjectId '{id}'")
        return jsonify(data=email), 200

    # POST new email
    @current_app.route('/emails', methods=['POST'])
    def new_email():
        """This route creates a new email in the database"""
        raw_email = None
        email = None

        # First, check that the request can be decoded as JSON
        try:
            raw_email = request.get_json()
        except Exception as exc:
            logger.error(f"Error decoding {request} : {str(exc)}")
            return jsonify(error=f"{str(exc)}"), 400

        # Instantiate a new Email
        try:
            email = EMail(**raw_email)
        except Exception as exc:
            logger.error(f"{request} Exception met while instantiating EMail : {str(exc)}")
            return jsonify(error=f"{str(exc)}"), 500

        # Save the new email
        try:
            email.save()
        except ValidationError as exc:
            logger.error(f"{request} Exception met while saving a new email : {str(exc)}")
            return jsonify(error=f"{str(exc)}"), 500
        except Exception as exc:
            logger.error(f"{request} Exception met while saving a new email : {str(exc)}")
            return jsonify(error=f"Can not save email : {raw_email}"), 500

        logger.debug(f"{request} successfully created a new email'")
        return jsonify(data=email), 201

    # PUT (update) email by id
    @current_app.route('/emails/<string:id>', methods=['PUT'])
    def update_email(id):
        """This route updates an email, identified by its id, in the database"""
        updated_email = None
        email = None
        success = False

        # First, check that the request can be decoded as JSON
        try:
            updated_email = request.get_json()
        except Exception as exc:
            logger.error(f"Error decoding {request} : {str(exc)}")
            return jsonify(error=f"{str(exc)}"), 400

        # validation of the ObjectId
        if not ObjectId.is_valid(id):
            logger.error(f"{request} invalid ObjectId '{id}'")
            return jsonify(error=f"Invalid ObjectId '{id}' in request"), 400

        try:
            email = EMail.objects(id=id)
            success = email.modify(**updated_email)
        except DoesNotExist as exc:
            logger.error(f"{request} : {str(exc)}")
            return jsonify(error=f"{str(exc)}"), 404
        except Exception as exc:
            logger.error(f"{request} Exception met while updating email '{id}' : {str(exc)}")
            return jsonify(error=f"{request} Exception met while updating email _id '{id}'"), 500

        if success:
            logger.debug(f"{request} successfully updated email with id {id}'")
            return jsonify(data=email), 200
        else:
            logger.error(f"{request} Can not find email with id '{id}' to modify")
            return jsonify(error="Can not find email with id '{id}' to modify"), 404

    # DELETE email by id
    @current_app.route('/emails/<string:id>', methods=['DELETE'])
    def delete_email(id):
        """This route deletes an email, identified by its id, in the database"""
        email = {}
        # validation of the ObjectId
        if not ObjectId.is_valid(id):
            logger.error(f"{request} invalid ObjectId '{id}'")
            return jsonify(error=f"Invalid ObjectId '{id}' in request"), 400

        try:
            email = EMail.objects.get(id=id)
        except DoesNotExist as exc:
            logger.error(f"{request} : {str(exc)}")
            return jsonify(error=f"{str(exc)}"), 404
        except Exception as exc:
            logger.error(f"{request} Exception met while retrieving Email '{id}' : {str(exc)}")
            return jsonify(error=f"{request} Exception met while retrieving Email _id '{id}'"), 500

        try:
            email.delete()
        except Exception as exc:
            logger.error(f"{request} Exception met while deleting Email '{id}' : {str(exc)}")
            return jsonify(error=f"{request} Exception met while deleting Email _id '{id}'"), 500

        logger.debug(f"{request} successfully deleted email with id {id}'")
        return jsonify({}), 204
    
    #
    # Invoice routes
    #

    # GET invoice by id
    @current_app.route('/invoices/<string:id>', methods=['GET'])
    def get_invoice(id):
        """This route retrieves an invoice using its _id"""
        invoice = {}
        # validation of the ObjectId
        if not ObjectId.is_valid(id):
            logger.error(f"{request} invalid ObjectId '{id}'")
            return jsonify(error=f"Invalid ObjectId '{id}' in request"), 400

        try:
            invoice = Invoice.objects.no_dereference().get(id=id)
        except DoesNotExist as exc:
            logger.error(f"{request} : {str(exc)}")
            return jsonify(error=f"{str(exc)}"), 404
        except Exception as exc:
            logger.error(f"{request} Exception met while retrieving invoice '{id}' : {str(exc)}")
            return jsonify(error=f"{request} Exception met while retrieving invoice _id '{id}'"), 500

        logger.debug(f"{request} responded with invoice with ObjectId '{id}'")
        return jsonify(data=invoice), 200

    # POST new invoice
    @current_app.route('/invoices', methods=['POST'])
    def new_invoice():
        """This route creates a new invoice in the database"""
        raw_invoice = None
        invoice = None

        # First, check that the request can be decoded as JSON
        try:
            raw_invoice = request.get_json()
        except Exception as exc:
            logger.error(f"Error decoding {request} : {str(exc)}")
            return jsonify(error=f"{str(exc)}"), 400

        # Instantiate a new Invoice
        try:
            invoice = Invoice(**raw_invoice)
        except Exception as exc:
            logger.error(f"{request} Exception met while instantiating Invoice : {str(exc)}")
            return jsonify(error=f"{str(exc)}"), 500

        # Save the new invoice
        try:
            invoice.save()
        except ValidationError as exc:
            logger.error(f"{request} Exception met while saving a new invoice : {str(exc)}")
            return jsonify(error=f"{str(exc)}"), 500
        except Exception as exc:
            logger.error(f"{request} Exception met while saving a new invoice : {str(exc)}")
            return jsonify(error=f"Can not save invoice : {raw_invoice}"), 500

        logger.debug(f"{request} successfully created a new invoice'")
        return jsonify(data=invoice), 201
    
    # PUT (update) invoice by id
    @current_app.route('/invoices/<string:id>', methods=['PUT'])
    def update_invoice(id):
        """This route updates an invoice, identified by its id, in the database"""
        updated_invoice = None
        invoice = None
        success = False

        # First, check that the request can be decoded as JSON
        try:
            updated_invoice = request.get_json()
        except Exception as exc:
            logger.error(f"Error decoding {request} : {str(exc)}")
            return jsonify(error=f"{str(exc)}"), 400

        # validation of the ObjectId
        if not ObjectId.is_valid(id):
            logger.error(f"{request} invalid ObjectId '{id}'")
            return jsonify(error=f"Invalid ObjectId '{id}' in request"), 400

        try:
            invoice = Invoice.objects(id=id)
            success = invoice.modify(**updated_invoice)
        except DoesNotExist as exc:
            logger.error(f"{request} : {str(exc)}")
            return jsonify(error=f"{str(exc)}"), 404
        except Exception as exc:
            logger.error(f"{request} Exception met while updating invoice '{id}' : {str(exc)}")
            return jsonify(error=f"{request} Exception met while updating invoice _id '{id}'"), 500

        if success:
            logger.debug(f"{request} successfully updated invoice with id {id}'")
            return jsonify(data=invoice), 200
        else:
            logger.error(f"{request} Can not find invoice with id '{id}' to modify")
            return jsonify(error="Can not find invoice with id '{id}' to modify"), 404

    # DELETE invoice by id
    @current_app.route('/invoices/<string:id>', methods=['DELETE'])
    def delete_invoice(id):
        """This route deletes an invoice, identified by its id, in the database"""
        invoice = {}
        # validation of the ObjectId
        if not ObjectId.is_valid(id):
            logger.error(f"{request} invalid ObjectId '{id}'")
            return jsonify(error=f"Invalid ObjectId '{id}' in request"), 400

        try:
            invoice = Invoice.objects.get(id=id)
        except DoesNotExist as exc:
            logger.error(f"{request} : {str(exc)}")
            return jsonify(error=f"{str(exc)}"), 404
        except Exception as exc:
            logger.error(f"{request} Exception met while retrieving Invoice '{id}' : {str(exc)}")
            return jsonify(error=f"{request} Exception met while retrieving Invoice _id '{id}'"), 500

        try:
            invoice.delete()
        except Exception as exc:
            logger.error(f"{request} Exception met while deleting Invoice '{id}' : {str(exc)}")
            return jsonify(error=f"{request} Exception met while deleting Invoice _id '{id}'"), 500

        logger.debug(f"{request} successfully deleted invoice with id {id}'")
        return jsonify({}), 204