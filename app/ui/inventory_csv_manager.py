
from tkinter import filedialog, messagebox

import ttkbootstrap as tb 

import csv
import sqlite3

DB_FILE = "inventory.db"

# ------------------ Database Functions ------------------ #
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


# ------------------ Sync CSV with Database ------------------ #
def sync_csv_to_db(csv_file, mode="update"):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    inserted = 0
    updated = 0
    deleted = 0
    skipped = 0
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

    # --- Deletion only happens in UPDATE mode ---
    if mode == "update":
        codes_to_delete = db_codes - new_codes

        for code in codes_to_delete:
            try:
                # Check total_qty before deletion
                c.execute("SELECT total_qty FROM products WHERE code = ?", (code,))
                result = c.fetchone()
                if result and result[0] > 0:
                    skipped += 1
                    result_rows.append(('N/A', code, f'skipped (qty={result[0]})'))
                    print(f"⏭️ Skipped deletion of {code} (total_qty = {result[0]})")
                    continue
                
                c.execute("DELETE FROM products WHERE code = ?", (code,))
                deleted += 1
                result_rows.append(('N/A', code, 'deleted'))
                print(f"🗑️ Deleted old product: {code}")
            except Exception as e:
                errors += 1
                result_rows.append(('N/A', code, f'error: {e}'))
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

            c.execute("SELECT 1 FROM products WHERE code = ?", (code,))
            exists = c.fetchone() is not None

            if exists:
                # Update only basic data, without touching quantities
                c.execute("""
                    UPDATE products
                    SET name=?, description=?, cost=?, retail=?, required_qty=?
                    WHERE code=?
                """,(name, description, cost, retail, required_qty, code))
                updated += 1
                result_rows.append((index, code, 'updated'))
            else:
                # Insert new product with default quantities = 0 (not from CSV)
                c.execute("""
                    INSERT INTO products (
                        code, name, description, cost, retail,
                        required_qty, good_qty, gift, damaged_qty, total_qty
                    )
                    VALUES (?, ?, ?, ?, ?, ?, 0, 0, 0, 0)
                """, (code, name, description, cost, retail, required_qty))
                inserted += 1
                result_rows.append((index, code, 'inserted'))

        except Exception as e:
            errors += 1
            result_rows.append((index, code, f'error: {e}'))
            print(f"⚠️ Error processing {code}: {e}")

    conn.commit()
    conn.close()

    print(f"\n✅ Summary: {inserted} inserted | {updated} updated | 🗑️ {deleted} deleted | ⏭️ {skipped} skipped | ⚠️ {errors} errors")
    return inserted, updated, deleted, skipped, errors, result_rows


# ------------------ User Interface ------------------ #
def refresh_tree(tree, rows):
    for item in tree.get_children():
        tree.delete(item)
    for r in rows:
        tree.insert("", "end", values=r)


def select_file_sync(mode="update", tree=None, lbl_file=None, lbl_stats=None):
    """
    mode: "copy" → insert/update only (no deletion)
          "update" → insert/update/delete (full sync)
    """
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    # --- Different warning messages based on mode ---
    if mode == "copy":
        warning_msg = (
            "📥 ADD/UPDATE MODE (Copy Mode)\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "✅ WILL DO:\n"
            "1. Add new products from CSV\n"
            "2. Update existing product data:\n"
            "   • name, description, cost, retail, required_qty\n\n"
            "🔒 WILL NOT:\n"
            "1. Delete any existing products in database\n"
            "2. Modify stored quantities:\n"
            "   • good_qty, gift, damaged_qty, total_qty\n\n"
            "💡 Use this mode to add new products or update prices only.\n\n"
            "⚠️ Make sure you have a backup before proceeding."
        )
    else:  # update mode
        warning_msg = (
            "🔄 FULL SYNC MODE (Update Mode)\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "✅ WILL DO:\n"
            "1. Add new products from CSV\n"
            "2. Update existing product data:\n"
            "   • name, description, cost, retail, required_qty\n"
            "3. Delete products not in CSV:\n"
            "   ⚠️ Will delete ONLY if total_qty = 0\n"
            "   ✅ Will skip deletion if total_qty > 0\n\n"
            "🔒 WILL NOT:\n"
            "• Modify stored quantities:\n"
            "  good_qty, gift, damaged_qty, total_qty\n\n"
            "💡 Use this mode for full catalog synchronization.\n\n"
            "⚠️ Make sure you have a backup before proceeding."
        )

    # --- Ask for confirmation ---
    confirm = messagebox.askokcancel(
        f"⚠️ Confirm Operation - {mode.upper()}",
        warning_msg,
        icon="warning"
    )
    if not confirm:
        messagebox.showinfo("Operation Cancelled", "❌ Operation was cancelled.")
        return

    if lbl_file:
        lbl_file.config(text=file_path)
    
    inserted, updated, deleted, skipped, errors, result_rows = sync_csv_to_db(file_path, mode)

    stats_text = f"🆕 Inserted: {inserted} | 🔁 Updated: {updated}"
    if mode == "update":
        stats_text += f" | 🗑️ Deleted: {deleted} | ⏭️ Skipped: {skipped}"
    stats_text += f" | ⚠️ Errors: {errors}"
    
    if lbl_stats:
        lbl_stats.config(text=stats_text)
    
    if tree:
        refresh_tree(tree, result_rows)

    # --- Result message ---
    result_msg = f"✅ Operation completed successfully.\n\n🆕 Inserted: {inserted}\n🔁 Updated: {updated}\n"
    if mode == "update":
        result_msg += f"🗑️ Deleted: {deleted}\n⏭️ Skipped: {skipped}\n"
    result_msg += f"⚠️ Errors: {errors}\n\n💡 Tip: Always keep a backup of your database."
    
    messagebox.showinfo("Operation Completed", result_msg)
    
    return inserted, updated, deleted, skipped, errors


#  ------------------ Main Window Function (can be called from other scripts) ------------------ #

def open_csv_manager(parent=None, reload_callback=None): # ✅ إضافة reload_callback    
    create_table()
    
    # 1. استخدام tb.Toplevel / tb.Window
    if parent:
        # ✅ عند وجود نافذة رئيسية (parent)، نستخدم Toplevel فقط
        # هي ترث الثيم من parent تلقائيًا
        root = tb.Toplevel(parent)
    else:
        # إذا تم تشغيله بشكل مستقل (لا يوجد parent)، نبدأ نافذة جديدة بثيم افتراضي
        root = tb.Window(themename="litera") # يمكن تغيير "litera" ليتناسب مع ذوقك
        
    root.title("📦 Inventory CSV Manager")
    root.geometry("800x600")

    # ✅ لا حاجة لإعداد الأنماط يدوياً (مثل style.configure)
    # ❌ تم إزالة: style = ttk.Style() و style.theme_use("clam")

    # 2. استخدام tb.Notebook و tb.Frame
    tab_control = tb.Notebook(root)
    tab_main = tb.Frame(tab_control, padding=10)
    tab_control.add(tab_main, text="📦 Database Management")
    tab_control.pack(expand=1, fill="both", padx=10, pady=10)

    # ----- Title and Description ----- #
    title_frame = tb.Frame(tab_main)
    title_frame.pack(pady=10, fill="x")

    tb.Label(
        title_frame,
        text="📦 Inventory Management from CSV Files",
        font=("Segoe UI", 14, "bold"),
        bootstyle="primary" # استخدام bootstyle بدلاً من foreground
    ).pack()

    tb.Label(
        title_frame,
        text="Choose the appropriate mode based on your needs:",
        font=("Segoe UI", 9),
        bootstyle="secondary" # استخدام bootstyle بدلاً من foreground
    ).pack()

    # ----- Operation Buttons ----- #
    btn_frame = tb.Frame(tab_main)
    btn_frame.pack(pady=10)

    # ----- Display File and Statistics ----- #
    tb.Separator(tab_main, orient="horizontal").pack(fill="x", pady=10)

    lbl_file = tb.Label(tab_main, text="No file selected", bootstyle="info", font=("Segoe UI", 10))
    lbl_file.pack()
    lbl_stats = tb.Label(tab_main, text="", font=("Segoe UI", 10, "bold"))
    lbl_stats.pack(pady=5)

    # ----- Treeview to Display Results ----- #
    frame_tree = tb.Frame(tab_main)
    frame_tree.pack(expand=True, fill="both", pady=10)

    # استخدام tb.Treeview و tb.Scrollbar
    tree_main = tb.Treeview(frame_tree, columns=("index", "code", "status"), show="headings", bootstyle="info")
    tree_main.heading("index", text="#")
    tree_main.heading("code", text="Code")
    tree_main.heading("status", text="Status")
    tree_main.column("index", width=60)
    tree_main.column("code", width=180)
    tree_main.column("status", width=250)
    tree_main.pack(side="left", expand=True, fill="both")
    
    scroll_y = tb.Scrollbar(frame_tree, orient="vertical", command=tree_main.yview)
    tree_main.configure(yscrollcommand=scroll_y.set)
    scroll_y.pack(side="right", fill="y")

    # 3. إعداد الأزرار (مرة واحدة فقط)
    
    # زر Add/Update Only (Copy)
    btn_copy = tb.Button(
        btn_frame,
        text="📥 Add/Update Only (Copy)",
        command=lambda: select_file_sync("copy", tree_main, lbl_file, lbl_stats),
        width=30,
        bootstyle="success" 
    )
    btn_copy.pack(pady=5)

    tb.Label(
        btn_frame,
        text="↑ To add new products or update prices without deletion",
        font=("Segoe UI", 8),
        bootstyle="secondary"
    ).pack()

    # زر Full Sync (Update)
    btn_update = tb.Button(
        btn_frame,
        text="🔄 Full Sync (Update)",
        command=lambda: select_file_sync("update", tree_main, lbl_file, lbl_stats),
        width=30,
        bootstyle="primary" 
    )
    btn_update.pack(pady=5)

    tb.Label(
        btn_frame,
        text="↑ For full synchronization with deletion of old products (quantity protected)",
        font=("Segoe UI", 8),
        bootstyle="secondary"
    ).pack()

    def on_closing():
        if reload_callback:
            reload_callback()
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # 4. إزالة استدعاءات mainloop المكررة وغير الضرورية
    if not parent:
        root.mainloop()
    
    return root
# ------------------ Run standalone if executed directly ------------------ #


if __name__ == "__main__":
    open_csv_manager()