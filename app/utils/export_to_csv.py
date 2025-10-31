from .dp_utils import fetch_products
from tkinter import filedialog, messagebox
import csv

from constants.index import COLUMNS
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

