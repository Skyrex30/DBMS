import json

CATALOG_FILE = "catalog.json"

catalog = {"databases": {}}

def load_catalog():
    global catalog
    try:
        with open(CATALOG_FILE, "r") as f:
            catalog = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        catalog = {"databases": {}}

def save_catalog():
    with open("catalog.json", "w") as f:
        json.dump(catalog, f, indent=4)
