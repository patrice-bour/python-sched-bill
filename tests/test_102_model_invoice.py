import unittest
from schedbill import create_app, config, db
from schedbill.models import Invoice
from mongoengine.errors import DoesNotExist, NotUniqueError, ValidationError
from fixtures.col import drop_collections
from fixtures.invoices import create_invoices
import mongoengine
import json
from bson import ObjectId


class InvoiceModelTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.conn = db.connect_db(config.TestingConfiguration)
        cls.raw_db = mongoengine.connection.get_db()
        # Empty collections on testing DB
        for col in cls.raw_db.list_collection_names():
            cls.raw_db[col].drop()

    def setUp(self) -> None:
        drop_collections(InvoiceModelTestCase.raw_db)
        create_invoices(self, InvoiceModelTestCase.raw_db)

    def test_invoice_finding(self):
        """Test retrieving a invoice into a Invoice model"""
        invoice = Invoice.objects.get(id=self.invoice1_json['_id']['$oid'])
        self.assertDictEqual(self.invoice1_json, json.loads(invoice.to_json()))

    def test_invoice_save(self):
        """Test saving a Invoice model"""
        # Can save a valid invoice
        self.invoice_in_test_json.pop('sender')
        self.invoice_in_test_json.pop('recipient')
        invoice = Invoice(**self.invoice_in_test_json)
        invoice.save()
        invoice_find = Invoice.objects.no_dereference().get(id=str(invoice.id))
        self.invoice_in_test_json['_id'] = { '$oid': str(invoice.id)}
        self.assertDictEqual(self.invoice_in_test_json, json.loads(invoice_find.to_json()))
        # attempt to create another invoice without a reference will raise an exception
        invoice_raising = Invoice.objects.get(id=self.invoice1_json['_id']['$oid'])
        delattr(invoice_raising, 'reference')
        self.assertRaises(ValidationError, lambda: invoice_raising.save())
        # attempt to create another invoice without a unique reference will raise an exception
        invoice_raising = Invoice.objects.get(id=self.invoice2_json['_id']['$oid'])
        setattr(invoice_raising, 'reference', invoice_find.reference)
        self.assertRaises(NotUniqueError, lambda: invoice_raising.save())

    def test_invoice_update(self):
        """Test updating a Invoice model"""
        invoice = Invoice(**self.invoice_in_test_json)
        invoice.sender = ObjectId(self.invoice1_json['sender']['$oid'])
        invoice.recipient = ObjectId(self.invoice1_json['recipient']['$oid'])
        self.invoice_in_test_json['sender'] = {'$oid': self.invoice1_json['sender']['$oid']}
        self.invoice_in_test_json['recipient'] = {'$oid': self.invoice1_json['recipient']['$oid']}
        invoice.save()
        invoice_find = Invoice.objects.no_dereference().get(id=str(invoice.id))
        self.invoice_in_test_json['_id'] = { '$oid': str(invoice.id)}
        self.assertDictEqual(self.invoice_in_test_json, json.loads(invoice_find.to_json()))
        notify_initial_value = invoice.notify
        self.assertNotEqual(invoice.notify, not notify_initial_value)
        invoice.notify = not notify_initial_value
        self.assertEqual(invoice.notify, not notify_initial_value)

    def test_invoice_delete(self):
        """Test deleting a Invoice model"""
        invoice = Invoice(**self.invoice_in_test_json)
        invoice.sender = ObjectId(self.invoice1_json['sender']['$oid'])
        invoice.recipient = ObjectId(self.invoice1_json['recipient']['$oid'])
        self.invoice_in_test_json['sender'] = {'$oid': self.invoice1_json['sender']['$oid']}
        self.invoice_in_test_json['recipient'] = {'$oid': self.invoice1_json['recipient']['$oid']}
        invoice.save()
        invoice_id = str(invoice.id)
        self.invoice_in_test_json['_id'] = {'$oid': invoice_id}
        invoice_find = Invoice.objects.no_dereference().get(id=invoice_id)
        self.assertDictEqual(self.invoice_in_test_json, json.loads(invoice.to_json()))
        invoice.delete()
        self.assertRaises(DoesNotExist, lambda: Invoice.objects.get(id=invoice_id))


if __name__ == '__main__':
    unittest.main()
