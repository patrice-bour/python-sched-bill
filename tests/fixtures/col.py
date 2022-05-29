import csv
from bson import ObjectId


def drop_collections(raw_db):
    """Drop each and every collection in the MongoDb database"""

    # Empty collections on testing DB
    for col in raw_db.list_collection_names():
        raw_db[col].drop()


def create_from_csv_file(raw_db, document_name, test_instance):
    """Generate documents from a csv file"""
    # Add some users as JSON objects and documents
    test_items_count = 0
    documents = []
    col = raw_db[f"{document_name}s"]
    with open(f"fixtures/csv/{document_name}s.csv") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            for k,v in row.items():
                v = str.strip(v)
                # Ugly trick to convert strings representing int to int
                if str.isnumeric(v):
                    try:
                        v = int(v)
                    except (ValueError, TypeError):
                        pass
                # Convert empty string to None
                elif len(v) == 0 or str.isspace(v):
                    v = None
                # Convert boolean string values
                elif v == 'False':
                    v = False
                elif v == 'True':
                    v = True

                row[k] = v
            test_items_count = test_items_count + 1
            setattr(test_instance, f"{document_name}{test_items_count}_json", row)
            documents.append(row)
            # Insert the document corresponding to the JSON object in the collection
            ins_res = col.insert_one(row)
            # Update JSON objects corresponding with documents by adding ObjectId values
            json_row = getattr(test_instance, f"{document_name}{test_items_count}_json")
            json_row['_id'] = {'$oid': str(ins_res.inserted_id)}
    # This JSON object corresponding to the last csv row will be used to test document creation later on
    not_yet_in_col_row = getattr(test_instance, f"{document_name}{test_items_count}_json")
    id404 = not_yet_in_col_row.pop('_id')
    # Remove the corresponding entry from the collection
    result = col.delete_one({"_id": ObjectId(id404.get('$oid'))})
    test_instance.assertEqual(result.deleted_count, 1)
    setattr(test_instance, 'id_404', id404['$oid'])  # Let's store the henceforth unrelated id
    # Rename the remaining attribute
    delattr(test_instance, f"{document_name}{test_items_count}_json")
    setattr(test_instance, f"{document_name}_in_test_json", not_yet_in_col_row)
    documents.pop()  # Also remove the ntry from the documents list

    return documents
