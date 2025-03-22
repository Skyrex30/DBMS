from flask import Flask, request, jsonify
import json

app = Flask(__name__)

with open("catalog.json", "r") as f:
   catalog = json.load(f)
    
@app.route("/create_database", methods=["POST"])
def create_database():
    data = request.json
    db_name = data["db_name"]

    if db_name in catalog:
        return jsonify({"error": "Database already exists"}), 400

    catalog[db_name] = {}
    with open("catalog.json", "w") as f:
        json.dump(catalog, f, indent=4)

    return jsonify({"message": f"Database {db_name} created successfully"})

@app.route("/drop_database", methods=["POST"])
def drop_database():
    data = request.json
    db_name = data["db_name"]
    
    if db_name not in catalog:
        return jsonify({"error": "Database does not exist"}), 400
    
    return jsonify({"message": f"Database {db_name} dropped successfully"})


if __name__ == "__main__":
    app.run(debug=True)