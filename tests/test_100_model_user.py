import unittest
from schedbill import create_app, config, db
from schedbill.models import User
from mongoengine.errors import DoesNotExist, NotUniqueError, ValidationError
from fixtures.col import drop_collections
from fixtures.users import create_users
import mongoengine
import json


class UserModelTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.conn = db.connect_db(config.TestingConfiguration)
        cls.raw_db = mongoengine.connection.get_db()
        # Empty collections on testing DB
        for col in cls.raw_db.list_collection_names():
            cls.raw_db[col].drop()

    def setUp(self) -> None:
        drop_collections(UserModelTestCase.raw_db)
        create_users(self, UserModelTestCase.raw_db)

    def test_user_finding(self):
        """Test retrieving a user into a User model"""
        user = User.objects.get(id=self.user1_json['_id']['$oid'])
        self.assertDictEqual(self.user1_json, json.loads(user.to_json()))

    def test_user_save(self):
        """Test saving a User model"""
        # Can save a valid user
        user = User(**self.user_in_test_json)
        user.save()
        user_find = User.objects.get(id=str(user.id))
        self.user_in_test_json['_id'] = { '$oid': str(user.id)}
        self.assertDictEqual(self.user_in_test_json, json.loads(user_find.to_json()))
        # attempt to create another user with the same email will raise an exception
        user_raising = User.objects.get(id=self.user1_json['_id']['$oid'])
        user_raising.emailAddress = user.emailAddress
        self.assertRaises(NotUniqueError, lambda: user_raising.save())
        # attempt to create another user without an email address will raise an exception
        delattr(user_raising, 'emailAddress')
        self.assertRaises(ValidationError, lambda: user_raising.save())
        # attempt to create another user with an invalid email address will raise an exception
        setattr(user_raising, 'emailAddress', 'foo.xyz.com')
        self.assertRaises(ValidationError, lambda: user_raising.save())

    def test_user_update(self):
        """Test updating a User model"""
        user = User(**self.user_in_test_json)
        user.save()
        user_find = User.objects.get(id=str(user.id))
        self.user_in_test_json['_id'] = { '$oid': str(user.id)}
        self.assertDictEqual(self.user_in_test_json, json.loads(user_find.to_json()))
        self.assertNotEqual(user.firstName, self.user1_json.get('firstName'))
        user.firstName = self.user1_json.get('firstName')
        self.assertEqual(user.firstName, self.user1_json.get('firstName'))
        self.assertNotEqual(user.lastName, self.user1_json.get('lastName'))
        user.lastName = self.user1_json.get('lastName')
        self.assertEqual(user.lastName, self.user1_json.get('lastName'))

    def test_user_delete(self):
        """Test deleting a User model"""
        user = User(**self.user_in_test_json)
        user.save()
        user_id = str(user.id)
        self.user_in_test_json['_id'] = {'$oid': user_id}
        user_find = User.objects.get(id=user_id)
        self.assertDictEqual(self.user_in_test_json, json.loads(user.to_json()))
        user.delete()
        self.assertRaises(DoesNotExist, lambda: User.objects.get(id=user_id))


if __name__ == '__main__':
    unittest.main()
