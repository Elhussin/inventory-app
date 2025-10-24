import pyodbc
from dotenv import load_dotenv
import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# =========================
# إعداد الاتصال بـ SQL Server
# =========================
load_dotenv()
server = os.getenv('SERVER')
database = os.getenv('DATABASE')
username = os.getenv('DBUSERNAME')
password = os.getenv('PASSWORD')

connection_string = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password};'
    'Encrypt=no;TrustServerCertificate=yes;'
)

# =========================
# قاعدة بيانات SQLite
# =========================
DB_FILE = "inventory.db"

def create_table():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            name TEXT,
            description TEXT,
            cost REAL,
            retail REAL,
            required_qty INTEGER,
            good_qty INTEGER DEFAULT 0,
            gift INTEGER DEFAULT 0,
            damaged_qty INTEGER DEFAULT 0,
            total_qty INTEGER DEFAULT 0,
            note TEXT
        )
    """)
    conn.commit()
    conn.close()


# =========================
# جلب البيانات من SQL Server
# =========================
def fetch_from_sqlserver():
    try:
        cnxn = pyodbc.connect(connection_string)
        cursor = cnxn.cursor()
        cursor.execute("""
            SELECT 
                dbo.v_ItemCardtaha.Code, 
                dbo.v_ItemCardtaha.Description AS name, 
                SUM(dbo.v_ItemCardtaha.Incoming - dbo.v_ItemCardtaha.Outgoing) AS required_qty, 
                dbo.Product.CostPrice AS cost, 
                dbo.Product.RetailPrice AS retail
            FROM dbo.v_ItemCardtaha 
            INNER JOIN dbo.Product ON dbo.v_ItemCardtaha.Code = dbo.Product.Code
            WHERE (dbo.v_ItemCardtaha.DepName = N'Jeddah Store') 
              AND (dbo.v_ItemCardtaha.MainGroupID = 38 OR dbo.v_ItemCardtaha.MainGroupID = 58)
            GROUP BY dbo.v_ItemCardtaha.Description, dbo.v_ItemCardtaha.Code, dbo.Product.RetailPrice, dbo.Product.CostPrice
            HAVING (SUM(dbo.v_ItemCardtaha.Incoming - dbo.v_ItemCardtaha.Outgoing) <> 0)
        """)
        rows = cursor.fetchall()
        cnxn.close()
        return rows
    except Exception as e:
        messagebox.showerror("SQL Error", f"❌ Error fetching data: {e}")
        return []


# =========================
# حفظ البيانات في SQLite
# =========================
def insert_or_update_data(rows, mode="update"):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    if mode == "new":
        # حذف كل البيانات القديمة
        c.execute("DELETE FROM products")

    inserted, updated = 0, 0

    for r in rows:
        code, name, required_qty, cost, retail = r
        c.execute("SELECT 1 FROM products WHERE code=?", (code,))
        exists = c.fetchone()

        if exists:
            c.execute("""
                UPDATE products
                SET name=?, cost=?, retail=?, required_qty=?
                WHERE code=?
            """, (name, cost, retail, required_qty, code))
            updated += 1
        else:
            c.execute("""
                INSERT INTO products (code, name, cost, retail, required_qty)
                VALUES (?, ?, ?, ?, ?)
            """, (code, name, cost, retail, required_qty))
            inserted += 1

    conn.commit()
    conn.close()
    return inserted, updated


# =========================
# واجهة المستخدم (Tkinter)
# =========================
create_table()

root = tk.Tk()
root.title("📦 SQL → SQLite Inventory Sync")
root.geometry("700x400")
root.configure(bg="#f4f6f8")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=8)
style.configure("Treeview", font=("Segoe UI", 10), rowheight=26)
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

# ----------- دوال الواجهة -----------
def update_data(mode):
    confirm_msg = (
        "سيتم جلب البيانات مباشرة من SQL Server.\n\n"
        "هل تريد المتابعة؟"
    )
    if mode == "new":
        confirm_msg += "\n\n⚠️ سيتم حذف كل البيانات السابقة من قاعدة البيانات المحلية (SQLite)."

    if not messagebox.askokcancel("تأكيد العملية", confirm_msg):
        return

    rows = fetch_from_sqlserver()
    if not rows:
        messagebox.showwarning("تنبيه", "لم يتم العثور على بيانات!")
        return

    inserted, updated = insert_or_update_data(rows, mode)
    lbl_stats.config(
        text=f"✅ تم تنفيذ العملية بنجاح | 🆕 مضافة: {inserted} | 🔁 محدّثة: {updated}"
    )

    refresh_tree(rows)


def refresh_tree(rows):
    for i in tree.get_children():
        tree.delete(i)
    for idx, r in enumerate(rows, start=1):
        tree.insert("", "end", values=(idx, r[0], r[1], r[2], r[3], r[4]))


# ----------- تصميم الواجهة -----------
frame_buttons = ttk.Frame(root)
frame_buttons.pack(pady=10)

btn_update = ttk.Button(frame_buttons, text="🔁 تحديث البيانات", command=lambda: update_data("update"))
btn_update.grid(row=0, column=0, padx=10)

btn_new = ttk.Button(frame_buttons, text="🆕 إنشاء جديد", command=lambda: update_data("new"))
btn_new.grid(row=0, column=1, padx=10)

lbl_stats = ttk.Label(root, text="", font=("Segoe UI", 10))
lbl_stats.pack(pady=5)

columns = ("#", "Code", "Name", "Required Qty", "Cost", "Retail")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
tree.pack(expand=True, fill="both", padx=10, pady=10)

root.mainloop()
