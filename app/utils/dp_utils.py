import sqlite3
# from constants import DB_FILE
from constants.index import DB_FILE

# -------------------------
# Database helpers
# -------------------------

from tkinter import messagebox

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
    c.execute("SELECT * FROM products WHERE id=?", (prod_id))
    row = c.fetchone()
    conn.close()
    return row


def update_product_full(data_dict): 
    """
    Update product fields. If total_qty is None it's computed as good+damaged+gift.
    Returns True on success, False on unique-code violation or error.
    """

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    try:
        c.execute("""
            UPDATE products SET
                name = ?, code = ?, description = ?, cost = ?, retail = ?,
                required_qty = ?, good_qty = ?, damaged_qty = ?, gift = ?,
                total_qty = ?, note = ?
            WHERE id = ?
        """, (
            data_dict["name"], data_dict["code"], data_dict["description"],
            data_dict["cost"], data_dict["retail"],
            data_dict["required_qty"], data_dict["good_qty"], data_dict["damaged_qty"],
            data_dict["gift"], data_dict["total_qty"], data_dict["note"],
            data_dict["id"] # ID هو مفتاح التحديث
        ))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        
        return False
    except Exception as e:
        # print(f"DB Error during update: {e}")
        return False
    finally:
        conn.close()

def insert_product(data_tuple):
    """
    data_tuple: (name, code, description, cost, retail, required_qty, good_qty, damaged_qty, total_qty, gift, note)
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        # (name, code, description, cost, retail, required_qty, good_qty, damaged_qty, total_qty, gift, note)
        c.execute("""
            INSERT INTO products (name, code, description, cost, retail, required_qty, good_qty, damaged_qty, total_qty, gift, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data_tuple)
        conn.commit()
        conn.close()
        return True, "Product added successfully!"
    except sqlite3.IntegrityError:
        return False, "Product code already exists!"
    except Exception as e:
        return False, str(e)

def delete_product(prod_id):
    if not prod_id:
        messagebox.showerror("Error", "Product ID is required!")
        return False
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("DELETE FROM products WHERE id=?", (prod_id,))  # Note the comma after prod_id
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Error deleting product: {e}")
        return False

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
