import csv
from collections import Counter

def find_duplicate_codes(csv_file):
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        codes = [row.get('code', '').strip() for row in reader if row.get('code')]
    
    # نحسب عدد مرات ظهور كل كود
    duplicates = [code for code, count in Counter(codes).items() if count > 1]
    
    if not duplicates:
        print("✅ no duplicates found")
        return

    print("⚠️ duplicates found:")
    for code in duplicates:
        print(code)

    # لو تحب نعرض تفاصيل كل صف مكرر:
    f.seek(0)
    f.readline()  # تخطي العنوان
    print("\n📄 details of duplicate rows:")
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('code', '').strip() in duplicates:
                print(row)

# 🔸 استدعاء الدالة
find_duplicate_codes("review.csv")
