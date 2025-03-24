from flask import Flask, request, jsonify
import json
import os

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

    return jsonify({"message": f"Database {db_name} created successfully"})

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
    
    return jsonify({"message": f"Database {db_name} dropped successfully"})

@app.route("/create_table", methods=["POST"])
def create_table():
    
    global selected_db
    if not selected_db:
        return jsonify({"error": "No database selected. Use USE db_name; GO first."}), 400
    
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
        #"indexes": indexes
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
    return jsonify({"message": f"Table {table_name} dropped successfully"})

    
if __name__ == "__main__":
    app.run(debug=True)