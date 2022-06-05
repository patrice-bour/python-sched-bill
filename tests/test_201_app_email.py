import flask_unittest
from schedbill import create_app, config, db, scheduler
from flask.testing import FlaskClient
from fixtures.col import drop_collections
from fixtures.emails import create_emails
from flask import Flask, g
import mongoengine


class TestFlaskApp(flask_unittest.AppClientTestCase):
    def create_app(self):
        app = create_app(config.TestingConfiguration)
        with app.app_context():
            self.db = db.get_db()
            self.raw_db = mongoengine.connection.get_db()
            self.scheduler = scheduler.get_scheduler()
            self.scheduler.start()
            yield app

    def setUp(self, app: Flask, client: FlaskClient) -> None:
        drop_collections(self.raw_db)
        create_emails(self, self.raw_db)

    def tearDown(self, app: Flask, client: FlaskClient) -> None:
        pass

    def test_read_email(self, app: Flask, client: FlaskClient) -> None:
        # retrieve an email by id
        resp = client.get(f"/emails/{self.email1_json['_id']['$oid']}")
        self.assertStatus(resp, 200)
        self.assertEqual(self.email1_json, resp.json["data"])
        # attempt to retrieve an email with a not existent id
        resp = client.get(f"/emails/{self.id_404}")
        self.assertStatus(resp, 404)
        assert "EMail matching query does not exist" in resp.json['error']
        # attempt to retrieve an email with an invalid id
        resp = client.get(f"/emails/123")
        self.assertStatus(resp, 400)
        assert "Invalid ObjectId" in resp.json['error']

    def test_create_email(self, app: Flask, client: FlaskClient) -> None:
        # create an email
        resp = client.post('/emails', json=self.email_in_test_json)
        self.assertStatus(resp, 201)
        user = resp.json["data"]
        self.assertIsNotNone(client.get('_id', None))
        # attempt to create another email without valid JSON in payload
        resp = client.post('/emails')
        self.assertStatus(resp, 400)
        # attempt to create another user without a valid email address as recipient should return 500
        resp = client.post('/users', json={"recipient": "foo.bar.baz", "firstName": "Foo", "lastName": "Bar",
                                           "content": "foobar"})
        self.assertStatus(resp, 500)
        # attempt to create another user without a content should return 500
        resp = client.post('/users', json={"recipient": "foo.bar@baz", "firstName": "Foo", "lastName": "Bar"})
        self.assertStatus(resp, 500)

    def test_update_email(self, app: Flask, client: FlaskClient) -> None:
        # update an existing email
        #
        resp = client.put(
            f"/emails/{str(self.email1_json['_id']['$oid'])}",
            json=self.email_in_test_json
        )
        self.assertStatus(resp, 200)
        # attempt to update a not existing email
        resp = client.put(
            f"/emails/{self.id_404}",
            json=self.email_in_test_json
        )
        self.assertStatus(resp, 404)

    def test_delete_email(self, app: Flask, client: FlaskClient) -> None:
        # delete an existing email
        resp = client.delete(f"/emails/{str(self.email1_json['_id']['$oid'])}")
        self.assertStatus(resp, 204)
        # attempt to delete a not existing email
        resp = client.delete(f"/emails/{str(self.email1_json['_id']['$oid'])}")
        self.assertStatus(resp, 404)
        # attempt to delete a email using an invalid ObjectId
        resp = client.delete(f"/emails/123")
        self.assertStatus(resp, 400)
        assert "Invalid ObjectId" in resp.json['error']