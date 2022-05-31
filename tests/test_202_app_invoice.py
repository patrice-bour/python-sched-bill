import flask_unittest
from schedbill import create_app, config, db
from flask.testing import FlaskClient
from fixtures.col import drop_collections
from fixtures.invoices import create_invoices
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
        create_invoices(self, self.raw_db)

    def tearDown(self, app: Flask, client: FlaskClient) -> None:
        pass

    def test_read_invoice(self, app: Flask, client: FlaskClient) -> None:
        # retrieve an invoice by id
        resp = client.get(f"/invoices/{self.invoice1_json['_id']['$oid']}")
        self.assertStatus(resp, 200)
        self.assertEqual(self.invoice1_json, resp.json["data"])
        # attempt to retrieve an invoice with a not existent id
        resp = client.get(f"/invoices/{self.id_404}")
        self.assertStatus(resp, 404)
        assert "Invoice matching query does not exist" in resp.json['error']
        # attempt to retrieve an invoice with an invalid id
        resp = client.get(f"/invoices/123")
        self.assertStatus(resp, 400)
        assert "Invalid ObjectId" in resp.json['error']
        
    def test_create_invoice(self, app: Flask, client: FlaskClient) -> None:
        # create an invoice
        resp = client.post('/invoices', json=self.invoice_in_test_json)
        self.assertStatus(resp, 201)
        user = resp.json["data"]
        self.assertIsNotNone(client.get('_id', None))
        # attempt to create another invoice without valid JSON in payload
        resp = client.post('/invoices')
        self.assertStatus(resp, 400)
        # attempt to create another user without a reference should return 500
        self.invoice_in_test_json.pop('reference')
        resp = client.post('/users', json=self.invoice_in_test_json)
        self.assertStatus(resp, 500)
        # attempt to create another user without a unique reference should return 500
        self.invoice_in_test_json['reference'] = self.invoice1_json.get('reference')
        resp = client.post('/users', json=self.invoice_in_test_json)
        self.assertStatus(resp, 500)

    def test_update_invoice(self, app: Flask, client: FlaskClient) -> None:
        # update an existing invoice
        #
        resp = client.put(
            f"/invoices/{str(self.invoice1_json['_id']['$oid'])}",
            json=self.invoice_in_test_json
        )
        self.assertStatus(resp, 200)
        # attempt to update a not existing invoice
        resp = client.put(
            f"/invoices/{self.id_404}",
            json=self.invoice_in_test_json
        )
        self.assertStatus(resp, 404)

    def test_delete_invoice(self, app: Flask, client: FlaskClient) -> None:
        # delete an existing invoice
        resp = client.delete(f"/invoices/{str(self.invoice1_json['_id']['$oid'])}")
        self.assertStatus(resp, 204)
        # attempt to delete a not existing invoice
        resp = client.delete(f"/invoices/{str(self.invoice1_json['_id']['$oid'])}")
        self.assertStatus(resp, 404)
        # attempt to delete a invoice using an invalid ObjectId
        resp = client.delete(f"/invoices/123")
        self.assertStatus(resp, 400)
        assert "Invalid ObjectId" in resp.json['error']