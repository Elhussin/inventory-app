
from tkinter import messagebox
from app.utils.dp_utils import delete_product



def delete_selected(tree, load_data_func, search_term, stat_vars):
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Select", "Please select a product first.")
        return
    item = sel[0]
    vals = tree.item(item, "values")
    prod_id = vals[0]
    prod_name = vals[1]
    prod_code = vals[2]
    if messagebox.askyesno("Delete", f"Are you sure you want to delete:\n{prod_name} ({prod_code}) ?"):
        delete_product(prod_id)
        load_data_func(tree, search_term, stat_vars)
        messagebox.showinfo("Deleted", "✅ Product deleted successfully.")
