#import catalog
import json

CATALOG_FILE = "catalog.json"


def load_catalog():
    #Loads the catalog.json file
    global catalog
    try:
        with open(CATALOG_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"databases": {}}

def save_catalog():
    #Saves the catalog.json file
    with open("catalog.json", "w") as f:
        json.dump(catalog, f, indent=4)

selected_db = None

def use_database(db_name):
    global selected_db
    if db_name not in catalog.catalog["databases"]:
        return False, "Database does not exist"
    selected_db = db_name
    return True, f"Using database {db_name}"

def create_database(db_name):
    if db_name in catalog.catalog["databases"]:
        return False, "Database already exists"
    
    catalog.catalog["databases"][db_name] = {"tables": {}}
    catalog.save_catalog()
    return True, f"Database {db_name} created successfully"

def drop_database(db_name):
    global selected_db
    if db_name not in catalog.catalog["databases"]:
        return False, "Database does not exist"
    
    del catalog.catalog["databases"][db_name]
    if selected_db == db_name:
        selected_db = None
    
    catalog.save_catalog()
    return True, f"Database {db_name} dropped successfully"
