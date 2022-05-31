import flask_unittest
from fixtures.users import create_users
from fixtures.col import drop_collections
from schedbill import create_app, config, db
from flask.testing import FlaskClient
from flask import Flask
import mongoengine


class TestFlaskApp(flask_unittest.AppClientTestCase):
    def create_app(self):
        app = create_app(config.TestingConfiguration)
        with app.app_context():
            self.db = db.get_db()
            self.raw_db = mongoengine.connection.get_db()
            yield app

    def setUp(self, app: Flask, client: FlaskClient) -> None:
        drop_collections(self.raw_db)
        create_users(self, self.raw_db)

    def tearDown(self, app: Flask, client: FlaskClient) -> None:
        pass

    def test_home(self, app: Flask, client: FlaskClient) -> None:
        self.assertStatus(client.get('/'), 200)

    def test_read_user(self, app: Flask, client: FlaskClient) -> None:
        # retrieve a user by id
        resp = client.get(f"/users/{self.user1_json['_id']['$oid']}")
        self.assertStatus(resp, 200)
        self.assertEqual(self.user1_json, resp.json["data"])
        # attempt to retrieve a user with a not existent id
        resp = client.get(f"/users/{self.id_404}")
        self.assertStatus(resp, 404)
        assert "User matching query does not exist" in resp.json['error']
        # attempt to retrieve a user with an invalid id
        resp = client.get(f"/users/123")
        self.assertStatus(resp, 400)
        assert "Invalid ObjectId" in resp.json['error']
        # retrieve a user by email
        resp = client.get(f"/users/emailAddress/{self.user1_json['emailAddress']}")
        self.assertStatus(resp, 200)
        self.assertEqual(self.user1_json, resp.json["data"])
        # attempt to retrieve a user with a not existent email
        resp = client.get(f"/users/emailAddress/ido@notexi.st")
        self.assertStatus(resp, 404)
        assert "User matching query does not exist" in resp.json['error']

    def test_create_user(self, app: Flask, client: FlaskClient) -> None:
        # create a user
        resp = client.post('/users', json=self.user_in_test_json)
        self.assertStatus(resp, 201)
        user = resp.json["data"]
        self.assertIsNotNone(user.get('_id', None))
        # attempt to create another user with the same email address should return 500
        resp = client.post('/users', json=self.user_in_test_json)
        self.assertStatus(resp, 500)
        # attempt to create another user without an email address should return 500
        resp = client.post('/users', json={"firstName": "Foo", "lastName": "Bar"})
        self.assertStatus(resp, 500)
        # attempt to create another user without a valid email address should return 500
        resp = client.post('/users', json={"emailAddress": "foo.bar.baz", "firstName": "Foo", "lastName": "Bar"})
        self.assertStatus(resp, 500)
        # attempt to create another user without valid JSON in payload
        resp = client.post('/users')
        self.assertStatus(resp, 400)

    def test_update_user(self, app: Flask, client: FlaskClient) -> None:
        # update an existing user
        resp = client.put(
            f"/users/{str(self.user1_json['_id']['$oid'])}",
            json=self.user_in_test_json
        )
        self.assertStatus(resp, 200)
        # attempt to update a not existing user
        resp = client.put(
            f"/users/{self.id_404}",
            json=self.user_in_test_json
        )
        self.assertStatus(resp, 404)
        # attempt to update an existing user with an invalid email
        resp = client.put(
            f"/users/{str(self.user1_json['_id']['$oid'])}",
            json={"emailAddress": "foo@@bar.baz"}
        )
        self.assertStatus(resp, 500)

    def test_delete_user(self, app: Flask, client: FlaskClient) -> None:
        # delete an existing user
        resp = client.delete(f"/users/{str(self.user1_json['_id']['$oid'])}")
        self.assertStatus(resp, 204)
        # attempt to delete a not existing user
        resp = client.delete(f"/users/{str(self.user1_json['_id']['$oid'])}")
        self.assertStatus(resp, 404)
        # attempt to delete a user using an invalid ObjectId
        resp = client.delete(f"/users/123")
        self.assertStatus(resp, 400)
        assert "Invalid ObjectId" in resp.json['error']
