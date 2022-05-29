from fixtures.col import create_from_csv_file


def create_users(test_instance, raw_db):
    """Create users JSON objects, documents and various references to use in unit tests"""
    create_from_csv_file(raw_db, "user", test_instance)
