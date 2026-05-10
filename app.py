import tkinter as tk
import sqlite3
import base64
import random
import string

# ---------- Database ----------
conn = sqlite3.connect("passwords.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS passwords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account TEXT,
    password TEXT
)
""")

conn.commit()

# ---------- Utils ----------
def encode(text):
    return base64.b64encode(text.encode()).decode()

def decode(text):
    return base64.b64decode(text.encode()).decode()

# ---------- Refresh ----------
def refresh(search_text=""):
    listbox.delete(0, tk.END)

    cursor.execute("SELECT * FROM passwords")

    for row in cursor.fetchall():
        account = row[1]
        password = decode(row[2])

        display = f"{row[0]}. {account} → {password}"

        if search_text.lower() in display.lower():
            listbox.insert(tk.END, display)

# ---------- Save ----------
def save_password():
    account = account_entry.get()
    password = password_entry.get()

    if account and password:
        cursor.execute(
            "INSERT INTO passwords (account, password) VALUES (?, ?)",
            (account, encode(password))
        )

        conn.commit()

        account_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)

        refresh()

# ---------- Delete ----------
def delete_password():
    selected = listbox.curselection()

    if selected:
        item = listbox.get(selected[0])

        password_id = item.split(".")[0]

        cursor.execute(
            "DELETE FROM passwords WHERE id=?",
            (password_id,)
        )

        conn.commit()

        refresh()

# ---------- Update ----------
def load_selected(event):
    selected = listbox.curselection()

    if selected:
        item = listbox.get(selected[0])

        parts = item.split(" → ")

        account = parts[0].split(". ", 1)[1]
        password = parts[1]

        account_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)

        account_entry.insert(0, account)
        password_entry.insert(0, password)

def update_password():
    selected = listbox.curselection()

    if selected:
        item = listbox.get(selected[0])

        password_id = item.split(".")[0]

        cursor.execute(
            "UPDATE passwords SET account=?, password=? WHERE id=?",
            (
                account_entry.get(),
                encode(password_entry.get()),
                password_id
            )
        )

        conn.commit()
        refresh()

# ---------- Search ----------
def search_passwords():
    refresh(search_entry.get())

# ---------- Generator ----------
def generate_password():
    chars = string.ascii_letters + string.digits + "!@#$%"

    generated = "".join(
        random.choice(chars) for _ in range(12)
    )

    password_entry.delete(0, tk.END)
    password_entry.insert(0, generated)

# ---------- GUI ----------
root = tk.Tk()
root.title("Advanced Password Manager")
root.configure(bg="#222222")

# Labels
tk.Label(root, text="Account", bg="#222222", fg="white").pack()

account_entry = tk.Entry(root, width=40)
account_entry.pack()

tk.Label(root, text="Password", bg="#222222", fg="white").pack()

password_entry = tk.Entry(root, width=40, show="*")
password_entry.pack()

# Buttons
tk.Button(
    root,
    text="Generate Password",
    command=generate_password
).pack(pady=5)

tk.Button(
    root,
    text="Save",
    command=save_password
).pack()

tk.Button(
    root,
    text="Update Selected",
    command=update_password
).pack()

# Search
search_entry = tk.Entry(root, width=40)
search_entry.pack(pady=5)

tk.Button(
    root,
    text="Search",
    command=search_passwords
).pack()

# Listbox
listbox = tk.Listbox(
    root,
    width=60,
    bg="#333333",
    fg="white"
)

listbox.pack(pady=10)

listbox.bind("<<ListboxSelect>>", load_selected)

# Delete
tk.Button(
    root,
    text="Delete Selected",
    command=delete_password
).pack()

refresh()

root.mainloop()

conn.close()
