from mongoengine import Document, StringField, EmailField, IntField, BooleanField, ReferenceField


class User(Document):
    """"""
    meta = {'collection': 'users'}
    emailAddress = EmailField(required=True, unique=True)
    lastName = StringField()
    firstName = StringField()


class EMail(Document):
    """"""
    meta = {'collection': 'emails'}
    sender = ReferenceField(User)
    recipient = EmailField(required=True)
    title = StringField(default="")
    content = StringField(required=True)
    sendAt = IntField(default=0)


class Invoice(Document):
    """"""
    meta = {'collection': 'invoices'}
    sender = ReferenceField(User)
    recipient = ReferenceField(User)
    reference = StringField(unique=True, required=True)
    periodicity = IntField(default=0)
    notify = BooleanField(default=False)
    notifyAt = IntField(default=0)

