from flask import current_app, g, request, jsonify
from mongoengine import ValidationError, DoesNotExist
from bson import ObjectId
from bson.errors import InvalidId
from models import User, EMail, Invoice
from timing import TimeCalc
import logging


logger = logging.getLogger()


class UserController:
    """"""

    @classmethod
    def find(cls, oid: str) -> User:
        """Find a user and return it

        :param oid: the ObjectId of the document
        :return: User's document matching the id
        """

        if not ObjectId.is_valid(oid):
            raise InvalidId(f"Invalid ObjectId '{oid}'")
        user = User.objects.get(id=oid)

        return user

    @classmethod
    def find_by_email(cls, email_address: str):
        """Find a user and return it

        :param email_address: the email address of the document
        :return: User's document matching the user address
        """

        user = User.objects.get(emailAddress=email_address)

        return user

    @classmethod
    def create_user(cls, raw_user: dict) -> User:
        """Create a new user and return it

        :param raw_user: the properties of the document
        :return: the new User
        """

        user = User(**raw_user)
        user.save()

        return user

    @classmethod
    def update_user(cls, oid: str, updated_user: dict) -> User:
        """Update a user and return it

        :param oid: the ObjectId of the document
        :param updated_user: the properties to update in the document
        :return: the updated User
        """

        if not ObjectId.is_valid(oid):
            raise InvalidId(f"Invalid ObjectId '{oid}'")
        user = User.objects(id=oid).modify(**updated_user)
        if not user:
            raise DoesNotExist(f"Can not find user with id '{oid}'")

        return user

    @classmethod
    def delete_user(cls, oid: str) -> None:
        """Delete a user

        :param oid: the ObjectId of the document
        :return:
        """

        if not ObjectId.is_valid(oid):
            raise InvalidId(f"Invalid ObjectId '{oid}'")
        user = User.objects.get(id=oid)
        user.delete()


class EMailController:
    """"""

    @classmethod
    def find(cls, oid: str) -> EMail:
        """Find a email and return it

        :param oid: the ObjectId of the document
        :return: EMail's document matching the id
        """

        if not ObjectId.is_valid(oid):
            raise InvalidId(f"Invalid ObjectId '{oid}'")
        email = EMail.objects.no_dereference().get(id=oid)

        return email

    @classmethod
    def create_email(cls, raw_email: dict) -> EMail:
        """Create a new email and return it

        :param raw_email: the properties of the document
        :return: the new EMail
        """

        # Reckon sending time
        if raw_email.get('sendAt', 0) > 0:
            raw_email['sendAt'] = TimeCalc.convert_to_store(raw_email['sendAt'])
        email = EMail(**raw_email)
        email.save()
        cls.schedule_email(email)

        return email

    @classmethod
    def update_email(cls, oid: str, updated_email: dict) -> EMail:
        """Update an email and return it

        :param updated_email: the properties to update in the document
        :param oid: the ObjectId of the document
        :return: the updated EMail
        """

        if not ObjectId.is_valid(oid):
            raise InvalidId(f"Invalid ObjectId '{oid}'")
        # Reckon sending time
        if updated_email.get('sendAt', 0) > 0:
            updated_email['sendAt'] = TimeCalc.convert_to_store(updated_email['sendAt'])
        email = EMail.objects(id=oid).modify(**updated_email)
        if not email:
            raise DoesNotExist(f"Can not find email with id '{oid}'")
        cls.schedule_email(email)

        return email

    @classmethod
    def delete_email(cls, oid: str) -> None:
        """Delete an email

        :param oid: the ObjectId of the document
        """

        if not ObjectId.is_valid(oid):
            raise InvalidId(f"Invalid ObjectId '{oid}'")
        email = EMail.objects.get(id=oid)
        cls.schedule_email(email)

        email.delete()

    @classmethod
    def schedule_email(cls, email: EMail) -> int:
        """"""
        if email.sendAt > 0:
            # replace_existing is set to true. This would then also update an existing job's schedule.
            g.scheduler.add_job(EMailController.send_email, 'date', args=[str(email.id)], id=str(email.id),
                                replace_existing=True)
            return 1
        else:
            # any existing job's schedule has to be deleted.
            ret = cls.unschedule_email(email)
            return ret if ret == 0 else -1

    @classmethod
    def unschedule_email(cls, email: EMail) -> int:
        """"""

        if g.scheduler.get_job(str(email.id)) is not None:
            g.scheduler.remove_job(str(email.id))
            return 1
        else:
            return 0

    @classmethod
    def send_email(cls, oid: str) -> None:
        """"""

        email = cls.find(oid)
        logger.info(f"*** Sending email : {email.to_json()}")


class InvoiceController:
    """"""

    @classmethod
    def find(cls, oid: str) -> Invoice:
        """Find a invoice and return it

        :param oid: the ObjectId of the document
        :return: Invoice's document matching the id
        """

        if not ObjectId.is_valid(oid):
            raise InvalidId(f"Invalid ObjectId '{oid}'")
        invoice = Invoice.objects.no_dereference().get(id=oid)

        return invoice

    @classmethod
    def create_invoice(cls, raw_invoice: dict) -> Invoice:
        """Create a new invoice and return it

        :param raw_invoice: the properties of the document
        :return: the new Invoice
        """

        invoice = Invoice(**raw_invoice)
        invoice.save()

        return invoice

    @classmethod
    def update_invoice(cls, oid: str, updated_invoice: dict) -> Invoice:
        """Update a invoice and return it

        :param oid: the ObjectId of the document
        :param updated_invoice: the properties to update in the document
        :return: the updated Invoice
        """

        if not ObjectId.is_valid(oid):
            raise InvalidId(f"Invalid ObjectId '{oid}'")
        invoice = Invoice.objects(id=oid).modify(**updated_invoice)
        if not invoice:
            raise DoesNotExist(f"Can not find invoice with id '{oid}'")

        return invoice

    @classmethod
    def delete_invoice(cls, oid: str) -> None:
        """Delete a invoice

        :param oid: the ObjectId of the document
        """

        if not ObjectId.is_valid(oid):
            raise InvalidId(f"Invalid ObjectId '{oid}'")
        invoice = Invoice.objects.get(id=oid)
        invoice.delete()
