from flask import Flask, request, jsonify
import json
import os
from db.mongodb_handler import *

app = Flask(__name__)

CATALOG_FILE = "catalog.json"

if not os.path.exists(CATALOG_FILE) or os.stat(CATALOG_FILE).st_size == 0:
    catalog = {"databases": {}}
    with open(CATALOG_FILE, "w") as f:
        json.dump(catalog, f, indent=4)
else:
    with open(CATALOG_FILE, "r") as f:
        catalog = json.load(f)
        
        
selected_db = None

def save_catalog():
    with open(CATALOG_FILE, "w") as f:
        json.dump(catalog, f, indent=4)       
        
@app.route("/use_database", methods=["POST"])
def use_database():
    global selected_db
    data = request.json
    db_name = data.get("db_name")

    if db_name not in catalog["databases"]:
        return jsonify({"error": "Database does not exist"}), 400
    
    selected_db = db_name
    return jsonify({"message": f"Using database {db_name}"})
    
@app.route("/create_database", methods=["POST"])
def create_database():
    data = request.json
    db_name = data["db_name"]

    if db_name in catalog["databases"]:
        return jsonify({"error": "Database already exists"}), 400

    catalog["databases"][db_name] = {"tables": {}}
    save_catalog()
    
    create_collection(db_name) #create in mongodb

    return jsonify({"message": f"Database {db_name} created successfully"})


@app.route("/list_databases", methods=["GET"])
def list_databases():
    return jsonify({"databases": list(catalog["databases"].keys())})

@app.route("/drop_database", methods=["POST"])
def drop_database():
    data = request.json
    db_name = data["db_name"]
    
    if db_name not in catalog["databases"]:
        return jsonify({"error": "Database does not exist"}), 400
    
    del catalog["databases"][db_name]
    # if selected_db == db_name:
    #    selected_db = None
        
    save_catalog()
    drop_collection(db_name) 
    
    return jsonify({"message": f"Database {db_name} dropped successfully"})

@app.route("/create_table", methods=["POST"])
def create_table():
    
    global selected_db
    if not selected_db:
        return jsonify({"error": "No database selected. Use USE db_name first."}), 400
    
    data = request.json
    db_name = data["db_name"]
    table_name = data["table_name"]
    file_name = data.get("file_name", f"{table_name}.bin")
    row_length = data.get("row_length", 0)
    structure = data["structure"]
    primary_key = data.get("primary_key", [])
    foreign_keys = data.get("foreign_keys", {})
    unique_keys = data.get("unique_keys", [])
    # indexes = data.get("indexes", {})
    
    if db_name not in catalog["databases"]:
        return jsonify({"error": "Database does not exist"}), 400

    if table_name in catalog["databases"][db_name]["tables"]:
        return jsonify({"error": "Table already exists"}), 400 
    
    catalog["databases"][db_name]["tables"][table_name] = {
        "file": file_name,
        "row_length": row_length,
        "structure": structure,
        "primary_key": primary_key,
        "foreign_keys": foreign_keys,
        "unique_keys": unique_keys,
    }
    save_catalog()
    
    return jsonify({"message": f"Table {table_name} created successfully"})
    
@app.route("/drop_table", methods=["POST"])
def drop_table():
    data = request.json
    table_name = data["table_name"]
    
    global selected_db
    
    if selected_db not in catalog["databases"]:
        return jsonify({"error": "Database does not exist"}), 400
    
    if table_name not in catalog["databases"][selected_db]["tables"]:
        return jsonify({"error": f"Table does not exist in database '{selected_db}'."}), 400
    
    del catalog["databases"][selected_db]["tables"][table_name]
    
    save_catalog()
    drop_document(selected_db, table_name) #delete from mongodb
    
    return jsonify({"message": f"Table {table_name} dropped successfully"})

@app.route("/list_tables", methods=["GET"])
def list_tables():
    db_name = request.args.get("db_name")
    if db_name not in catalog["databases"]:
        return jsonify({"error": "Database does not exist"}), 400
    return jsonify({"tables": list(catalog["databases"][db_name]["tables"].keys())})

#Structure for insert (for the Client)
@app.route("/table_structure", methods=["GET"])
def table_structure():
    db_name = request.args.get("db_name")
    table_name = request.args.get("table_name")
    
    if db_name not in catalog["databases"]:
        return jsonify({"status": "error", "error": "Database does not exist"}), 400
        
    if table_name not in catalog["databases"][db_name]["tables"]:
        return jsonify({"status": "error", "error": "Table does not exist"}), 400
        
    table_info = catalog["databases"][db_name]["tables"][table_name]
    return jsonify({
        "status": "success",
        "structure": table_info["structure"],
        "primary_key": table_info.get("primary_key", [])
    })


@app.route("/insert", methods=["POST"])
def insert():
    data = request.json
    print(data)
    result = insert_row(data["db_name"], data["table"], data["primary_key"], data["attributes"])
    return result

@app.route("/delete", methods=["POST"])
def delete():
    data = request.json
    result = delete_row(data["db_name"], data["table"], data["primary_key"])
    return result

@app.route("/create_index", methods=["POST"])
def create_index():
    data = request.json
    db_name = data["db_name"]
    table_name = data["table_name"]
    index_fields = data["index_fields"]  # Expected to be a list of tuples, like [("name", "ascending"), ("age", "descending")]
    index_type = data.get("index_type", "ascending")  # Default is ascending
    unique = data.get("unique", False)
    sparse = data.get("sparse", False)
    
    result = create_index_mongo(db_name, table_name, index_fields, index_type, unique, sparse)
    return result

if __name__ == "__main__":
    app.run(debug=True)