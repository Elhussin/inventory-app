# copycsb to dat pase

import csv
import sqlite3

# def copy_csv_to_db(csv_file, db_file):
#     conn = sqlite3.connect(db_file)
#     c = conn.cursor()
#     c.execute("DROP TABLE IF EXISTS products")
#     # c.execute()
#     c.execute("""CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,
#     code TEXT,
#     description TEXT,
#     cost REAL,
#     retail REAL,
#     required_qty INTEGER,
#     good_qty INTEGER,
#     damaged_qty INTEGER,
#     total_qty INTEGER
# )""")

        
        
#         # "CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT, code TEXT, description TEXT, cost REAL, retail REAL, required_qty INTEGER, good_qty INTEGER, damaged_qty INTEGER, total_qty INTEGER)")
    
#     with open(csv_file, 'r', encoding='utf-8') as f:
#         reader = csv.reader(f)
#         next(reader)  # Skip header row
        
#         for row in reader:
#             c.execute("INSERT INTO products (name, code,description,cost, retail , required_qty, good_qty, damaged_qty, total_qty) VALUES (?, ?, ?, ?, ?, ?,?,?,?)", row)
    
#     conn.commit()
#     conn.close()

# if __name__ == "__main__":
#     csv_file = "hussam2025.csv"  # Replace with your CSV file path
#     db_file = "inventory.db"  # Replace with your database file path
    
#     copy_csv_to_db(csv_file, db_file)
#     print("CSV data copied to database successfully.")
import csv
import sqlite3

def copy_csv_to_db(csv_file, db_file):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS products")
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
            total_qty INTEGER
        )
    """)

    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
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

    conn.commit()
    conn.close()
    print("✅ CSV data copied successfully.")



if __name__ == "__main__":
    csv_file = "2025.csv"  # Replace with your CSV file path
    db_file = "inventory.db"  # Replace with your database file path
    
    copy_csv_to_db(csv_file, db_file)
    print("CSV data copied to database successfully.")