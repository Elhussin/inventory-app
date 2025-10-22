# import tkinter as tk
# from tkinter import filedialog, ttk
# import csv
# import sqlite3
# from tkinter import messagebox


# DB_FILE = "inventory.db"

# # ------------------ وظائف قاعدة البيانات ------------------ #
# def create_table():
#     conn = sqlite3.connect(DB_FILE)
#     c = conn.cursor()
#     c.execute("""
#         CREATE TABLE IF NOT EXISTS products (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT,
#             code TEXT UNIQUE,
#             description TEXT,
#             cost REAL,
#             retail REAL,
#             required_qty INTEGER,
#             good_qty INTEGER,
#             gift INTEGER,
#             damaged_qty INTEGER,
#             total_qty INTEGER,
#             note TEXT
#         )
#     """)
#     conn.commit()
#     conn.close()


# def safe_int(value):
#     try:
#         return int(float(value))
#     except (ValueError, TypeError):
#         return 0


# def safe_float(value):
#     try:
#         return float(value)
#     except (ValueError, TypeError):
#         return 0.0


# # # ------------------ نسخ CSV ------------------ #
# # def copy_csv_to_db(csv_file):
# #     conn = sqlite3.connect(DB_FILE)
# #     c = conn.cursor()
# #     added = 0
# #     skipped = 0
# #     errors = 0
# #     last_rows = []

# #     with open(csv_file, 'r', encoding='utf-8-sig') as f:
# #         reader = csv.DictReader(f)

# #         for index, row in enumerate(reader, start=1):
# #             try:
# #                 code = row.get('code', '').strip()

# #                 # تحقق إذا الكود موجود مسبقًا
# #                 c.execute("SELECT 1 FROM products WHERE code = ?", (code,))
# #                 exists = c.fetchone()

# #                 if exists:
# #                     skipped += 1
# #                     last_rows.append((index, code, 'skipped'))
# #                     continue

# #                 # إدراج سجل جديد
# #                 c.execute("""
# #                     INSERT INTO products (
# #                         name, code, description, cost, retail,
# #                         required_qty, good_qty, gift, damaged_qty, total_qty
# #                     )
# #                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
# #                 """, (
# #                     row.get('name', '').strip(),
# #                     code,
# #                     row.get('description', '').strip(),
# #                     safe_float(row.get('cost', 0)),
# #                     safe_float(row.get('retail', 0)),
# #                     safe_int(row.get('required_qty', 0)),
# #                     safe_int(row.get('good_qty', 0)),
# #                     safe_int(row.get('gift', 0)),
# #                     safe_int(row.get('damaged_qty', 0)),
# #                     safe_int(row.get('total_qty', 0)),
# #                 ))

# #                 added += 1
# #                 last_rows.append((index, code, 'added'))

# #             except sqlite3.IntegrityError:
# #                 skipped += 1
# #                 last_rows.append((index, code, 'duplicate'))
# #             except Exception as e:
# #                 errors += 1
# #                 last_rows.append((index, code, f'error: {e}'))

# #     conn.commit()
# #     conn.close()
# #     return added, skipped, errors, last_rows


# # # ------------------ تحديث CSV ------------------ #
# # def update_csv_to_db(csv_file):
# #     conn = sqlite3.connect(DB_FILE)
# #     c = conn.cursor()

# #     inserted = 0
# #     updated = 0
# #     deleted = 0
# #     errors = 0
# #     result_rows = []

# #     # تحميل الأكواد من الملف الجديد
# #     with open(csv_file, 'r', encoding='utf-8-sig') as f:
# #         reader = csv.DictReader(f)
# #         csv_rows = list(reader)
# #         new_codes = {row.get('code', '').strip() for row in csv_rows if row.get('code')}

# #     # تحميل الأكواد الموجودة حالياً في قاعدة البيانات
# #     c.execute("SELECT code FROM products")
# #     db_codes = {row[0] for row in c.fetchall()}

# #     # الأكواد المحذوفة (موجودة في DB لكن غير موجودة في CSV)
# #     codes_to_delete = db_codes - new_codes

# #     # حذف الأكواد القديمة الغير موجودة في الملف الجديد
# #     for code in codes_to_delete:
# #         try:
# #             c.execute("DELETE FROM products WHERE code = ?", (code,))
# #             deleted += 1
# #             print(f"🗑️ Deleted old product: {code}")
# #         except Exception as e:
# #             errors += 1
# #             print(f"⚠️ Error deleting {code}: {e}")

# #     # تحديث أو إدخال السجلات من الملف الجديد
# #     for index, row in enumerate(csv_rows, start=1):
# #         try:
# #             code = (row.get('code') or '').strip()
# #             name = (row.get('name') or '').strip()
# #             description = (row.get('description') or '').strip()
# #             cost = safe_float(row.get('cost', 0))
# #             retail = safe_float(row.get('retail', 0))
# #             required_qty = safe_int(row.get('required_qty', 0))

# #             c.execute("SELECT 1 FROM products WHERE code = ?", (code,))
# #             exists = c.fetchone() is not None

# #             if exists:
# #                 c.execute("""
# #                     UPDATE products
# #                     SET name = ?, description = ?, cost = ?, retail = ?, required_qty = ?
# #                     WHERE code = ?
# #                 """, (name, description, cost, retail, required_qty, code))
# #                 updated += 1
# #                 result_rows.append((index, code, 'updated'))
# #             else:
# #                 c.execute("""
# #                     INSERT INTO products (code, name, description, cost, retail, required_qty)
# #                     VALUES (?, ?, ?, ?, ?, ?)
# #                 """, (code, name, description, cost, retail, required_qty))
# #                 inserted += 1
# #                 result_rows.append((index, code, 'inserted'))

# #         except Exception as e:
# #             errors += 1
# #             result_rows.append((index, code, f'error: {e}'))

# #     conn.commit()
# #     conn.close()

# #     print(f"\n✅ Summary: {inserted} inserted | {updated} updated | 🗑️ {deleted} deleted | ⚠️ {errors} errors")
# #     return inserted, updated, deleted, errors, result_rows

# def sync_csv_to_db(csv_file):
#     conn = sqlite3.connect(DB_FILE)
#     c = conn.cursor()

#     inserted = 0
#     updated = 0
#     deleted = 0
#     errors = 0
#     result_rows = []

#     # --- Load new CSV data ---
#     with open(csv_file, 'r', encoding='utf-8-sig') as f:
#         reader = csv.DictReader(f)
#         csv_rows = list(reader)
#         new_codes = {row.get('code', '').strip() for row in csv_rows if row.get('code')}

#     # --- Load existing DB codes ---
#     c.execute("SELECT code FROM products")
#     db_codes = {row[0] for row in c.fetchall()}

#     # --- Find codes to delete (exist in DB but not in CSV) ---
#     codes_to_delete = db_codes - new_codes

#     for code in codes_to_delete:
#         try:
#             c.execute("DELETE FROM products WHERE code = ?", (code,))
#             deleted += 1
#             print(f"🗑️ Deleted old product: {code}")
#         except Exception as e:
#             errors += 1
#             print(f"⚠️ Error deleting {code}: {e}")

#     # --- Process each row in CSV (insert or update) ---
#     for index, row in enumerate(csv_rows, start=1):
#         try:
#             code = (row.get('code') or '').strip()
#             if not code:
#                 continue

#             name = (row.get('name') or '').strip()
#             description = (row.get('description') or '').strip()
#             cost = safe_float(row.get('cost', 0))
#             retail = safe_float(row.get('retail', 0))
#             required_qty = safe_int(row.get('required_qty', 0))
#             good_qty = safe_int(row.get('good_qty', 0))
#             gift = safe_int(row.get('gift', 0))
#             damaged_qty = safe_int(row.get('damaged_qty', 0))
#             total_qty = safe_int(row.get('total_qty', 0))

#             c.execute("SELECT 1 FROM products WHERE code = ?", (code,))
#             exists = c.fetchone() is not None

#             if exists:
#                 # 🔁 Update record if it already exists
#                 c.execute("""
#                     UPDATE products
#                     SET name=?, description=?, cost=?, retail=?, required_qty=?,
#                         good_qty=?, gift=?, damaged_qty=?, total_qty=?
#                     WHERE code=?
#                 """, (name, description, cost, retail, required_qty,
#                       good_qty, gift, damaged_qty, total_qty, code))
#                 updated += 1
#                 result_rows.append((index, code, 'updated'))
#             else:
#                 # 🆕 Insert new record
#                 c.execute("""
#                     INSERT INTO products (
#                         code, name, description, cost, retail,
#                         required_qty, good_qty, gift, damaged_qty, total_qty
#                     )
#                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#                 """, (code, name, description, cost, retail,
#                       required_qty, good_qty, gift, damaged_qty, total_qty))
#                 inserted += 1
#                 result_rows.append((index, code, 'inserted'))

#         except Exception as e:
#             errors += 1
#             result_rows.append((index, code, f'error: {e}'))
#             print(f"⚠️ Error processing {code}: {e}")

#     conn.commit()
#     conn.close()

#     print(f"\n✅ Summary: {inserted} inserted | {updated} updated | 🗑️ {deleted} deleted | ⚠️ {errors} errors")
#     return inserted, updated, deleted, errors, result_rows


# # ------------------ واجهة المستخدم ------------------ #
# def refresh_tree(tree, rows):
#     for item in tree.get_children():
#         tree.delete(item)
#     for r in rows:
#         tree.insert("", "end", values=r)

# def select_file_sync(mode="update"):
#     """
#     mode: "copy" → import data (will update existing rows)
#           "update" → update & delete missing rows
#     """
#     file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
#     if not file_path:
#         return

#     # --- Compose warning message ---
#     warning_msg = (
#         "Before proceeding, please make sure you have a BACKUP of your database file.\n\n"
#         "This operation will perform the following actions:\n\n"
#         "1 Update the following columns if the record exists:\n"
#         "   • name\n"
#         "   • description\n"
#         "   • cost\n"
#         "   • retail\n"
#         "   • required_qty\n\n"
#         "2 The following columns will NOT be modified:\n"
#         "   • good_qty\n"
#         "   • gift\n"
#         "   • damaged_qty\n"
#         "   • total_qty\n\n"
#     )

#     if mode == "update":
#         warning_msg += (
#             "3 Any record that exists in the database but does NOT exist in the new CSV file\n"
#             "   will be DELETED completely.\n\n"
#         )
#     else:
#         warning_msg += "3 Any record that exists in the database but not in the CSV will remain unchanged.\n\n"

#     warning_msg += "⚠️ Please confirm that you understand and want to continue."

#     # --- Ask for confirmation ---
#     confirm = messagebox.askokcancel(
#         "⚠️ Confirm Database Operation",
#         warning_msg,
#         icon="warning"
#     )
#     if not confirm:
#         messagebox.showinfo("Operation Cancelled", "❌ The operation was cancelled.")
#         return

#     # --- Run sync ---
#     lbl_target_file = lbl_update_file if mode == "update" else lbl_copy_file
#     lbl_target_stats = lbl_update_stats if mode == "update" else lbl_copy_stats
#     tree_target = tree_update if mode == "update" else tree_copy

#     lbl_target_file.config(text=file_path)

#     inserted, updated, deleted, errors, result_rows = sync_csv_to_db(file_path)

#     lbl_target_stats.config(
#         text=f"🆕 Inserted: {inserted} | 🔁 Updated: {updated} | 🗑️ Deleted: {deleted} | ⚠️ Errors: {errors}"
#     )
#     refresh_tree(tree_target, result_rows)

#     # --- Show result message ---
#     messagebox.showinfo(
#         "Operation Completed",
#         (
#             f"✅ {mode.capitalize()} operation completed successfully.\n\n"
#             f"🆕 Inserted: {inserted}\n"
#             f"🔁 Updated: {updated}\n"
#             f"🗑️ Deleted: {deleted}\n"
#             f"⚠️ Errors: {errors}\n\n"
#             "💡 Tip: Always keep a backup of your database."
#         )
#     )

# # ------------------ تصميم الواجهة ------------------ #
# create_table()

# root = tk.Tk()
# root.title("📦 Inventory CSV Manager")
# root.geometry("720x500")
# root.configure(bg="#f4f6f8")

# style = ttk.Style()
# style.theme_use("clam")

# # تحسين مظهر الأزرار والجداول
# style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=8, background="#4CAF50", foreground="white")
# style.map("TButton", background=[("active", "#45a049")])

# style.configure("Treeview", font=("Segoe UI", 10), rowheight=26, background="#fff", fieldbackground="#fff")
# style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#0078D7", foreground="white")

# tab_control = ttk.Notebook(root)
# tab_copy = ttk.Frame(tab_control, padding=10)
# tab_update = ttk.Frame(tab_control, padding=10)

# tab_control.add(tab_copy, text="📥 Create Database")
# tab_control.add(tab_update, text="🔁 Update Database")
# tab_control.pack(expand=1, fill="both", padx=10, pady=10)

# # ----- تبويب النسخ ----- #
# btn_copy = ttk.Button(tab_copy, text="📂 Select CSV to Create Database",command=lambda: select_file_sync("copy"))



# btn_copy.pack(pady=10)
# lbl_copy_file = ttk.Label(tab_copy, text="No file selected", foreground="#0078D7", font=("Segoe UI", 10))
# lbl_copy_file.pack()
# lbl_copy_stats = ttk.Label(tab_copy, text="", font=("Segoe UI", 10))
# lbl_copy_stats.pack(pady=5)

# frame_copy = ttk.Frame(tab_copy)
# frame_copy.pack(expand=True, fill="both")

# tree_copy = ttk.Treeview(frame_copy, columns=("index", "code", "status"), show="headings")
# tree_copy.heading("index", text="#")
# tree_copy.heading("code", text="Code")
# tree_copy.heading("status", text="Status")
# tree_copy.pack(side="left", expand=True, fill="both")

# scroll_y_copy = ttk.Scrollbar(frame_copy, orient="vertical", command=tree_copy.yview)
# tree_copy.configure(yscrollcommand=scroll_y_copy.set)
# scroll_y_copy.pack(side="right", fill="y")

# # ----- تبويب التحديث ----- #
# btn_update = ttk.Button(tab_update, text="🧾 Select CSV to Update Database", command=lambda: select_file_sync("update"))

# btn_update.pack(pady=10)
# lbl_update_file = ttk.Label(tab_update, text="No file selected", foreground="#0078D7", font=("Segoe UI", 10))
# lbl_update_file.pack()
# lbl_update_stats = ttk.Label(tab_update, text="", font=("Segoe UI", 10))
# lbl_update_stats.pack(pady=5)

# frame_update = ttk.Frame(tab_update)
# frame_update.pack(expand=True, fill="both")

# tree_update = ttk.Treeview(frame_update, columns=("index", "code", "status"), show="headings")
# tree_update.heading("index", text="#")
# tree_update.heading("code", text="Code")
# tree_update.heading("status", text="Status")
# tree_update.pack(side="left", expand=True, fill="both")

# scroll_y_update = ttk.Scrollbar(frame_update, orient="vertical", command=tree_update.yview)
# tree_update.configure(yscrollcommand=scroll_y_update.set)
# scroll_y_update.pack(side="right", fill="y")

# root.mainloop()

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import csv
import sqlite3

DB_FILE = "inventory.db"

# ------------------ وظائف قاعدة البيانات ------------------ #
def create_table():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            code TEXT UNIQUE,
            description TEXT,
            cost REAL,
            retail REAL,
            required_qty INTEGER,
            good_qty INTEGER,
            gift INTEGER,
            damaged_qty INTEGER,
            total_qty INTEGER,
            note TEXT
        )
    """)
    conn.commit()
    conn.close()


def safe_int(value):
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return 0


def safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


# ------------------ مزامنة CSV مع DB ------------------ #
def sync_csv_to_db(csv_file):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    inserted = 0
    updated = 0
    deleted = 0
    errors = 0
    result_rows = []

    # --- Load new CSV data ---
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        csv_rows = list(reader)
        new_codes = {row.get('code', '').strip() for row in csv_rows if row.get('code')}

    # --- Load existing DB codes ---
    c.execute("SELECT code FROM products")
    db_codes = {row[0] for row in c.fetchall()}

    # --- Find codes to delete (exist in DB but not in CSV) ---
    codes_to_delete = db_codes - new_codes

    for code in codes_to_delete:
        try:
            c.execute("DELETE FROM products WHERE code = ?", (code,))
            deleted += 1
            print(f"🗑️ Deleted old product: {code}")
        except Exception as e:
            errors += 1
            print(f"⚠️ Error deleting {code}: {e}")

    # --- Process each row in CSV (insert or update) ---
    for index, row in enumerate(csv_rows, start=1):
        try:
            code = (row.get('code') or '').strip()
            if not code:
                continue

            name = (row.get('name') or '').strip()
            description = (row.get('description') or '').strip()
            cost = safe_float(row.get('cost', 0))
            retail = safe_float(row.get('retail', 0))
            required_qty = safe_int(row.get('required_qty', 0))
            good_qty = safe_int(row.get('good_qty', 0))
            gift = safe_int(row.get('gift', 0))
            damaged_qty = safe_int(row.get('damaged_qty', 0))
            total_qty = safe_int(row.get('total_qty', 0))

            c.execute("SELECT 1 FROM products WHERE code = ?", (code,))
            exists = c.fetchone() is not None

            if exists:
                c.execute("""
                    UPDATE products
                    SET name=?, description=?, cost=?, retail=?, required_qty=?
                    WHERE code=?
                """,(name, description, cost, retail, required_qty, code))
                updated += 1
                result_rows.append((index, code, 'updated'))
            else:
                c.execute("""
                    INSERT INTO products (
                        code, name, description, cost, retail,
                        required_qty, good_qty, gift, damaged_qty, total_qty
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (code, name, description, cost, retail,
                      required_qty, good_qty, gift, damaged_qty, total_qty))
                inserted += 1
                result_rows.append((index, code, 'inserted'))

        except Exception as e:
            errors += 1
            result_rows.append((index, code, f'error: {e}'))
            print(f"⚠️ Error processing {code}: {e}")

    conn.commit()
    conn.close()

    print(f"\n✅ Summary: {inserted} inserted | {updated} updated | 🗑️ {deleted} deleted | ⚠️ {errors} errors")
    return inserted, updated, deleted, errors, result_rows


# ------------------ واجهة المستخدم ------------------ #
def refresh_tree(tree, rows):
    for item in tree.get_children():
        tree.delete(item)
    for r in rows:
        tree.insert("", "end", values=r)


def select_file_sync(mode="update"):
    """
    mode: "copy" → insert/create CSV
          "update" → update/delete CSV
    """
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    # --- Compose warning message ---
    warning_msg = (
        "Before proceeding, please make sure you have a BACKUP of your database file.\n\n"
        "This operation will perform the following actions:\n\n"
        "1 Update the following columns if the record exists:\n"
        "   • name\n"
        "   • description\n"
        "   • cost\n"
        "   • retail\n"
        "   • required_qty\n\n"
        "2 The following columns will NOT be modified:\n"
        "   • good_qty\n"
        "   • gift\n"
        "   • damaged_qty\n"
        "   • total_qty\n\n"
    )

    if mode == "update":
        warning_msg += (
            "3 Any record that exists in the database but does NOT exist in the new CSV file\n"
            "   will be DELETED completely.\n\n"
        )
    else:
        warning_msg += "3 Any record that exists in the database but not in the CSV will remain unchanged.\n\n"

    warning_msg += "⚠️ Please confirm that you understand and want to continue."

    # --- Ask for confirmation ---
    confirm = messagebox.askokcancel(
        "⚠️ Confirm Database Operation",
        warning_msg,
        icon="warning"
    )
    if not confirm:
        messagebox.showinfo("Operation Cancelled", "❌ The operation was cancelled.")
        return

    lbl_file.config(text=file_path)
    inserted, updated, deleted, errors, result_rows = sync_csv_to_db(file_path)

    lbl_stats.config(
        text=f"🆕 Inserted: {inserted} | 🔁 Updated: {updated} | 🗑️ Deleted: {deleted} | ⚠️ Errors: {errors}"
    )
    refresh_tree(tree_main, result_rows)

    # --- Show result message ---
    messagebox.showinfo(
        "Operation Completed",
        (
            f"✅ {mode.capitalize()} operation completed successfully.\n\n"
            f"🆕 Inserted: {inserted}\n"
            f"🔁 Updated: {updated}\n"
            f"🗑️ Deleted: {deleted}\n"
            f"⚠️ Errors: {errors}\n\n"
            "💡 Tip: Always keep a backup of your database."
        )
    )


# ------------------ تصميم الواجهة ------------------ #
create_table()

root = tk.Tk()
root.title("📦 Inventory CSV Manager")
root.geometry("750x500")
root.configure(bg="#f4f6f8")

style = ttk.Style()
style.theme_use("clam")

# تحسين مظهر الأزرار والجداول
style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=8, background="#4CAF50", foreground="white")
style.map("TButton", background=[("active", "#45a049")])

style.configure("Treeview", font=("Segoe UI", 10), rowheight=26, background="#fff", fieldbackground="#fff")
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#0078D7", foreground="white")

tab_control = ttk.Notebook(root)
tab_main = ttk.Frame(tab_control, padding=10)
tab_control.add(tab_main, text="📦 Manage Database")
tab_control.pack(expand=1, fill="both", padx=10, pady=10)

# ----- أزرار العمليات ----- #
btn_copy = ttk.Button(tab_main, text="📂 Create / Insert CSV", command=lambda: select_file_sync("copy"))
btn_copy.pack(pady=10)

btn_update = ttk.Button(tab_main, text="🧾 Update / Delete CSV", command=lambda: select_file_sync("update"))
btn_update.pack(pady=5)

# ----- عرض الملف والإحصائيات ----- #
lbl_file = ttk.Label(tab_main, text="No file selected", foreground="#0078D7", font=("Segoe UI", 10))
lbl_file.pack()
lbl_stats = ttk.Label(tab_main, text="", font=("Segoe UI", 10))
lbl_stats.pack(pady=5)

# ----- Treeview لعرض النتائج ----- #
frame_tree = ttk.Frame(tab_main)
frame_tree.pack(expand=True, fill="both")

tree_main = ttk.Treeview(frame_tree, columns=("index", "code", "status"), show="headings")
tree_main.heading("index", text="#")
tree_main.heading("code", text="Code")
tree_main.heading("status", text="Status")
tree_main.pack(side="left", expand=True, fill="both")

scroll_y = ttk.Scrollbar(frame_tree, orient="vertical", command=tree_main.yview)
tree_main.configure(yscrollcommand=scroll_y.set)
scroll_y.pack(side="right", fill="y")

root.mainloop()
