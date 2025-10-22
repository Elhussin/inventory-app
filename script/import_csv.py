
import tkinter as tk
from tkinter import filedialog, messagebox
import sqlite3
import csv
import ttkbootstrap as tb

def copy_csv_to_db(csv_file, db_file):
    """نسخ بيانات CSV إلى قاعدة البيانات"""
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            code TEXT,
            description TEXT,
            cost REAL,
            retail REAL,
            required_qty INTEGER,
            good_qty INTEGER,
            damaged_qty INTEGER,
            gift INTEGER,
            total_qty INTEGER,
            note TEXT
        )
    """)

    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            c.execute("""
                INSERT INTO products (name, code, description, cost, retail, required_qty, good_qty, damaged_qty, total_qty)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row.get('name', ''),
                row.get('code', ''),
                row.get('description', ''),
                float(row.get('cost', 0) or 0),
                float(row.get('retail', 0) or 0),
                int(row.get('required_qty', 0) or 0),
                int(row.get('good_qty', 0) or 0),
                int(row.get('damaged_qty', 0) or 0),
                int(row.get('total_qty', 0) or 0),
            ))
            count += 1

    conn.commit()
    conn.close()
    return count


def browse_csv():
    """Select CSV file"""
    file_path = filedialog.askopenfilename(
        title="Select CSV file",
        filetypes=[("CSV files", "*.csv")]
    )
    if file_path:
        csv_path_var.set(file_path)


def import_data():
    """Import data when the add button is clicked"""
    csv_file = csv_path_var.get()
    db_file = db_path_var.get()

    if not csv_file:
        messagebox.showwarning("Warning", "Please select a CSV file first.")
        return

    if not db_file:
        messagebox.showwarning("Warning", "Please select a database file.")
        return

    try:
        count = copy_csv_to_db(csv_file, db_file)
        messagebox.showinfo("Success ✅", f"Successfully imported {count} rows into the database.")
    except Exception as e:
        print(e)
        messagebox.showerror("Error", f"An error occurred during import:\n{e}")


# واجهة المستخدم
root = tb.Window(themename="flatly")
root.title("📦 Import products from CSV to database")
root.geometry("600x300")

frame = tb.Frame(root, padding=20)
frame.pack(fill="both", expand=True)

# مسار ملف CSV
csv_path_var = tk.StringVar()
db_path_var = tk.StringVar(value="inventory.db")

tb.Label(frame, text="📁 CSV file:").grid(row=0, column=0, sticky="w", pady=10)
tb.Entry(frame, textvariable=csv_path_var, width=50).grid(row=0, column=1, padx=5)
tb.Button(frame, text="Browse", bootstyle="info-outline", command=browse_csv).grid(row=0, column=2, padx=5)

# قاعدة البيانات
tb.Label(frame, text="🗃️ Database:").grid(row=1, column=0, sticky="w", pady=10)
tb.Entry(frame, textvariable=db_path_var, width=50).grid(row=1, column=1, padx=5)

# زر تنفيذ
tb.Button(
    frame,
    text="🚀 Import data to database",
    bootstyle="success",
    command=import_data
).grid(row=2, column=0, columnspan=3, pady=30)

root.mainloop()
