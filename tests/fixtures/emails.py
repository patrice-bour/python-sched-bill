from fixtures.col import create_from_csv_file
from random import randint
from bson import ObjectId


def create_emails(test_instance, raw_db):
    """Create emails JSON objects, documents and various references to use in unit tests"""
    # Use fixtures from fixtures.users
    # create_users(test_instance, raw_db)
    users_list = create_from_csv_file(raw_db, "user", test_instance)
    # Add some emails as JSON objects and documents
    emails_list = create_from_csv_file(raw_db, 'email', test_instance)
    # Reference users from emails
    users_count = len(users_list)
    email_rank = 0  # Index for retrieving the email attribute of test_instance (email{email_rank}_csv)
    # Update emails documents and JSON objects with the sender id
    for email_csv in emails_list:
        email_rank = email_rank + 1
        random_id = randint(0, users_count-1)
        random_user = users_list[random_id]
        random_user_id = random_user["_id"]['$oid']
        raw_db.emails.find_one_and_update(
            {"_id": ObjectId(email_csv["_id"]['$oid'])},
            {
             '$set': {"sender": random_user_id}
            }
        )
        email_csv_attr = getattr(test_instance, f"email{email_rank}_json")
        email_csv_attr['sender'] = {'$oid': random_user_id}
