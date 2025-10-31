# cell_editor.py
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb
from utils.dp_utils import update_product_full

from constants.index import COLUMNS,NUMERIC_FIELDS

_edit_entry = None

def _open_editor_for_item_column(tree, root, item, col_index, EDITABLE_INDEXES, FIRST_EDITABLE_INDEX, load_data_func, search_var, stat_vars):
    """Open editor for given tree item and column index (0-based)."""
    global _edit_entry
    
    if item not in tree.get_children(): return
    column_id = f"#{col_index + 1}"
    try:
        bbox = tree.bbox(item, column_id)
    except tk.TclError: return
    if not bbox: return
    if column_id == "#1": return # لا نحرر ID

    if _edit_entry: 
        try: _edit_entry.destroy()
        except Exception: pass
        _edit_entry = None

    x, y, width, height = bbox
    pad_w, pad_h = 12, 12
    entry = tb.Entry(tree, font=("Arial", 13), bootstyle="info")
    entry.place(x=x - pad_w//2, y=y - pad_h//2, width=width + pad_w, height=height + pad_h)
    value = tree.item(item, "values")[col_index]
    entry.insert(0, value)
    entry.focus()
    entry.select_range(0, tk.END)

    def save_and_move(next_on_tab=True):
        nonlocal entry
        new_raw = entry.get().strip()
        field_name = COLUMNS[col_index]
        print("col_index",col_index)
        print("field_name",field_name)

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

        pd = {}
        for i, col in enumerate(COLUMNS):
            v_raw = values[i] # القيمة في الصف، والتي قد تكون جديدة أو قديمة
                        
            # 🟢 التأكد من تحويل جميع القيم إلى النوع الصحيح قبل التخزين في القاموس
            if col == "id":
                pd[col] = int(v_raw)
            elif col in ("cost", "retail"): 
                pd[col] = float(v_raw) if v_raw not in ("", None) else 0.0
            elif col in ("required_qty", "good_qty", "damaged_qty", "gift"):
                # نستخدم int(float(v)) للتعامل مع أي أرقام عشرية قد تدخل خطأ
                pd[col] = int(float(v_raw)) if v_raw not in ("", None) and v_raw != "" else 0
            else: 
                pd[col] = v_raw
        
        # 🟢 إعادة حساب total_qty
        pd["total_qty"] = pd.get("good_qty", 0) + pd.get("damaged_qty", 0) + pd.get("gift", 0)

        # 🟢 استدعاء دالة التحديث باستخدام القاموس الموحد
        ok = update_product_full(pd) # ⬅️ هنا التعديل
        
        if not ok:
            messagebox.showerror("Update Error", "❌ Update failed - duplicate code or DB error.")
            load_data_func(tree, search_var.get(), stat_vars)
            entry.destroy()
            return False

        entry.destroy()
        # reload to reflect formatting & summaries
        root.after(50, lambda: load_data_func(tree, search_var.get(), stat_vars))

        if next_on_tab:
            try: idx_row = tree.get_children().index(item)
            except ValueError: return True
            
            editable_after = [i for i in EDITABLE_INDEXES if i > col_index]
            if editable_after:
                next_col = editable_after[0]
                root.after(120, lambda: _open_editor_for_item_column(tree, root, item, next_col, EDITABLE_INDEXES, FIRST_EDITABLE_INDEX, load_data_func, search_var, stat_vars))
            else:
                cur_row_children = tree.get_children()
                next_row_idx = (idx_row + 1) % len(cur_row_children)
                next_item = cur_row_children[next_row_idx]
                root.after(120, lambda: _open_editor_for_item_column(tree, root, next_item, FIRST_EDITABLE_INDEX, EDITABLE_INDEXES, FIRST_EDITABLE_INDEX, load_data_func, search_var, stat_vars))
        return True

    entry.bind("<Return>", lambda e: save_and_move(next_on_tab=False) or "break")
    entry.bind("<Tab>", lambda e: save_and_move(next_on_tab=True) or "break")
    entry.bind("<FocusOut>", lambda e: save_and_move(next_on_tab=False))
    entry.bind("<Escape>", lambda e: entry.destroy() and "break")
    
    _edit_entry = entry


def tree_tab_handler(event):
    """Override Tab behavior in tree to stay within tree"""
    return "break"




class CellEditorState:
    def __init__(self):
        self.current_item = None
        self.current_col = None

def setup_tree_bindings(tree, root,EDITABLE_FIELDS, FIRST_EDITABLE_INDEX, EDITABLE_INDEXES, load_data_func, search_var, stat_vars):
    state = CellEditorState()
    
    def handle_edit_cell(event=None, item=None, col_index=None):
        if item is None or col_index is None:
            item, col_index = state.current_item, state.current_col
            if item is None or col_index is None:
                return
                
        _open_editor_for_item_column(
            tree, root, 
            item, col_index, EDITABLE_INDEXES, 
            FIRST_EDITABLE_INDEX, load_data_func, search_var, stat_vars
        )
    
    # Store the edit state when double-clicking
    def on_double_click(event):
        item = tree.identify_row(event.y)
        column = tree.identify_column(event.x)
        if not item or not column: 
            return
        col_index = int(column.replace("#", "")) - 1
        field_name = COLUMNS[col_index]
        if field_name in EDITABLE_FIELDS:
            state.current_item = item
            state.current_col = col_index
            handle_edit_cell()
    
    # Store the edit state when pressing Return/F2
    def on_tree_key(event):
        if event.keysym in ("Return", "F2"):
            sel = tree.selection()
            if sel:
                state.current_item = sel[0]
                state.current_col = FIRST_EDITABLE_INDEX
                handle_edit_cell()
                return "break"
        return None
    
    tree.bind("<<EditCell>>", handle_edit_cell)
    tree.bind("<Double-1>", on_double_click)
    tree.bind("<Return>", on_tree_key)
    tree.bind("<F2>", on_tree_key)
    tree.bind("<Tab>", lambda e: "break")