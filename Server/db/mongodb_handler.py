from flask import jsonify
from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT

client = MongoClient("mongodb://localhost:27017/")
db = client["MiniABKR"]

def insert_row(database_name, table_name, primary_key, attributes):
    """
    Insert a row into a table in MongoDB.
    
    The ID is the name of the table.
    
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
    
    
    validation = validate_insert(database_name, table_name, attributes)
    if "error" in validation:
        return validation

    result = collection.update_one(
        {"_id": table_name},
        {"$set": {f"rows.{primary_key_str}": attributes}} 
    )
    
    for key, value in attributes.items():
        update_index(database_name, table_name, key, primary_key, value, operation="insert")

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
    
    row_to_delete = table_doc["rows"][primary_key_str]
    
    result = collection.update_one(
        {"_id": table_name},  # Filter by table name
        {"$unset": {f"rows.{primary_key_str}": ""}}  # Unset the row with the given primary key
    )
    
    for key, value in row_to_delete.items():
        update_index(database_name, table_name, key, primary_key, value, operation="delete")


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

def create_index_mongo(database_name, table_name, index_type, index_key):
    """
    Create an index document for a table based on a specified key.
    
    Args:
        database_name: The database (MongoDB collection) name.
        table_name: The table (MongoDB document) name.
        index_type: 'unique' or 'non-unique'
        index_key: The attribute/column to index.
        
    Returns:
        A success or error message.
    """
    collection = db[database_name]
    table_doc = collection.find_one({"_id": table_name})

    if not table_doc:
        return {"error": f"Table {table_name} does not exist."}

    rows = table_doc.get("rows", {})

    index_doc_id = f"{table_name}_index_{index_key}"

    # Check if its already existing
    if collection.find_one({"_id": index_doc_id}):
        return {"error": f"Index {index_doc_id} already exists."}

    index_data = {}

    for primary_key, attributes in rows.items():
        value = attributes.get(index_key)

        if value is None:
            continue

        if index_type == "unique":
            if str(value) in index_data:
                return {"error": f"Duplicate value '{value}' found for unique index '{index_key}'."}
            index_data[str(value)] = primary_key
        elif index_type == "non-unique":
            if str(value) not in index_data:
                index_data[str(value)] = []
            index_data[str(value)].append(primary_key)
        else:
            return {"error": "Invalid index type. Use 'unique' or 'non-unique'."}

    collection.insert_one({
        "_id": index_doc_id,
        "index_key": index_key,
        "index_type": index_type,
        "entries": index_data
    })

    return {"message": f"Index {index_doc_id} created successfully."}

def update_index(database_name, table_name, index_key, primary_key, attribute_value, operation):
    """
    Update an index document when a row is inserted or deleted.

    Args:
        database_name: The database (MongoDB collection) name.
        table_name: The table (MongoDB document) name.
        index_key: The attribute/column on which the index was built.
        primary_key: The primary key of the row being inserted or deleted.
        attribute_value: The value of the attribute for the index.
        operation: 'insert' or 'delete'
    """
    collection = db[database_name]
    index_doc_id = f"{table_name}_index_{index_key}"

    index_doc = collection.find_one({"_id": index_doc_id})

    if not index_doc:
        return {"error": f"Index {index_doc_id} does not exist."}

    index_type = index_doc["index_type"]
    entries = index_doc.get("entries", {})

    value_str = str(attribute_value)
    primary_key_str = str(primary_key)

    if operation == "insert":
        if index_type == "unique":
            if value_str in entries:
                return {"error": f"Duplicate value '{attribute_value}' for unique index '{index_key}'."}
            entries[value_str] = primary_key_str
        elif index_type == "non-unique":
            if value_str not in entries:
                entries[value_str] = []
            entries[value_str].append(primary_key_str)

    elif operation == "delete":
        if index_type == "unique":
            if entries.get(value_str) == primary_key_str:
                del entries[value_str]
        elif index_type == "non-unique":
            if value_str in entries:
                if primary_key_str in entries[value_str]:
                    entries[value_str].remove(primary_key_str)
                    if not entries[value_str]:  # If the list is empty we delete it
                        del entries[value_str]
    else:
        return {"error": "Invalid operation. Use 'insert' or 'delete'."}

    collection.update_one(
        {"_id": index_doc_id},
        {"$set": {"entries": entries}}
    )

    return {"message": f"Index {index_doc_id} updated successfully."}

def validate_insert(database_name, table_name, attributes):
    """
    Validate before inserting a new row: check unique and foreign keys.

    Args:
        database_name: Database (MongoDB collection) name
        table_name: Table (MongoDB document) name
        attributes: Dict of attribute values to be inserted

    Returns:
        {"ok": True} if valid
        {"error": "..."} if invalid
    """
    collection = db[database_name]
    table_doc = collection.find_one({"_id": table_name})

    if not table_doc:
        return {"error": f"Table {table_name} does not exist."}

    unique_keys = table_doc.get("unique_keys", [])
    #foreign_keys = table_doc.get("foreign_keys", {})

    # Unique key check
    for unique_key in unique_keys:
        index_doc_id = f"{table_name}_index_{unique_key}"
        index_doc = collection.find_one({"_id": index_doc_id})
        
        if not index_doc:
            continue  # Skip if index doesn't exist
        
        entries = index_doc.get("entries", {})
        value_str = str(attributes.get(unique_key))

        if value_str in entries:
            return {"error": f"Unique key constraint violation on '{unique_key}' with value '{value_str}'."}

    # Foreign key check

    return {"ok": True}

def validate_delete(database_name, table_name, primary_key):
    """
    Validate before deleting a row: check foreign key references.

    Args:
        database_name: Database (MongoDB collection) name
        table_name: Table (MongoDB document) name
        primary_key: Primary key of the row to delete

    Returns:
        {"ok": True} if deletion allowed
        {"error": "..."} if not allowed
    """
    collection = db[database_name]
    all_tables = collection.find({})

    return {"ok": True}
