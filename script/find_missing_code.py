import csv
import sqlite3

DB_FILE = "database.db"
CSV_FILE = "new_products.csv"

def find_missing_codes():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # الأكواد من قاعدة البيانات القديمة
    c.execute("SELECT code FROM products")
    db_codes = {row[0] for row in c.fetchall()}

    # الأكواد من الملف الجديد
    with open(CSV_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        csv_codes = {row.get('code', '').strip() for row in reader if row.get('code')}

    # الأكواد الموجودة في القاعدة لكن غير موجودة في الملف الجديد
    missing = db_codes - csv_codes

    conn.close()

    print(f"عدد الأكواد المفقودة: {len(missing)}")
    for code in sorted(missing):
        print(code)


find_missing_codes()
