import unittest
from schedbill import create_app, config, db
from schedbill.models import EMail
from mongoengine.errors import DoesNotExist, NotUniqueError, ValidationError
from fixtures.col import drop_collections
from fixtures.emails import create_emails
import mongoengine
import json
from bson import ObjectId


class EMailModelTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.conn = db.connect_db(config.TestingConfiguration)
        cls.raw_db = mongoengine.connection.get_db()
        # Empty collections on testing DB
        for col in cls.raw_db.list_collection_names():
            cls.raw_db[col].drop()

    def setUp(self) -> None:
        drop_collections(EMailModelTestCase.raw_db)
        create_emails(self, EMailModelTestCase.raw_db)

    def test_email_finding(self):
        """Test retrieving a email into a EMail model"""
        email = EMail.objects.get(id=self.email1_json['_id']['$oid'])
        self.assertDictEqual(self.email1_json, json.loads(email.to_json()))

    def test_email_save(self):
        """Test saving a EMail model"""
        # Can save a valid email
        self.email_in_test_json.pop('sender')
        email = EMail(**self.email_in_test_json)
        email.save()
        email_find = EMail.objects.no_dereference().get(id=str(email.id))
        self.email_in_test_json['_id'] = { '$oid': str(email.id)}
        self.assertDictEqual(self.email_in_test_json, json.loads(email_find.to_json()))
        # attempt to create another email with an invalid recipient will raise an exception
        email_raising = EMail.objects.get(id=self.email1_json['_id']['$oid'])
        setattr(email_raising, 'recipient', 'foo.xyz.com')
        self.assertRaises(ValidationError, lambda: email_raising.save())
        # attempt to create another email without a content field will raise an exception
        email_raising = EMail.objects.get(id=self.email2_json['_id']['$oid'])
        delattr(email_raising, 'content')
        self.assertRaises(ValidationError, lambda: email_raising.save())

    def test_email_update(self):
        """Test updating a EMail model"""
        email = EMail(**self.email_in_test_json)
        email.sender = ObjectId(self.email1_json['sender']['$oid'])
        self.email_in_test_json['sender'] = {'$oid': self.email1_json['sender']['$oid']}
        email.save()
        email_find = EMail.objects.no_dereference().get(id=str(email.id))
        self.email_in_test_json['_id'] = { '$oid': str(email.id)}
        self.assertDictEqual(self.email_in_test_json, json.loads(email_find.to_json()))
        self.assertNotEqual(email.title, self.email1_json.get('title'))
        email.title = self.email1_json.get('title')
        self.assertEqual(email.title, self.email1_json.get('title'))
        self.assertNotEqual(email.content, self.email1_json.get('content'))
        email.content = self.email1_json.get('content')
        self.assertEqual(email.content, self.email1_json.get('content'))

    def test_email_delete(self):
        """Test deleting a EMail model"""
        email = EMail(**self.email_in_test_json)
        email.sender = ObjectId(self.email1_json['sender']['$oid'])
        self.email_in_test_json['sender'] = {'$oid': self.email1_json['sender']['$oid']}
        email.save()
        email_id = str(email.id)
        self.email_in_test_json['_id'] = {'$oid': email_id}
        email_find = EMail.objects.no_dereference().get(id=email_id)
        self.assertDictEqual(self.email_in_test_json, json.loads(email.to_json()))
        email.delete()
        self.assertRaises(DoesNotExist, lambda: EMail.objects.get(id=email_id))


if __name__ == '__main__':
    unittest.main()
