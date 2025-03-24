import tkinter as tk
from tkinter import messagebox
import requests

SERVER_URL = "http://127.0.0.1:5000"

def create_database():
    db_name = db_entry.get()
    if not db_name:
        messagebox.showerror("Hiba", "Adj meg egy adatbázis nevet!")
        return
    
    response = requests.post(f"{SERVER_URL}/create_database", json={"db_name": db_name})
    
    if response.status_code == 200:
        messagebox.showinfo("Siker", f"Az adatbázis létrehozva: {db_name}")
        update_database_list()
    else:
        messagebox.showerror("Hiba", "Az adatbázis létrehozása sikertelen!")

def update_database_list():
    response = requests.get(f"{SERVER_URL}/list_databases")
    if response.status_code == 200:
        databases = response.json().get("databases", [])
        database_listbox.delete(0, tk.END)  # Töröljük a régi listát
        for db in databases:
            database_listbox.insert(tk.END, db)
    else:
        messagebox.showerror("Hiba", "Nem sikerült lekérdezni az adatbázisokat!")

def select_database():
    selected = database_listbox.curselection()
    if not selected:
        messagebox.showerror("Hiba", "Válassz ki egy adatbázist!")
        return
    
    db_name = database_listbox.get(selected[0])
    response = requests.post(f"{SERVER_URL}/select_database", json={"db_name": db_name})
    
    if response.status_code == 200:
        messagebox.showinfo("Siker", f"Az aktív adatbázis: {db_name}")
    else:
        messagebox.showerror("Hiba", "Nem sikerült kiválasztani az adatbázist!")

# GUI setup
root = tk.Tk()
root.title("Adatbázis Kezelő")

root.geometry("500x500")
root.config(bg="gray")

tk.Label(root, text="Adatbázis neve:").pack()
db_entry = tk.Entry(root)
db_entry.pack()

tk.Button(root, text="Létrehozás", command=create_database).pack()
tk.Button(root,text="Frissítés", command=update_database_list).pack()
#tk.Button.size(10,10)

tk.Label(root, text="Elérhető adatbázisok:").pack()
database_listbox = tk.Listbox(root)
database_listbox.pack()

tk.Button(root, text="USE", command=select_database).pack()

update_database_list()  # Indításkor frissítse a listát
root.mainloop()
