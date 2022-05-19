import unittest
import json
from models import Base, User


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.uuid = '123'

    def test_construction(self):
        base = Base()
        self.assertIsNone(base.uuid, 'uuid attribute is None when not specified at construction time')

        base = Base(uuid=self.uuid)
        self.assertEqual(base.uuid, self.uuid, 'uuid attribute can be specified at construction time')

    def test_uuid(self):
        u1 = Base.get_uuid()
        self.assertIsNotNone(u1, 'statically generated uuid is not None')
        self.assertIsInstance(u1, str, 'uuid is a string')
        u2 = Base.get_uuid()
        self.assertNotEqual(u1, u2, 'statically generated uuids are unique')


class UserTestCase(unittest.TestCase):
    def setUp(self):
        self.email = 'foo@bar.baz'
        self.uuid = '123'

    def test_construction(self):
        user = User()
        self.assertIsNone(user.email, 'email attribute is None when not specified at construction time')
        self.assertIsNone(user.uuid, 'uuid attribute is None when not specified at construction time')

        user = User(uuid=self.uuid, email=self.email)
        self.assertEqual(user.email, self.email, 'email attribute can be specified at construction time')
        self.assertEqual(user.uuid, self.uuid, 'uuid attribute can be specified at construction time')

    def test_obj_to_string(self):
        user = User(uuid=self.uuid, email=self.email)
        self.assertEqual(user.to_string(), "foo@bar.baz (123)",
                         'to_string() behaves as expected with 2 attributes set')

        user = User()
        self.assertEqual(user.to_string(), "None (None)",
                         'to_string() behaves as expected with 2 attributes set')

    def test_obj_to_json(self):
        user = User(uuid=self.uuid, email=self.email)
        self.assertDictEqual(
            json.loads(user.to_json()),
            {'email': self.email, 'uuid': self.uuid},
            'to_json() behaves correctly with 2 attributes set'
        )

        user = User()
        self.assertDictEqual(
            json.loads(user.to_json()),
            {'email': None, 'uuid': None},
            'to_json() behaves correctly without any attribute set'
        )


if __name__ == '__main__':
    unittest.main()
