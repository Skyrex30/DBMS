import requests

def main():
    while True:
        cmd = input("DBMS> ")
        if cmd.lower().startswith("create database"):
            db_name = cmd.split()[-1]
            response = requests.post("http://127.0.0.1:5000/create_database", json={"db_name": db_name})
            print(response.json())

if __name__ == "__main__":
    main()