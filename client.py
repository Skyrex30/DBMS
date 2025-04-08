import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import requests
import json


SERVER_URL = "http://127.0.0.1:5000"
selected_db = None

def refresh_database():
    try:
        response = requests.get(f"{SERVER_URL}/list_databases", timeout=2)
        if response.status_code == 200:
            databases = response.json().get("databases", [])
            database_listbox.delete(0, tk.END)
            for db in databases:
                database_listbox.insert(tk.END, db)
        else:
            messagebox.showerror("Error", "Failed to retrieve databases!")
    except requests.exceptions.RequestException:
        messagebox.showerror("Error", "Could not connect to server")

def create_database():
    db_name = simpledialog.askstring("Create Database", "Enter database name:")
    if db_name:
        try:
            response = requests.post(f"{SERVER_URL}/create_database", 
                                   json={"db_name": db_name},
                                   timeout=2)
            if response.status_code == 200:
                messagebox.showinfo("Success", f"Database created: {db_name}")
                refresh_database()
            else:
                messagebox.showerror("Error", response.json().get("error", "Failed to create database!"))
        except requests.exceptions.RequestException:
            messagebox.showerror("Error", "Could not connect to server")

def drop_database():
    selected = database_listbox.curselection()
    if selected:
        db_name = database_listbox.get(selected[0])
        try:
            response = requests.post(f"{SERVER_URL}/drop_database", 
                                   json={"db_name": db_name},
                                   timeout=2)
            if response.status_code == 200:
                messagebox.showinfo("Success", f"Database dropped: {db_name}")
                refresh_database()
            else:
                messagebox.showerror("Error", response.json().get("error", "Failed to drop database!"))
        except requests.exceptions.RequestException:
            messagebox.showerror("Error", "Could not connect to server")
    else:
        messagebox.showerror("Error", "Select a database to drop!")

def use_database():
    global selected_db
    selected = database_listbox.curselection()
    if selected:
        selected_db = database_listbox.get(selected[0])
        try:
            response = requests.post(
                f"{SERVER_URL}/use_database",
                json={"db_name": selected_db},
                timeout=2
            )
            if response.status_code == 200:
                data = response.json()
                messagebox.showinfo("Success", data["message"])
                status_bar.config(text=f"Selected DB: {selected_db}")

                table_listbox.delete(0, tk.END)
                for table in data.get("tables", []):
                    table_listbox.insert(tk.END, table)
            else:
                messagebox.showerror("Error", response.json().get("error", "Failed to use database!"))
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")
            refresh_tables()
    else:
        messagebox.showerror("Error", "Select a database to use!")

def refresh_tables():
    if not selected_db:
        return
    try:
        response = requests.get(
            f"{SERVER_URL}/list_tables",
            params={"db_name": selected_db},
            timeout=2
        )
        if response.status_code == 200:
            tables = response.json().get("tables", [])
            table_listbox.delete(0, tk.END)
            for table in tables:
                table_listbox.insert(tk.END, table)
        else:
            messagebox.showerror("Error", response.json().get("error", "Failed to load tables"))
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Could not connect to server: {str(e)}")

def create_table():
    if not selected_db:
        messagebox.showerror("Error", "Select a database first!")
        return
    
    table_window = tk.Toplevel(root)
    table_window.title("Create Table")
    table_window.geometry("500x600")
    
    tk.Label(table_window, text="Table Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    table_name_entry = tk.Entry(table_window, width=30)
    table_name_entry.grid(row=0, column=1, padx=5, pady=5)
    
    attr_frame = tk.LabelFrame(table_window, text="Table Attributes", padx=5, pady=5)
    attr_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
    
    attr_listbox = tk.Listbox(attr_frame, height=10)
    attr_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    attr_controls = tk.Frame(attr_frame)
    attr_controls.pack(side=tk.RIGHT, fill=tk.Y)
    
    attr_name_entry = tk.Entry(attr_controls, width=20)
    attr_name_entry.pack(pady=2)
    
    attr_type_var = tk.StringVar(value="varchar")
    attr_type_menu = tk.OptionMenu(attr_controls, attr_type_var, "varchar", "int", "float", "date")
    attr_type_menu.pack(pady=2)
    
    attr_length_entry = tk.Entry(attr_controls, width=5)
    attr_length_entry.pack(pady=2)
    attr_length_entry.insert(0, "255")
    
    pk_var = tk.BooleanVar()
    pk_check = tk.Checkbutton(attr_controls, text="Primary Key", variable=pk_var)
    pk_check.pack(pady=2)
    
    unique_var = tk.BooleanVar()
    unique_check = tk.Checkbutton(attr_controls, text="Unique", variable=unique_var)
    unique_check.pack(pady=2)
    
    structure = {}
    primary_keys = []
    unique_keys = []
    
    def add_attribute():
        name = attr_name_entry.get()
        if not name:
            return
            
        attr_type = attr_type_var.get()
        length = int(attr_length_entry.get()) if attr_type == "varchar" else 0
        
        structure[name] = {
            "type": attr_type,
            "length": length,
            "nullable": not pk_var.get()
        }
        
        if pk_var.get():
            primary_keys.append(name)
        if unique_var.get():
            unique_keys.append(name)
            
        attr_listbox.insert(tk.END, f"{name} ({attr_type})")
        attr_name_entry.delete(0, tk.END)
    
    tk.Button(attr_controls, text="Add Attribute", command=add_attribute).pack(pady=5)
    
    def submit_table():
        if not table_name_entry.get():
            messagebox.showerror("Error", "Enter table name!")
            return
            
        if not structure:
            messagebox.showerror("Error", "Add at least one attribute!")
            return
            
        table_data = {
            "db_name": selected_db,
            "table_name": table_name_entry.get(),
            "file_name": f"{table_name_entry.get()}.bin",
            "row_length": sum(attr["length"] for attr in structure.values()),
            "structure": structure,
            "primary_key": primary_keys,
            "unique_keys": unique_keys,
            "foreign_keys": {}
        }
        
        try:
            response = requests.post(f"{SERVER_URL}/create_table", 
                                   json=table_data,
                                   timeout=2)
            if response.status_code == 200:
                messagebox.showinfo("Success", f"Table {table_name_entry.get()} created!")
                table_window.destroy()
                refresh_tables()
            else:
                messagebox.showerror("Error", response.json().get("error", "Failed to create table!"))
        except requests.exceptions.RequestException:
            messagebox.showerror("Error", "Could not connect to server")
    
    tk.Button(table_window, text="Create Table", command=submit_table).grid(row=2, column=1, pady=10)

def drop_table():
    if not selected_db:
        messagebox.showerror("Error", "Select a database first!")
        return
    
    selected = table_listbox.curselection()
    if selected:
        table_name = table_listbox.get(selected[0])
        try:
            response = requests.post(f"{SERVER_URL}/drop_table", 
                                  json={"table_name": table_name},
                                  timeout=2)
            if response.status_code == 200:
                messagebox.showinfo("Success", f"Table dropped: {table_name}")
                refresh_tables()
            else:
                messagebox.showerror("Error", response.json().get("error", "Failed to drop table!"))
        except requests.exceptions.RequestException:
            messagebox.showerror("Error", "Could not connect to server")
    else:
        messagebox.showerror("Error", "Select a table to drop!")

def insert_row():
    if not selected_db:
        messagebox.showerror("Error", "Select a database first!")
        return
    
    selected = table_listbox.curselection()
    if not selected:
        messagebox.showerror("Error", "Select a table first!")
        return
    
    table_name = table_listbox.get(selected[0])
    
    try:
        response = requests.get(
            f"{SERVER_URL}/table_structure",
            params={
                "db_name": selected_db,
                "table_name": table_name
            },
            timeout=5
        )
        response_data = response.json()
        
        if response.status_code != 200 or response_data.get("status") != "success":
            error_msg = response_data.get("error", "Failed to get table structure")
            messagebox.showerror("Error", f"{error_msg} (Status: {response.status_code})")
            return
            
        structure = response_data["structure"]
        primary_key = response_data.get("primary_key", [])
        
        insert_window = tk.Toplevel(root)
        insert_window.title(f"Insert into {table_name}")
        
        entries = {}
        row = 0
        
        for pk in primary_key:
            tk.Label(insert_window, text=f"{pk} (Primary Key)*:").grid(row=row, column=0, padx=5, pady=5, sticky="e")
            entries[pk] = tk.Entry(insert_window, width=30)
            entries[pk].grid(row=row, column=1, padx=5, pady=5)
            row += 1
        
        for column, col_type in structure.items():
            if column not in primary_key:
                tk.Label(insert_window, text=f"{column} ({col_type['type']}):").grid(row=row, column=0, padx=5, pady=5, sticky="e")
                entries[column] = tk.Entry(insert_window, width=30)
                entries[column].grid(row=row, column=1, padx=5, pady=5)
                row += 1
        
        def submit_insert():
            primary_key_data = {}
            attributes_data = {}
            
            for pk in primary_key:
                value = entries[pk].get()
                if not value:
                    messagebox.showerror("Error", f"Primary key field '{pk}' is required!")
                    return
                
                if structure[pk]["type"] == "int":
                    try:
                        primary_key_data[pk] = int(value)
                    except ValueError:
                        messagebox.showerror("Error", f"Invalid integer value for {pk}")
                        return
                elif structure[pk]["type"] == "float":
                    try:
                        primary_key_data[pk] = float(value)
                    except ValueError:
                        messagebox.showerror("Error", f"Invalid float value for {pk}")
                        return
                else:
                    primary_key_data[pk] = value
            
            for col, col_type in structure.items():
                if col not in primary_key:
                    value = entries[col].get()
                    if value:
                        if col_type["type"] == "int":
                            try:
                                attributes_data[col] = int(value)
                            except ValueError:
                                messagebox.showerror("Error", f"Invalid integer value for {col}")
                                return
                        elif col_type["type"] == "float":
                            try:
                                attributes_data[col] = float(value)
                            except ValueError:
                                messagebox.showerror("Error", f"Invalid float value for {col}")
                                return
                        else:
                            attributes_data[col] = value
            
            data = {
                "table": table_name,
                "primary_key": primary_key_data,
                "attributes": attributes_data
            }
            
            try:
                response = requests.post(
                    f"{SERVER_URL}/insert",
                    json=data,
                    timeout=5
                )
                response_data = response.json()
                
                if response.status_code == 200 and response_data.get("status") == "success":
                    messagebox.showinfo("Success", response_data.get("message", "Row inserted successfully"))
                    insert_window.destroy()
                else:
                    error_msg = response_data.get("error", "Failed to insert row")
                    messagebox.showerror("Error", f"{error_msg} (Status: {response.status_code})")
            except requests.exceptions.RequestException as e:
                messagebox.showerror("Error", f"Could not connect to server: {str(e)}")
        
        submit_button = tk.Button(insert_window, text="Insert", command=submit_insert)
        submit_button.grid(row=row, column=1, pady=10)
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def delete_row():
    if not selected_db:
        messagebox.showerror("Error", "Select a database first!")
        return
    
    selected = table_listbox.curselection()
    if not selected:
        messagebox.showerror("Error", "Select a table first!")
        return
    
    table_name = table_listbox.get(selected[0])
    
    try:
        response = requests.get(
            f"{SERVER_URL}/table_structure",
            params={
                "db_name": selected_db,
                "table_name": table_name
            },
            timeout=5
        )
        response_data = response.json()
        
        if response.status_code != 200 or response_data.get("status") != "success":
            error_msg = response_data.get("error", "Failed to get table structure")
            messagebox.showerror("Error", f"{error_msg} (Status: {response.status_code})")
            return
            
        primary_key = response_data.get("primary_key", [])
        structure = response_data.get("structure", {})
        
        if not primary_key:
            messagebox.showerror("Error", "This table has no primary key defined!")
            return
        
        delete_window = tk.Toplevel(root)
        delete_window.title(f"Delete from {table_name}")
        
        entries = {}
        row = 0
        
        for pk in primary_key:
            tk.Label(delete_window, text=f"{pk} (Primary Key)*:").grid(row=row, column=0, padx=5, pady=5, sticky="e")
            entries[pk] = tk.Entry(delete_window, width=30)
            entries[pk].grid(row=row, column=1, padx=5, pady=5)
            row += 1
        
        def submit_delete():
            primary_key_data = {}
            
            for pk in primary_key:
                value = entries[pk].get()
                if not value:
                    messagebox.showerror("Error", f"Primary key field '{pk}' is required!")
                    return
                
                #convertalas
                if pk in structure and structure[pk]["type"] == "int":
                    try:
                        primary_key_data[pk] = int(value)
                    except ValueError:
                        messagebox.showerror("Error", f"Invalid integer value for {pk}")
                        return
                elif pk in structure and structure[pk]["type"] == "float":
                    try:
                        primary_key_data[pk] = float(value)
                    except ValueError:
                        messagebox.showerror("Error", f"Invalid float value for {pk}")
                        return
                else:
                    primary_key_data[pk] = value
            
            data = {
                "table": table_name,
                "primary_key": primary_key_data
            }
            
            try:
                response = requests.post(
                    f"{SERVER_URL}/delete",
                    json=data,
                    timeout=5
                )
                response_data = response.json()
                
                if response.status_code == 200 and response_data.get("status") == "success":
                    messagebox.showinfo("Success", response_data.get("message", "Row deleted successfully"))
                    delete_window.destroy()
                else:
                    error_msg = response_data.get("error", "Failed to delete row")
                    messagebox.showerror("Error", f"{error_msg} (Status: {response.status_code})")
            except requests.exceptions.RequestException as e:
                messagebox.showerror("Error", f"Could not connect to server: {str(e)}")
        
        submit_button = tk.Button(delete_window, text="Delete", command=submit_delete)
        submit_button.grid(row=row, column=1, pady=10)
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def refresh():
    refresh_database()
    refresh_tables()

#GUI
root = tk.Tk()
root.title("Database Management System")
root.geometry("800x600")

#databases - left panel 
left_frame = tk.Frame(root, width=200, height=600, bg="lightgray")
left_frame.pack(side=tk.LEFT, fill=tk.Y)

tk.Label(left_frame, text="Databases", bg="lightgray").pack(pady=5)
database_listbox = tk.Listbox(left_frame)
database_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

button_frame = tk.Frame(left_frame, bg="lightgray")
button_frame.pack(fill=tk.X, pady=5)

tk.Button(button_frame, text="Create DB", command=create_database).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
tk.Button(button_frame, text="Drop DB", command=drop_database).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
tk.Button(button_frame, text="Use DB", command=use_database).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
tk.Button(left_frame, text="Refresh", command=refresh).pack(fill=tk.X, padx=5, pady=2)

#table operations - right panel
right_frame = tk.Frame(root)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

#table list
table_frame = tk.Frame(right_frame)
table_frame.pack(fill=tk.X, pady=5)

tk.Label(table_frame, text="Tables").pack(side=tk.LEFT, padx=5)
table_listbox = tk.Listbox(table_frame)
table_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

#table operations
table_buttons = tk.Frame(right_frame)
table_buttons.pack(fill=tk.X, pady=5)

tk.Button(table_buttons, text="Create Table", command=create_table).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
tk.Button(table_buttons, text="Drop Table", command=drop_table).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)

data_buttons = tk.Frame(right_frame)
data_buttons.pack(fill=tk.X, pady=5)

tk.Button(data_buttons, text="Insert Row", command=insert_row).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
tk.Button(data_buttons, text="Delete Row", command=delete_row).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)

status_bar = tk.Label(right_frame, text="No database selected", bd=1, relief=tk.SUNKEN, anchor=tk.W)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

refresh_database()
root.mainloop()
