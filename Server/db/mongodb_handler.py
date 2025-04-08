from flask import jsonify
from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT

client = MongoClient("mongodb://localhost:27017/")
db = client["MiniABKR"]

def insert_row(database_name, table_name, primary_key, attributes):
    """
    Insert a row into a table in MongoDB.
    
    Args:
        database_name: Name of the database
        table_name: Name of the table
        primary_key: Primary key of the row
        attributes: Dictionary of attributes for the row
    """
    collection = db[database_name]
    table_doc = collection.find_one({"_id": table_name})
    
    primary_key_str = str(primary_key)
    
    if not table_doc:
        collection.insert_one({
            "_id": table_name,
            "rows": {primary_key_str: attributes}
        })
        return {"message": f"Table {table_name} created and row inserted."}
    
    if primary_key_str in table_doc:
        return {"error": f"Primary key {primary_key} already exists."}

    result = collection.update_one(
        {"_id": table_name},
        {"$set": {f"rows.{primary_key_str}": attributes}} 
    )
    
    return jsonify({
            "status": "success",
            "message": "Row inserted successfully",
            "inserted_id": table_name,
            "table": table_name
    })

def delete_row(database_name, table_name, primary_key):
    collection = db[database_name]
    table_doc = collection.find_one({"_id": table_name})
    
    primary_key_str = str(primary_key)


    if not table_doc:
        return {"error": f"Table {table_name} does not exist."}

    if primary_key_str not in table_doc["rows"]:
        return {"error": f"Row with key {primary_key} not found."}

    result = collection.update_one(
        {"_id": table_name},  # Filter by table name
        {"$unset": {f"rows.{primary_key_str}": ""}}  # Unset the row with the given primary key
    )

    return jsonify({
            "status": "success",
            "message": "Row deleted successfully",
            "deleted_count": result.modified_count
        })

def create_collection(database_name):    
    if database_name in db.list_collection_names():
        return {"error": f"Database {database_name} already exists."}
    
    db.create_collection(database_name)
    return {"message": f"Database {database_name} created."}

#def create_document(database_name, table_name, table_metadata):
    collection = db[database_name]
    
    if collection.find_one({"_id": table_name}):
        return {"error": f"Table {table_name} already exists in database {database_name}."}

    result = collection.insert_one({
        "_id": table_name,
        "structure": table_metadata["structure"],
        "primary_key_meta": table_metadata["primary_key"],
        "unique_keys": table_metadata["unique_keys"],
        "foreign_keys": table_metadata["foreign_keys"],
        "rows": {}  # optionally pre-create a place for rows
    })

    return {
        "message": f"Table document created in MongoDB database {database_name}.",
        "document_id": str(result.inserted_id)  # We'll store the document ID in the 
    }

def drop_collection(database_name):
    if database_name in db.list_collection_names():
        db.drop_collection(database_name)
        return {"message": f"Database {database_name} dropped from MongoDB."}
    return {"error": "Database does not exist in MongoDB."}

def drop_document(database_name, table_name):
    collection = db[database_name]
    result = collection.delete_one({"_id": table_name})
    
    if result.deleted_count:
        return {"message": f"Table {table_name} dropped from database {database_name}."}
    return {"error": "Table not found in MongoDB."}

def create_index_mongo(database_name, table_name, index_fields, index_type="ascending", unique=False, sparse=False):
    """
    Creates an index in mongodb
    Args:
        database_name: Name of the database
        table_name: Name of the table
        index_fields: Expected to be a list of tuples, like [("name", "ascending"), ("age", "descending")]_
        index_type: Type of the index(asc, desc, 2dsphere, text) (Defaults to "ascending".
        unique (bool, optional)
        sparse (bool, optional)
    """
    
    collection = db[database_name][table_name]
    
    # Maps the index type to the corresponding MongoDB type
    index_type_mapping = {
        "ascending": ASCENDING,
        "descending": DESCENDING,
        "text": TEXT
    }
    
    # Convert field names and order to MongoDB index format
    mongo_index_fields = []
    for field, order in index_fields:
        mongo_index_fields.append((field, index_type_mapping.get(order, ASCENDING)))
        
     # Try to create the index
    try:
        index_options = {}
        
        if unique:
            index_options["unique"] = True
        if sparse:
            index_options["sparse"] = True

        index_name = collection.create_index(mongo_index_fields, **index_options)
        
        print(f"index created {index_name}")
        return {"message": f"Index '{index_name}' created successfully."}

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}