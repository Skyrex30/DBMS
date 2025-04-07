from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["MiniABKR"]

def insert_row(table_name, primary_key, attributes):
    value_str = "#".join(attributes)
    document = {"_id": primary_key, "value": value_str}
    try:
        db[table_name].insert_one(document)
        return {"message": "Row inserted successfully"}
    except Exception as e:
        return {"error": str(e)}

def delete_row(table_name, primary_key):
    result = db[table_name].delete_one({"_id": primary_key})
    if result.deleted_count == 0:
        return {"error": "Row not found"}
    return {"message": "Row deleted successfully"}
