
import sqlite3

def add_columns():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    cursor.execute("ALTER TABLE products ADD COLUMN note TEXT")
    cursor.execute("ALTER TABLE products ADD COLUMN gift INTEGER")
    conn.commit()
    conn.close()

add_columns()