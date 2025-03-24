import requests
import json

SERVER_URL = "http://127.0.0.1:5000"

selected_db = None

def create_database(db_name):
    response = requests.post(f"{SERVER_URL}/create_database", json={"db_name": db_name})
    print(response.json())

def drop_database(db_name):
    response = requests.post(f"{SERVER_URL}/drop_database", json={"db_name": db_name})
    print(response.json())

def use_database(db_name):
    response = requests.post(f"{SERVER_URL}/use_database", json={"db_name": db_name})
    print(response.json())
    global selected_db 
    selected_db = db_name

def drop_table(db_name, table_name):
    response = requests.post(f"{SERVER_URL}/drop_table", json={
           "db_name": db_name,
        "table_name": table_name
    })
    print(response.json())

def create_table(db_name, table_name):
    structure = {}
    primary_key = []
    unique_keys = []
    # indexes = {}

    print("\n Define table structure (enter 'done' when finished):")
    while True:
        attr_name = input("Attribute Name (or 'done'): ").strip()
        if attr_name.lower() == "done":
            break

        attr_type = input(f"Type for {attr_name} (char, varchar, int, etc.): ").strip()
        attr_length = int(input(f"Length for {attr_name}: ").strip())
        nullable = input(f"Can {attr_name} be NULL? (yes/no): ").strip().lower() == "yes"

        structure[attr_name] = {"type": attr_type, "length": attr_length, "nullable": nullable}

        is_pk = input(f"Is {attr_name} a PRIMARY KEY? (yes/no): ").strip().lower() == "yes"
        if is_pk:
            primary_key.append(attr_name)

        is_unique = input(f"Is {attr_name} UNIQUE? (yes/no): ").strip().lower() == "yes"
        if is_unique:
            unique_keys.append(attr_name)

       # has_index = input(f"Create index on {attr_name}? (yes/no): ").strip().lower() == "yes"
        

    table_payload = {
        "db_name": db_name,
        "table_name": table_name,
        "file_name": f"{table_name}.bin",
        "row_length": sum(attr["length"] for attr in structure.values()),
        "structure": structure,
        "primary_key": primary_key,
        "unique_keys": unique_keys,
       # "indexes": indexes
    }

    response = requests.post(f"{SERVER_URL}/create_table", json=table_payload)
    print(response.json())

def parse_command(command):
    global selected_db
    parts = command.strip().split()
    
    if command.lower().startswith("create database"):
        db_name = parts[-1]
        create_database(db_name)

    elif command.lower().startswith("drop database"):
        db_name = parts[-1]
        drop_database(db_name)

    elif command.lower().startswith("use"):
        db_name = parts[-1]
        use_database(db_name)
    
    elif command.lower().startswith("drop table"):
        if selected_db is None:
            print("No selected database")
            return
        
        table_index = parts.index("table") + 1
        table_name = parts[table_index]
        drop_table(selected_db, table_name)
                
    elif command.lower().startswith("create table"):
        if selected_db is None:
            print("No selected database")
            return
        
        table_index = parts.index("table") + 1
        
        table_name = parts[table_index]
        db_name = selected_db

        create_table(db_name, table_name)

    else:
        print("Invalid Command")

def main():
    print("Universal DBMS CLI (Type 'exit' to quit)")
    while True:
        cmd = input("DBMS> ")
        if cmd.lower() in ["exit", "quit"]:
            break
        parse_command(cmd)

if __name__ == "__main__":
    main()
