#!/usr/bin/env python3
# inventory_app_enhanced.py
from logging import disable
import os
import sqlite3
import csv
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER

# -------------------------
# Configuration & Columns
# -------------------------
DB_FILE = "inventory.db"
COLUMNS = [
    "id", "name", "code", "description", "cost", "retail",
    "required_qty", "good_qty", "damaged_qty", "gift", "total_qty", "note"
]


EDITABLE_FIELDS = {"good_qty", "damaged_qty", "gift", "note"}
# تحضير فهرس أول عمود قابل للتعديل (مرة واحدة عند بدء البرنامج)
EDITABLE_INDEXES = [COLUMNS.index(f) for f in COLUMNS if f in EDITABLE_FIELDS]
FIRST_EDITABLE_INDEX = EDITABLE_INDEXES[0] if EDITABLE_INDEXES else 1

NUMERIC_FIELDS = {"cost", "retail", "required_qty", "good_qty", "damaged_qty", "gift", "total_qty"}

# -------------------------
# Database helpers
# -------------------------
def init_db():
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
            damaged_qty INTEGER,
            total_qty INTEGER,
            gift INTEGER,
            note TEXT
        )
    """)
    conn.commit()
    conn.close()

def fetch_products(search_text=""):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if search_text:
        q = f"%{search_text}%"
        c.execute("""
            SELECT * FROM products
            WHERE name LIKE ? OR description LIKE ? OR code LIKE ?
            ORDER BY id ASC
        """, (q, q, q))
    else:
        c.execute("SELECT * FROM products ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()
    return rows

def get_product_by_id(prod_id):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE id=?", (prod_id,))
    row = c.fetchone()
    conn.close()
    return row

def update_product_full(prod_id, name, code, description, cost, retail, required_qty, good_qty, damaged_qty, gift=0, total_qty=None, note=""):
    """
    Update product fields. If total_qty is None it's computed as good+damaged+gift.
    Returns True on success, False on unique-code violation or error.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        if total_qty is None:
            total_qty = (good_qty or 0) + (damaged_qty or 0) + (gift or 0)
        c.execute("""
            UPDATE products
            SET name=?, code=?, description=?, cost=?, retail=?, required_qty=?, good_qty=?, damaged_qty=?, total_qty=?, gift=?, note=?
            WHERE id=?
        """, (name, code, description, cost, retail, required_qty, good_qty, damaged_qty, total_qty, gift, note, prod_id))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception:
        return False

def insert_product(data_tuple):
    """
    data_tuple: (name, code, description, cost, retail, required_qty, good_qty, damaged_qty, total_qty, gift, note)
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
            INSERT INTO products (name, code, description,  good_qty, damaged_qty, total_qty, gift, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, data_tuple)
        conn.commit()
        conn.close()
        return True, "Product added successfully!"
    except sqlite3.IntegrityError:
        return False, "Product code already exists!"
    except Exception as e:
        return False, str(e)

def delete_product(prod_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE id=?", (prod_id,))
    conn.commit()
    conn.close()

def update_product_quantities(prod_id, good_qty_to_add=0, damaged_qty_to_add=0, gift_to_add=0, note_to_add=None):
    """
    Add quantities to existing product. Returns tuple (new_good, new_damaged, new_gift, new_note) or None on failure.
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT good_qty, damaged_qty, gift, note FROM products WHERE id=?", (prod_id,))
    current = c.fetchone()
    if not current:
        conn.close()
        return None
    cur_good = int(current["good_qty"] or 0)
    cur_damaged = int(current["damaged_qty"] or 0)
    cur_gift = int(current["gift"] or 0)
    cur_note = current["note"] or ""
    new_good = cur_good + (good_qty_to_add or 0)
    new_damaged = cur_damaged + (damaged_qty_to_add or 0)
    new_gift = cur_gift + (gift_to_add or 0)
    new_total = new_good + new_damaged + new_gift
    new_note = note_to_add if note_to_add is not None else cur_note
    c.execute("""
        UPDATE products
        SET good_qty=?, damaged_qty=?, total_qty=?, gift=?, note=?
        WHERE id=?
    """, (new_good, new_damaged, new_total, new_gift, new_note, prod_id))
    conn.commit()
    conn.close()
    return new_good, new_damaged, new_gift, new_note

# -------------------------
# UI
# -------------------------
app = tb.Window(title="Inventory Management System", themename="flatly", size=(1400, 800))
root = app

# Colors & Styles
FONT = ("Arial", 11)

# Top Frame (Header)
header = tb.Frame(root, bootstyle="primary")
header.pack(fill="x")
title = tb.Label(header, text="📦 Inventory Management System", font=("Arial", 22, "bold"), bootstyle="inverse")
title.pack(pady=15)

# Top Controls
top_frame = tb.Frame(root)
top_frame.pack(fill="x", padx=15, pady=10)

# Search
search_var = tk.StringVar()
search_lbl = tb.Label(top_frame, text="🔍 Search:", font=FONT)
search_lbl.pack(side=LEFT, padx=(2, 8))
search_entry = tb.Entry(top_frame, textvariable=search_var, width=45, font=FONT)
search_entry.pack(side=LEFT)

def search_products(ev=None):
    load_data(search_var.get())

search_entry.bind("<KeyRelease>", search_products)



def focus_first_row(event=None, start_edit=False):
    """Focus first row in tree. If start_edit True, open editor on first editable column."""
    children = tree.get_children()
    if not children:
        return "break"
    first = children[0]
    tree.selection_set(first)
    tree.focus(first)
    tree.see(first)
    tree.focus_set()  # give keyboard focus to tree

    if start_edit:
        # افتح المحرر على أول عمود قابل للتعديل
        root.after(50, lambda: _open_editor_for_item_column(first, FIRST_EDITABLE_INDEX))
        # التأخير الصغير يضمن أن الـ Treeview استقر بعد تغيير الاختيار
    return "break"

# Bind Tab key to move to tree (and prevent cycling back)

search_entry.bind("<Tab>", lambda e: focus_first_row(e, start_edit=True))
search_entry.bind("<Return>", lambda e: focus_first_row(e, start_edit=True))

# Buttons
btn_frame = tb.Frame(top_frame)
btn_frame.pack(side=RIGHT)

btn_add = tb.Button(btn_frame, text="➕ Add Product", bootstyle="success", command=lambda: open_add_window())
btn_add.pack(side=LEFT, padx=4)

btn_stock = tb.Button(btn_frame, text="📦 Add Stock", bootstyle="info", command=lambda: open_add_stock_window())
btn_stock.pack(side=LEFT, padx=4)

tb.Button(btn_frame, text="📥 Export CSV", bootstyle="primary", command=lambda: export_all_to_csv()).pack(side=LEFT, padx=4)
tb.Button(btn_frame, text="📄 Export PDF", bootstyle="primary", command=lambda: export_all_to_pdf()).pack(side=LEFT, padx=4)
tb.Button(btn_frame, text="⚠️ Mismatch CSV", bootstyle="warning", command=lambda: export_mismatch_to_csv()).pack(side=LEFT, padx=4)
tb.Button(btn_frame, text="⚠️ Mismatch PDF", bootstyle="warning", command=lambda: export_mismatch_to_pdf()).pack(side=LEFT, padx=4)
tb.Button(btn_frame, text="🗑️ Delete", bootstyle="danger", command=lambda: delete_selected()).pack(side=LEFT, padx=4)

# Table & Stats container
container = tb.Frame(root)
container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

# Stats Frame
stats_frame = tb.Frame(container)
stats_frame.pack(fill="x", pady=(0,10))

def create_stat_box(parent, text, color="secondary"):
    frame = tb.Frame(parent, bootstyle=color, padding=10)
    label = tb.Label(frame, text=text, font=("Arial", 11, "bold"), bootstyle=f"{color}-inverse")
    value = tb.Label(frame, text="0", font=("Arial", 14, "bold"), bootstyle=f"{color}-inverse")
    label.pack()
    value.pack()
    return frame, value

stat_req_frame, stat_req_val = create_stat_box(stats_frame, "📋 Total Required", "secondary")
stat_req_frame.pack(side=LEFT, expand=True, fill="x", padx=4)
stat_good_frame, stat_good_val = create_stat_box(stats_frame, "✅ Total Good", "success")
stat_good_frame.pack(side=LEFT, expand=True, fill="x", padx=4)
stat_dam_frame, stat_dam_val = create_stat_box(stats_frame, "❌ Total Damaged", "danger")
stat_dam_frame.pack(side=LEFT, expand=True, fill="x", padx=4)
stat_gift_frame, stat_gift_val = create_stat_box(stats_frame, "🎁 Total Gift", "warning")
stat_gift_frame.pack(side=LEFT, expand=True, fill="x", padx=4)
stat_tot_frame, stat_tot_val = create_stat_box(stats_frame, "📦 Total Stock", "info")
stat_tot_frame.pack(side=LEFT, expand=True, fill="x", padx=4)

# Treeview
columns = tuple(COLUMNS)
tree_frame = tb.Frame(container)
tree_frame.pack(fill="both", expand=True)


tree = tb.Treeview(tree_frame, columns=columns, show="headings", bootstyle="secondary")

# Scrollbars
vsb = tb.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
hsb = tb.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
tree.configure(yscroll=vsb.set, xscroll=hsb.set)
vsb.pack(side="right", fill="y")
hsb.pack(side="bottom", fill="x")
tree.pack(fill="both", expand=True)

# Configure row height
# style = tb.Style()
style = tb.Style(theme="superhero")  # أو "superhero" أو "morph"
# style.configure("Treeview", rowheight=200)
style.configure("Treeview",
                rowheight=50,  # ارتفاع الصف
                font=("Arial", 12, "bold"),
                padding=6)
style.configure("Treeview.Heading",
                font=("Arial", 12, "bold"),
                padding=6)


column_display_names = {
    "id": "ID",
    "name": "Product Name",
    "code": "Code",
    "description": "Description",
    "cost": "Cost",
    "retail": "Retail",
    "required_qty": "Required",
    "good_qty": "Good",
    "damaged_qty": "Damaged",
    "gift": "Gift",
    "total_qty": "Total",
    "note": "Note"
}

# Row styles
tree.tag_configure('evenrow', background='#e7e7e7', font=("Arial", 11) ,foreground='#000')
tree.tag_configure('oddrow', background='#ffffff', font=("Arial", 11) ,foreground='#000')

# Set headings and column widths based on content
for col in columns:
    tree.heading(col, text=column_display_names.get(col, col))
    # Dynamic column widths
    if col == "id":
        tree.column(col, width=70, minwidth=50, anchor="center", stretch=False, )
    elif col == "description":
        tree.column(col, width=250, minwidth=150, anchor="w", stretch=True)
    elif col == "name":
        tree.column(col, width=150, minwidth=120, anchor="w", stretch=True)
    elif col == "code":
        tree.column(col, width=120, minwidth=80, anchor="center", stretch=False)
    elif col == "note":
        tree.column(col, width=150, minwidth=100, anchor="w", stretch=True)
    elif col in ["cost", "retail"]:
        tree.column(col, width=100, minwidth=80, anchor="center", stretch=False)
    else:
        tree.column(col, width=100, minwidth=70, anchor="center", stretch=False)


# -------------------------
# Load / Insert helper
# -------------------------
def _format_cell_value(col, val):
    if val is None:
        val = ""
    if col in ("cost", "retail"):
        try:
            return f"{float(val):.2f}"
        except Exception:
            return "0.00"
    return val

def load_data(search=""):
    tree.delete(*tree.get_children())
    total_required = total_good = total_damaged = total_gift = total_stock = 0
    rows = fetch_products(search)
    for idx, r in enumerate(rows):
        tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
        values = tuple(_format_cell_value(col, r[col]) for col in COLUMNS)
        tree.insert("", "end", values=values, tags=(tag,))
        total_required += int(r["required_qty"] or 0)
        total_good += int(r["good_qty"] or 0)
        total_damaged += int(r["damaged_qty"] or 0)
        total_gift += int(r["gift"] or 0)
        total_stock += int(r["total_qty"] or 0)
    stat_req_val.config(text=f"{total_required:,}")
    stat_good_val.config(text=f"{total_good:,}")
    stat_dam_val.config(text=f"{total_damaged:,}")
    stat_gift_val.config(text=f"{total_gift:,}")
    stat_tot_val.config(text=f"{total_stock:,}")

load_data()

# -------------------------
# Cell Editing Helpers
# -------------------------
_edit_entry = None


def _open_editor_for_item_column(item, col_index):
    """Open editor for given tree item and column index (0-based). Robust with checks."""
    # تأكد العنصر لا زال موجوداً
    if item not in tree.get_children():
        return

    column_id = f"#{col_index + 1}"
    # protect bbox call
    try:
        bbox = tree.bbox(item, column_id)
    except tk.TclError:
        return
    if not bbox:
        return

    global _edit_entry
    # destroy previous editor if موجود
    if _edit_entry:
        try:
            _edit_entry.destroy()
        except Exception:
            pass
        _edit_entry = None

    # لا نحرر العمود الأول (ID) على أي حال
    if column_id == "#1":
        return

    x, y, width, height = bbox
    # enlarge editor a bit for better UX
    pad_w, pad_h = 12,12
    entry = tb.Entry(tree, font=("Arial", 13), bootstyle="info")
    entry.place(x=x - pad_w//2, y=y - pad_h//2, width=width + pad_w, height=height + pad_h)
    value = tree.item(item, "values")[col_index]
    entry.insert(0, value)
    entry.focus()
    entry.select_range(0, tk.END)

    def save_and_move(next_on_tab=True):
        """Save current editor value and optionally move to next editable cell."""
        nonlocal entry
        new_raw = entry.get().strip()
        field_name = COLUMNS[col_index]

        # Validation for numeric fields
        if field_name in NUMERIC_FIELDS:
            try:
                if field_name in {"cost", "retail"}:
                    new_val = float(new_raw) if new_raw != "" else 0.0
                    new_raw = f"{new_val:.2f}"
                else:
                    new_val = int(float(new_raw)) if new_raw != "" else 0
                    new_raw = str(new_val)
            except ValueError:
                messagebox.showerror("Invalid Input", f"Please enter a valid number for '{field_name}'.")
                entry.focus()
                return False

        # update tree view row values (in-memory)
        values = list(tree.item(item, "values"))
        values[col_index] = new_raw
        tree.item(item, values=values)

        # update DB: build pd (use existing values)
        pd = {}
        for i, col in enumerate(COLUMNS):
            v = values[i]
            if col in ("cost", "retail"):
                try:
                    pd[col] = float(v) if v not in ("", None) else 0.0
                except Exception:
                    pd[col] = 0.0
            elif col in ("required_qty", "good_qty", "damaged_qty", "gift", "total_qty"):
                try:
                    pd[col] = int(float(v)) if v not in ("", None) and v != "" else 0
                except Exception:
                    pd[col] = 0
            else:
                pd[col] = v

        # recompute total if needed
        pd["total_qty"] = int(pd.get("good_qty", 0)) + int(pd.get("damaged_qty", 0)) + int(pd.get("gift", 0))

        ok = update_product_full(
            pd["id"], pd["name"], pd["code"], pd["description"],
            pd["cost"], pd["retail"],
            pd["required_qty"], pd["good_qty"], pd["damaged_qty"],
            pd.get("gift", 0), pd.get("total_qty", None), pd.get("note", "")
        )
        if not ok:
            messagebox.showerror("Update Error", "❌ Update failed - duplicate code or DB error.")
            load_data(search_var.get())
            entry.destroy()
            return False

        entry.destroy()
        # reload to reflect formatting & summaries
        root.after(50, lambda: load_data(search_var.get()))

        if next_on_tab:
            # move to next editable column in the same row; if none, move to next row's first editable
            cur_row_children = tree.get_children()
            try:
                idx_row = cur_row_children.index(item)
            except ValueError:
                return True
            # find next editable column index after current
            editable_after = [i for i in EDITABLE_INDEXES if i > col_index]
            if editable_after:
                next_col = editable_after[0]
                # open after short delay to allow reload
                root.after(120, lambda: _open_editor_for_item_column(item, next_col))
            else:
                # move to next row (wrap)
                next_row_idx = idx_row + 1
                if next_row_idx >= len(cur_row_children):
                    next_row_idx = 0
                next_item = cur_row_children[next_row_idx]
                root.after(120, lambda: _open_editor_for_item_column(next_item, FIRST_EDITABLE_INDEX))
        return True

    def on_return(e=None):
        save_and_move(next_on_tab=False)
        return "break"

    def on_tab(e=None):
        save_and_move(next_on_tab=True)
        return "break"

    def on_focus_out(e=None):
        # Save when focus leaves editor (but don't advance)
        save_and_move(next_on_tab=False)

    entry.bind("<Return>", on_return)
    entry.bind("<Tab>", on_tab)
    entry.bind("<FocusOut>", on_focus_out)
    entry.bind("<Escape>", lambda e: entry.destroy())

    _edit_entry = entry


# Double click handler
def on_double_click(event):
    item = tree.identify_row(event.y)
    column = tree.identify_column(event.x)
    if not item or not column:
        return
    col_index = int(column.replace("#", "")) - 1
    field_name = COLUMNS[col_index]
    if field_name not in EDITABLE_FIELDS:
        return
    _open_editor_for_item_column(item, col_index)

tree.bind("<Double-1>", on_double_click)

# Keyboard navigation

def on_tree_key(event):
    sel = tree.selection()
    if not sel:
        return
    current = sel[0]

    if event.keysym in ("Up", "Down"):
        if event.keysym == "Up":
            prev_item = tree.prev(current)
            if prev_item:
                tree.selection_set(prev_item)
                tree.focus(prev_item)
                tree.see(prev_item)
        else:
            nxt = tree.next(current)
            if nxt:
                tree.selection_set(nxt)
                tree.focus(nxt)
                tree.see(nxt)
        return "break"

    elif event.keysym in ("Return",):
        # افتح المحرر على أول عمود قابل للتعديل في هذا الصف
        _open_editor_for_item_column(current, FIRST_EDITABLE_INDEX)
        return "break"

    elif event.keysym == "F2":
        # افتح المحرر على عمود الـ name لو تريد، لكن يجب أن يكون قابلاً للتعديل
        # سنفتح على أول عمود قابل للتعديل أيضاً (اتساق)
        _open_editor_for_item_column(current, FIRST_EDITABLE_INDEX)
        return "break"

tree.bind("<Up>", on_tree_key)
tree.bind("<Down>", on_tree_key)
tree.bind("<Return>", on_tree_key)
tree.bind("<F2>", on_tree_key)


# Prevent Tab from cycling back from tree to search
def tree_tab_handler(event):
    """Override Tab behavior in tree to stay within tree"""
    return "break"

tree.bind("<Tab>", tree_tab_handler)

# -------------------------
# Windows
# -------------------------
def delete_selected():
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Select", "⚠️ الرجاء تحديد منتج أولاً.")
        return
    item = sel[0]
    vals = tree.item(item, "values")
    prod_id = vals[0]
    prod_name = vals[1]
    prod_code = vals[2]
    if messagebox.askyesno("Delete", f"Are you sure you want to delete:\n{prod_name} ({prod_code}) ?"):
        delete_product(prod_id)
        load_data(search_var.get())
        messagebox.showinfo("Deleted", "✅ Product deleted successfully.")

def open_add_stock_window():
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Select", "⚠️ Please select a product first.")
        return
    item = sel[0]
    vals = tree.item(item, "values")
    prod_id = vals[0]
    prod_name = vals[1]
    cur_good = int(vals[7] or 0)
    cur_damaged = int(vals[8] or 0)

    win = tb.Toplevel(root)
    win.title("Add Stock")
    win.geometry("450x550")
    win.transient(root)
    win.grab_set()

    # Header
    header_frame = tb.Frame(win, bootstyle="info")
    header_frame.pack(fill="x")
    tb.Label(header_frame, text="📦Add Stock ", font=("Arial", 18, "bold"), bootstyle="inverse").pack(pady=12)

    # Info
    info_frame = tb.Frame(win, padding=15)
    info_frame.pack(fill="x")
    tb.Label(info_frame, text=f"Product: {prod_name}", font=("Arial", 13, "bold")).pack(anchor="w", pady=4)
    tb.Label(info_frame, text=f"Current Good: {cur_good} | Damaged: {cur_damaged}", 
             font=("Arial", 11)).pack(anchor="w", pady=4)

    # Form
    form = tb.Frame(win, padding=15)
    form.pack(fill="both", expand=True)

    tb.Label(form, text="Good Stock:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(8,2))
    good_e = tb.Entry(form, font=FONT)
    good_e.pack(fill="x", pady=(0,8))
    good_e.insert(0, "0")
    good_e.focus()

    tb.Label(form, text="Damaged Stock:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(8,2))
    damaged_e = tb.Entry(form, font=FONT)
    damaged_e.pack(fill="x", pady=(0,8))
    damaged_e.insert(0, "0")

    tb.Label(form, text="Gift Stock:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(8,2))
    gift_e = tb.Entry(form, font=FONT)
    gift_e.pack(fill="x", pady=(0,8))
    gift_e.insert(0, "0")

    tb.Label(form, text="Note (optional):", font=("Arial", 11, "bold")).pack(anchor="w", pady=(8,2))
    note_e = tb.Entry(form, font=FONT)
    note_e.pack(fill="x", pady=(0,8))

    def add_stock_action():
        try:
            g = int(float(good_e.get() or 0))
            d = int(float(damaged_e.get() or 0))
            gf = int(float(gift_e.get() or 0))
            note = note_e.get().strip() or None
            
            if g < 0 or d < 0 or gf < 0:
                messagebox.showerror("Error", "Quantities cannot be negative.")
                return
            if g == 0 and d == 0 and gf == 0:
                messagebox.showwarning("Warning", "Please enter at least one quantity.")
                return
                
            res = update_product_quantities(prod_id, g, d, gf, note)
            if not res:
                messagebox.showerror("Error", "Failed to add stock.")
                return
                
            new_good, new_damaged, new_gift, new_note = res
            win.destroy()
            load_data(search_var.get())
            messagebox.showinfo("Success", 
                f"✅ Stock added successfully!\n\n"
                f"New Good Stock: {new_good}\n"
                f"New Damaged Stock: {new_damaged}\n"
                f"New Gift Stock: {new_gift}\n"
                f"New Total Stock: {new_good + new_damaged + new_gift}")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values.")

    # Buttons
    btnf = tb.Frame(form)
    btnf.pack(pady=15)
    save_btn = tb.Button(btnf, text="✅ Save", bootstyle="success", command=add_stock_action)
    save_btn.pack(side=LEFT, padx=6)
    cancel_btn = tb.Button(btnf, text="❌ Cancel", bootstyle="danger", command=win.destroy)
    cancel_btn.pack(side=LEFT, padx=6)

    # Tab navigation - Fixed
    def focus_next_widget(event, next_widget):
        next_widget.focus()
        return "break"

    good_e.bind("<Tab>", lambda e: focus_next_widget(e, damaged_e))
    good_e.bind("<Return>", lambda e: focus_next_widget(e, damaged_e))
    
    damaged_e.bind("<Tab>", lambda e: focus_next_widget(e, gift_e))
    damaged_e.bind("<Return>", lambda e: focus_next_widget(e, gift_e))
    
    gift_e.bind("<Tab>", lambda e: focus_next_widget(e, note_e))
    gift_e.bind("<Return>", lambda e: focus_next_widget(e, note_e))
    
    note_e.bind("<Tab>", lambda e: focus_next_widget(e, save_btn))
    note_e.bind("<Return>", lambda e: (add_stock_action(), "break")[1])
    
    # Escape to cancel
    win.bind("<Escape>", lambda e: win.destroy())

def open_add_window():
    win = tb.Toplevel(root)
    win.title("Add New Product")
    win.geometry("500x650")
    win.transient(root)
    win.grab_set()

    # Header
    header_frame = tb.Frame(win, bootstyle="success")
    header_frame.pack(fill="x")
    tb.Label(header_frame, text="➕ Add New Product", font=("Arial", 18, "bold"), bootstyle="inverse").pack(pady=12)
    tb.Scrollbar(win, command=tree.yview).pack(side="right", fill="y")

    # Form
    form = tb.Frame(win, padding=15)
    form.pack(fill="both", expand=True)

    fields = [
        ("name", "Product Name *"),
        ("code", "Product Code *"),
        ("description", "Description"),
        ("good_qty", "Good Quantity"),
        ("damaged_qty", "Damaged Quantity"),
        ("gift", "Gift Quantity"),
        ("note", "Note")
    ]
    
    entries = {}
    entry_list = []
    
    for key, label in fields:
        tb.Label(form, text=label, font=("Arial", 11, "bold")).pack(anchor="w", pady=(8,2))
        e = tb.Entry(form, font=FONT)
        e.pack(fill="x", pady=(0,4))
        entries[key] = e
        entry_list.append(e)

    # Set default values
    entries["good_qty"].insert(0, "0")
    entries["damaged_qty"].insert(0, "0")
    entries["gift"].insert(0, "0")
    
    # Focus on first field
    entries["name"].focus()
    
    # Required note
    tb.Label(form, text="* Required fields", font=("Arial", 9, "italic"), bootstyle="danger").pack(anchor="w", pady=8)

    def add_action():
        try:
            name = entries["name"].get().strip()
            code = entries["code"].get().strip()
            
            if not name:
                messagebox.showerror("Error", "Product name is required!")
                entries["name"].focus()
                return
            if not code:
                messagebox.showerror("Error", "Product code is required!")
                entries["code"].focus()
                return
                
            description = entries["description"].get().strip()
            # cost = float(entries["cost"].get() or 0.0)
            # retail = float(entries["retail"].get() or 0.0)
            # required_qty = int(float(entries["required_qty"].get() or 0))
            good_qty = int(float(entries["good_qty"].get() or 0))
            damaged_qty = int(float(entries["damaged_qty"].get() or 0))
            gift = int(float(entries["gift"].get() or 0))
            note = entries["note"].get().strip()

            total_qty = good_qty + damaged_qty + gift
            data = (name, code, description, good_qty, damaged_qty, total_qty, gift, note)
            
            ok, msg = insert_product(data)
            if not ok:
                messagebox.showerror("Error", f"❌ {msg}")
                return
                
            win.destroy()
            load_data()
            messagebox.showinfo("Success", "✅ Product added successfully.")
        except ValueError as e:
            messagebox.showerror("Error", f"Please enter valid numeric values.\n{e}")

    # Buttons
    btnf = tb.Frame(form)
    btnf.pack(pady=15)
    save_btn = tb.Button(btnf, text="💾 Save", bootstyle="success", command=add_action)
    save_btn.pack(side=LEFT, padx=6)
    cancel_btn = tb.Button(btnf, text="❌ Cancel", bootstyle="danger", command=win.destroy)
    cancel_btn.pack(side=LEFT, padx=6)

    # Tab navigation between fields
    def setup_tab_navigation():
        for i in range(len(entry_list)):
            if i < len(entry_list) - 1:
                # Tab moves to next field
                entry_list[i].bind("<Tab>", lambda e, idx=i: (entry_list[idx + 1].focus(), "break")[1])
                entry_list[i].bind("<Return>", lambda e, idx=i: (entry_list[idx + 1].focus(), "break")[1])
            else:
                # Last field tabs to save button
                entry_list[i].bind("<Tab>", lambda e: (save_btn.focus(), "break")[1])
                entry_list[i].bind("<Return>", lambda e: (add_action(), "break")[1])
    
    setup_tab_navigation()
    
    # Escape to cancel
    win.bind("<Escape>", lambda e: win.destroy())

# -------------------------
# Export functions
# -------------------------
def export_all_to_csv():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
    if not file_path:
        return
    rows = fetch_products()
    with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNS)
        for r in rows:
            writer.writerow([r[col] for col in COLUMNS])
    messagebox.showinfo("Success", f"✅ CSV exported to:\n{file_path}")

def export_mismatch_to_csv():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
    if not file_path:
        return
    rows = fetch_products()
    mismatched = [r for r in rows if int(r["required_qty"] or 0) != int(r["total_qty"] or 0)]
    if not mismatched:
        messagebox.showinfo("Success", "ℹ️ No mismatched products found.")
        return
    with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNS + ["variance"])
        for r in mismatched:
            variance = int(r["total_qty"] or 0) - int(r["required_qty"] or 0)
            writer.writerow([r[col] for col in COLUMNS] + [variance])
    messagebox.showinfo("Success", f"✅ CSV exported to:\n{file_path}")

def export_all_to_pdf():
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
    if not file_path:
        return
    rows = fetch_products()
    try:
        doc = SimpleDocTemplate(file_path, pagesize=landscape(A4))
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=20, textColor=colors.HexColor('#2c3e50'))
        elements.append(Paragraph("📦 Complete Inventory Report", title_style))
        elements.append(Spacer(1, 12))
        
        # Date
        subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], alignment=TA_CENTER, fontSize=11, textColor=colors.HexColor('#7f8c8d'))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style))
        elements.append(Spacer(1, 18))

        # Summary totals
        total_required = sum(int(r["required_qty"] or 0) for r in rows)
        total_good = sum(int(r["good_qty"] or 0) for r in rows)
        total_damaged = sum(int(r["damaged_qty"] or 0) for r in rows)
        total_gift = sum(int(r["gift"] or 0) for r in rows)
        total_stock = sum(int(r["total_qty"] or 0) for r in rows)
        
        summary_table = Table([
            ["Summary", "Required", "Good", "Damaged", "Gift", "Total Stock"],
            ["Totals", f"{total_required:,}", f"{total_good:,}", f"{total_damaged:,}", f"{total_gift:,}", f"{total_stock:,}"]
        ], colWidths=[2*inch, 1.3*inch, 1.3*inch, 1.3*inch, 1.3*inch, 1.3*inch])
        
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 11),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('TOPPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#ecf0f1')),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,1), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#bdc3c7'))
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 22))

        # Data table
        headers = ['ID','Name','Code','Description','Cost','Retail','Required','Good','Damaged','Gift','Total','Note']
        data = [headers]
        
        for r in rows:
            data.append([
                str(r["id"]), 
                str(r["name"])[:22], 
                str(r["code"]), 
                (str(r["description"])[:32] if r["description"] else ""),
                f"${float(r['cost'] or 0):.2f}", 
                f"${float(r['retail'] or 0):.2f}",
                str(int(r["required_qty"] or 0)), 
                str(int(r["good_qty"] or 0)), 
                str(int(r["damaged_qty"] or 0)),
                str(int(r["gift"] or 0)), 
                str(int(r["total_qty"] or 0)), 
                str(r["note"] or "")[:20]
            ])
            
        col_widths = [0.4*inch, 1.5*inch, 0.9*inch, 1.7*inch, 0.75*inch, 0.75*inch, 0.85*inch, 0.65*inch, 0.85*inch, 0.65*inch, 0.65*inch, 1.3*inch]
        table = Table(data, colWidths=col_widths, repeatRows=1)
        
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('BOTTOMPADDING', (0,0), (-1,0), 10),
            ('TOPPADDING', (0,0), (-1,0), 10),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 8),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#bdc3c7')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 18))
        
        # Footer
        footer_style = ParagraphStyle('Footer', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8, textColor=colors.HexColor('#7f8c8d'))
        footer = Paragraph(f"Total Products: {len(rows)} | © {datetime.now().year} Inventory Management System", footer_style)
        elements.append(footer)
        
        doc.build(elements)
        messagebox.showinfo("Success", f"✅ PDF exported to:\n{file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"❌ An error occurred while creating PDF:\n{str(e)}")

def export_mismatch_to_pdf():
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
    if not file_path:
        return
    rows = fetch_products()
    mismatched = [r for r in rows if int(r["required_qty"] or 0) != int(r["total_qty"] or 0)]
    
    if not mismatched:
        messagebox.showinfo("لا يوجد اختلاف", "ℹ️ لم يتم العثور على منتجات غير متطابقة.")
        return
        
    try:
        doc = SimpleDocTemplate(file_path, pagesize=landscape(A4))
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=20, textColor=colors.HexColor('#e74c3c'))
        elements.append(Paragraph("⚠️ Mismatched Inventory Report", title_style))
        elements.append(Spacer(1, 12))
        
        # Date & Warning
        subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], alignment=TA_CENTER, fontSize=11, textColor=colors.HexColor('#7f8c8d'))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style))
        elements.append(Spacer(1, 12))
        
        warning_style = ParagraphStyle('Warning', parent=styles['Normal'], alignment=TA_CENTER, fontSize=11, textColor=colors.HexColor('#e74c3c'), fontName='Helvetica-Bold')
        warning = Paragraph(f"⚠️ {len(mismatched)} products have quantity mismatches (Required ≠ Total)", warning_style)
        elements.append(warning)
        elements.append(Spacer(1, 18))

        # Data table
        data = [["ID","Name","Code","Description","Required","Good","Damaged","Gift","Total","Variance"]]
        
        for r in mismatched:
            req = int(r["required_qty"] or 0)
            tot = int(r["total_qty"] or 0)
            variance = tot - req
            data.append([
                str(r["id"]), 
                str(r["name"])[:22], 
                str(r["code"]), 
                (str(r["description"])[:35] if r["description"] else ""),
                str(req), 
                str(int(r["good_qty"] or 0)), 
                str(int(r["damaged_qty"] or 0)), 
                str(int(r["gift"] or 0)), 
                str(tot), 
                f"{variance:+d}"
            ])
            
        col_widths = [0.4*inch, 1.6*inch, 0.9*inch, 2*inch, 0.9*inch, 0.75*inch, 0.9*inch, 0.7*inch, 0.75*inch, 0.85*inch]
        table = Table(data, colWidths=col_widths, repeatRows=1)
        
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('BOTTOMPADDING', (0,0), (-1,0), 10),
            ('TOPPADDING', (0,0), (-1,0), 10),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 8),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#bdc3c7')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
            # Highlight variance column
            ('BACKGROUND', (9,1), (9,-1), colors.HexColor('#fff3cd')),
            ('TEXTCOLOR', (9,1), (9,-1), colors.HexColor('#856404')),
            ('FONTNAME', (9,1), (9,-1), 'Helvetica-Bold'),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 18))
        
        # Footer
        footer_style = ParagraphStyle('Footer', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8, textColor=colors.HexColor('#7f8c8d'))
        footer = Paragraph(f"Mismatched Products: {len(mismatched)} | © {datetime.now().year} Inventory Management System", footer_style)
        elements.append(footer)
        
        doc.build(elements)
        messagebox.showinfo("تم التصدير", f"✅ تم تصدير PDF للمنتجات غير المتطابقة إلى:\n{file_path}")
    except Exception as e:
        messagebox.showerror("خطأ في التصدير", f"❌ حدث خطأ أثناء إنشاء PDF:\n{str(e)}")

# -------------------------
# Footer
# -------------------------
footer = tb.Frame(root, bootstyle="primary")
footer.pack(fill="x", side=BOTTOM)
footer_label = tb.Label(footer, text=f"© {datetime.now().year} Inventory Management System - All Rights Reserved", 
                        font=("Arial", 9), bootstyle="inverse")
footer_label.pack(pady=8)

# -------------------------
# Init DB & Run
# -------------------------
init_db()
root.mainloop()