from fixtures.col import create_from_csv_file
from random import randint
from bson import ObjectId


def create_invoices(test_instance, raw_db):
    """Create invoices JSON objects, documents and various references to use in unit tests"""
    # Use fixtures from fixtures.users
    # create_users(test_instance, raw_db)
    users_list = create_from_csv_file(raw_db, "user", test_instance)
    # Add some invoices as JSON objects and documents
    invoices_list = create_from_csv_file(raw_db, 'invoice', test_instance)
    # Reference users from invoices
    users_count = len(users_list)
    invoice_rank = 0  # Index for retrieving the invoice attribute of test_instance (invoice{invoice_rank}_csv)
    # Update invoices documents and JSON objects with the sender id
    for invoice_csv in invoices_list:
        invoice_rank = invoice_rank + 1
        random_id = randint(0, users_count-1)
        random_user = users_list[random_id]
        random_user_id = random_user["_id"]['$oid']
        raw_db.invoices.find_one_and_update(
            {"_id": ObjectId(invoice_csv["_id"]['$oid'])},
            {
             '$set': {"sender": random_user_id}
            }
        )
        invoice_csv_attr = getattr(test_instance, f"invoice{invoice_rank}_json")
        invoice_csv_attr['sender'] = {'$oid': random_user_id}