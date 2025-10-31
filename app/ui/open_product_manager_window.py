

# window_manager.py
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import sqlite3
from app.constants.index import column_display_names as COLUMNS_DATA, EDITABLE_FIELDS
from app.utils.data_handlers import fetch_products, fetch_product_by_id, update_product_full

# ------------------
#  define the main window function
# ------------------
def open_product_manager_window(root, load_data_func, main_tree, search_term, stat_vars):
    win = tb.Toplevel(root)
    win.title("📦 Manage Products")
    win.geometry("900x700")
    win.transient(root)
    win.grab_set()

    # Variables
    current_product_id = tk.StringVar(win, value="")  # Current Product ID
    search_var = tk.StringVar(win)  # Search Variable
    entries_vars = {col: tk.StringVar(win) for col in COLUMNS_DATA}

    # ------------------
    # 1. Mini Search Frame
    # ------------------
    search_frame = tb.Frame(win, padding=10)
    search_frame.pack(fill="x")

    tb.Label(search_frame, text="Search by Des/code:", bootstyle="primary").pack(side="right", padx=5)
    search_entry = tb.Entry(search_frame, textvariable=search_var, bootstyle="info")
    search_entry.pack(side="right", fill="x", expand=True, padx=10)

    # Mini Treeview
    mini_tree = tb.Treeview(
        win,
        columns=list(COLUMNS_DATA.keys()),
        show="headings",
        height=8,
        bootstyle="info",
    )
    for col, title in COLUMNS_DATA.items():
        col_width = 100 if col in ["code", "description"] else 45
        mini_tree.column(col, width=col_width, anchor="center")
        mini_tree.heading(col, text=title)
    mini_tree.pack(fill="x", padx=10, pady=5)

    # ------------------
    # 2. Details Frame (Improved layout)
    # ------------------
    details_frame = tb.Frame(win, padding=10)
    details_frame.pack(fill="both", expand=True)


    header_fields = [("description", "code")]  # Group fields that should be in the same row

    for row_idx, field_group in enumerate(header_fields):
        for col_idx, field in enumerate(field_group):
            tb.Label(details_frame, text=COLUMNS_DATA[field], width=15, anchor="e").grid(
                row=row_idx, column=col_idx*2, padx=5, pady=5, sticky="e"
            )
            entry = tb.Entry(details_frame, textvariable=entries_vars[field], width=35)  # Reduced width to fit
            entry.grid(row=row_idx, column=col_idx*2+1, padx=5, pady=5, sticky="w")
            entry.config(state="readonly")

    display_fields = [
        ("required_qty", "good_qty"),  # First row
        ("damaged_qty", "gift"),       # Second row
        ("note",)                      # Third row (single field)
    ]

    start_row = len(header_fields)

    for row_idx, field_group in enumerate(display_fields):
        for col_idx, field in enumerate(field_group):
            tb.Label(details_frame, text=COLUMNS_DATA[field], width=15, anchor="e").grid(
                row=start_row + row_idx, column=col_idx*2, padx=5, pady=5, sticky="e"
            )
            entry = tb.Entry(details_frame, textvariable=entries_vars[field], 
                            width=35)  # Make note field wider
                            #  if field != "note" else 50
            entry.grid(row=start_row + row_idx, column=col_idx*2+1, padx=5, pady=5, sticky="w")
            if field not in EDITABLE_FIELDS:
                entry.config(state="readonly")
    # --- Total Qty (readonly) ---
    tb.Label(details_frame, text="Total Qty:", width=15, anchor="e").grid(
        row=start_row + len(display_fields)-1, column=2, padx=5, pady=5, sticky="e"
    )
    total_label = tb.Label(details_frame, textvariable=entries_vars["total_qty"], bootstyle="danger")
    total_label.grid(row=start_row + len(display_fields)-1, column=3, padx=5, pady=5, sticky="w")

    # ------------------
    # 3. Buttons Frame
    # ------------------
    button_frame = tb.Frame(win, padding=10)
    button_frame.pack(fill="x")

    save_btn = tb.Button(button_frame, text="💾 Save/Add", bootstyle="success", command=lambda: handle_save_update())
    save_btn.pack(side="right", padx=10)

    new_btn = tb.Button(button_frame, text="➕ New (Clear)", bootstyle="info-outline", command=lambda: clear_form_for_new())
    new_btn.pack(side="right", padx=10)

    # ----------------------------------
    # ⚙️ Logic
    # ----------------------------------

    # A. Clear form for new product
    def clear_form_for_new():
        current_product_id.set("New")
        win.title("📦 Manage Products (New Product)")
        for var in entries_vars.values():
            var.set("")
        entries_vars["code"].set("")
        entries_vars["description"].set("")
        entries_vars["total_qty"].set("0")

    # B. Update mini tree
    def update_mini_tree(event=None, *args):
        mini_tree.delete(*mini_tree.get_children())
        search = search_var.get()
        rows = fetch_products(search)

        COLUMNS_KEYS = list(COLUMNS_DATA.keys())

        for idx, r in enumerate(rows):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            values = tuple(r[col] for col in COLUMNS_KEYS)
            mini_tree.insert("", "end", values=values, tags=(tag,))

    search_var.trace_add("write", update_mini_tree)
    search_entry.bind("<Return>", lambda e: mini_tree.focus_set())

    # C. Populate form for edit
    def populate_form_for_edit(event):
        selected_item = mini_tree.focus()
        if not selected_item:
            return

        values = mini_tree.item(selected_item, "values")
        p_id = values[0]

        product_data = fetch_product_by_id(p_id)
        if product_data:
            current_product_id.set(p_id)
            win.title(f"✍️ Edit Product: {product_data['description']}")
            for col in COLUMNS_DATA.keys():

                if col != "id" and col in product_data.keys() and col not in ["good_qty", "gift", "damaged_qty"]:
                    entries_vars[col].set(str(product_data[col]))

    mini_tree.bind("<<TreeviewSelect>>", populate_form_for_edit)

    # D. Save / Update / Merge
    def handle_save_update():
        data = {col: entries_vars[col].get() for col in COLUMNS_DATA if col != "id"}

        if not data["code"]:
            messagebox.showerror("Error", "Code is required.")
            return

        try:
            good = int(float(data.get("good_qty") or 0))
            damaged = int(float(data.get("damaged_qty") or 0))
            gift = int(float(data.get("gift") or 0))
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for quantities.")
            return

        data["good_qty"] = good
        data["damaged_qty"] = damaged
        data["gift"] = gift
        data["total_qty"] = good + damaged + gift
        entries_vars["total_qty"].set(data["total_qty"])

        # 🔍 check if product with same code exists
        conn = sqlite3.connect("inventory.db")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM products WHERE code = ?", (data["code"],))
        existing = cur.fetchone()

        if existing:
            # update quantities
            updated_good = int(existing["good_qty"] or 0) + good
            updated_damaged = int(existing["damaged_qty"] or 0) + damaged
            updated_gift = int(existing["gift"] or 0) + gift
            updated_total = updated_good + updated_damaged + updated_gift

            cur.execute(
                """
                UPDATE products
                SET good_qty=?, damaged_qty=?, gift=?, total_qty=?, note=?, description=?
                WHERE code=?
                """,
                (
                    updated_good,
                    updated_damaged,
                    updated_gift,
                    updated_total,
                    data["note"],
                    data["description"],
                    data["code"],
                ),
            )
            conn.commit()
            messagebox.showinfo("Updated", f"🔁 Updated quantities for product ({data['code']}).")
        else:
            # insert new product
            cur.execute(
                """
                INSERT INTO products 
                (name, code, description, cost, retail, required_qty, good_qty, damaged_qty, gift, total_qty, note)
                VALUES (:name, :code, :description, :cost, :retail, :required_qty, :good_qty, :damaged_qty, :gift, :total_qty, :note)
                """,
                data,
            )
            conn.commit()
            messagebox.showinfo("Success", f"✅ Added new product: {data['description']}")

        conn.close()

        load_data_func(main_tree, search_term.get(), stat_vars)
        update_mini_tree()
        clear_form_for_new()

    # Key bindings
    win.bind("<Escape>", lambda e: win.destroy())
    update_mini_tree()
    clear_form_for_new()

