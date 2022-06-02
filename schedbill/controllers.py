from flask import current_app, g, request, jsonify
from mongoengine import ValidationError, DoesNotExist
from bson import ObjectId
from bson.errors import InvalidId
from models import User, EMail, Invoice
from datetime import datetime
import pytz
import logging


logger = logging.getLogger()


class UserController():
    """"""

    @classmethod
    def find(cls, oid):
        """Find a user and return it

        :param oid: the ObjectId of the document
        :return: User's document matching the id
        """

        if not ObjectId.is_valid(oid):
            raise InvalidId(f"Invalid ObjectId '{oid}'")
        user = User.objects.get(id=oid)

        return user

    @classmethod
    def find_by_email(cls, email_address):
        """Find a user and return it

        :param email_address: the email address of the document
        :return: User's document matching the user address
        """

        user = User.objects.get(emailAddress=email_address)

        return user

    @classmethod
    def create_user(cls):
        """Create a new user and return it

        :return: the new User
        """

        raw_user = request.get_json()
        user = User(**raw_user)
        user.save()

        return user

    @classmethod
    def update_user(cls, oid):
        """Update a user and return it

        :param oid: the ObjectId of the document
        :return: the updated User
        """

        updated_user = request.get_json()
        if not ObjectId.is_valid(oid):
            raise InvalidId(f"Invalid ObjectId '{oid}'")
        user = User.objects(id=oid).modify(**updated_user)
        if not user:
            raise DoesNotExist(f"Can not find user with id '{oid}'")

        return user

    @classmethod
    def delete_user(cls, oid):
        """Delete a user

        :param oid: the ObjectId of the document
        :return:
        """

        if not ObjectId.is_valid(oid):
            raise InvalidId(f"Invalid ObjectId '{oid}'")
        user = User.objects.get(id=oid)
        user.delete()


class EMailController():
    """"""

    @classmethod
    def find(cls, oid):
        """Find a email and return it

        :param oid: the ObjectId of the document
        :return: EMail's document matching the id
        """

        if not ObjectId.is_valid(oid):
            raise InvalidId(f"Invalid ObjectId '{oid}'")
        email = EMail.objects.no_dereference().get(id=oid)

        return email

    @classmethod
    def create_email(cls):
        """Create a new email and return it

        :return: the new EMail
        """

        raw_email = request.get_json()
        # Reckon sending time

        email = EMail(**raw_email)
        email.save()

        return email

    @classmethod
    def update_email(cls, oid):
        """Update a email and return it

        :param oid: the ObjectId of the document
        :return: the updated EMail
        """

        updated_email = request.get_json()
        if not ObjectId.is_valid(oid):
            raise InvalidId(f"Invalid ObjectId '{oid}'")
        email = EMail.objects(id=oid).modify(**updated_email)
        if not email:
            raise DoesNotExist(f"Can not find email with id '{oid}'")

        return email

    @classmethod
    def delete_email(cls, oid):
        """Delete a email

        :param oid: the ObjectId of the document
        """

        if not ObjectId.is_valid(oid):
            raise InvalidId(f"Invalid ObjectId '{oid}'")
        email = EMail.objects.get(id=oid)
        email.delete()

    @classmethod
    def schedule_email(cls, email):
        """"""

        if email.sendAt > 0:
            g.scheduler.add_job(cls.send_email(), '', args=email.id, id=email.id, replace_existing=True)
        else:
            try:
                g.scheduler.remove_job(email.id)
            except Exception as exc:
                raise Exception(exc)


    @classmethod
    def send_email(cls, oid):
        """"""

        email = cls.find(oid)
        logger.info(f"*** Sending email : {email.to_json()}")

class InvoiceController():
    """"""

    @classmethod
    def find(cls, oid):
        """Find a invoice and return it

        :param oid: the ObjectId of the document
        :return: Invoice's document matching the id
        """

        if not ObjectId.is_valid(oid):
            raise InvalidId(f"Invalid ObjectId '{oid}'")
        invoice = Invoice.objects.no_dereference().get(id=oid)

        return invoice

    @classmethod
    def create_invoice(cls):
        """Create a new invoice and return it

        :return: the new Invoice
        """

        raw_invoice = request.get_json()
        invoice = Invoice(**raw_invoice)
        invoice.save()

        return invoice

    @classmethod
    def update_invoice(cls, oid):
        """Update a invoice and return it

        :param oid: the ObjectId of the document
        :return: the updated Invoice
        """

        updated_invoice = request.get_json()
        if not ObjectId.is_valid(oid):
            raise InvalidId(f"Invalid ObjectId '{oid}'")
        invoice = Invoice.objects(id=oid).modify(**updated_invoice)
        if not invoice:
            raise DoesNotExist(f"Can not find invoice with id '{oid}'")

        return invoice

    @classmethod
    def delete_invoice(cls, oid):
        """Delete a invoice

        :param oid: the ObjectId of the document
        """

        if not ObjectId.is_valid(oid):
            raise InvalidId(f"Invalid ObjectId '{oid}'")
        invoice = Invoice.objects.get(id=oid)
        invoice.delete()