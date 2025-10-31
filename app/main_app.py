# main_app.py

import tkinter as tk
from datetime import datetime
import ttkbootstrap as tb
from ttkbootstrap.constants import *

# Constants
from constants.index import COLUMNS, EDITABLE_FIELDS, FONT 

# Data Management Utils
from utils.dp_utils import init_db 
from utils.export_to_csv import export_all_to_csv, export_mismatch_to_csv
from utils.export_to_pdf import export_all_to_pdf, export_mismatch_to_pdf

# UI Components
from ui.ui_components import setup_main_window, setup_header, setup_top_controls, setup_stats_frame, setup_treeview
from utils.data_handlers import load_data, search_products
from utils.cell_editor import setup_tree_bindings
from ui.delete_selected import delete_selected
from ui.open_add_window import open_add_window
from ui.open_csv_manager import open_csv_manager
from ui.open_product_manager_window import open_product_manager_window

# Global Constants for Editable Fields
EDITABLE_INDEXES = [COLUMNS.index(f) for f in COLUMNS if f in EDITABLE_FIELDS]
FIRST_EDITABLE_INDEX = EDITABLE_INDEXES[0] if EDITABLE_INDEXES else 1


# -------------------------
# UI Setup
# -------------------------
app, root = setup_main_window()
search_var = tk.StringVar() 

# 1. Header
setup_header(root)

# 2. Top Controls (Search & Buttons)
top_frame, search_entry, btn_frame = setup_top_controls(root, search_var)

# 3. Table & Stats container
container = tb.Frame(root)
container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

# 4. Stats Frame
stats_frame, stat_vars = setup_stats_frame(container)
# stat_vars = (stat_req_val, stat_good_val, stat_dam_val, stat_gift_val, stat_tot_val)

# 5. Treeview
tree, style = setup_treeview(container)


# -------------------------
# Bindings & Commands
# -------------------------

# Search Binding
search_entry.bind("<KeyRelease>", lambda e: load_data(tree, search_var.get(), stat_vars))
search_entry.bind("<Return>", lambda e: search_products(tree, search_var, FIRST_EDITABLE_INDEX))
search_entry.bind("<Tab>", lambda e: search_products(tree, search_var, FIRST_EDITABLE_INDEX))

# Buttons Commandsroot, load_data_func, tree, search_term, stat_vars
tb.Button(btn_frame, text="➕ Add CSV ", bootstyle="success", command=lambda: open_csv_manager(root, load_data, tree, search_var.get(), stat_vars)).pack(side=LEFT, padx=4) 
tb.Button(btn_frame, text="➕ Add Product", bootstyle="success", command=lambda: open_add_window(root, load_data, tree, search_var.get(), stat_vars)).pack(side=LEFT, padx=4)
tb.Button(btn_frame, text="📦 Add Stock", bootstyle="info", command=lambda:open_product_manager_window(root, load_data, tree, search_var, stat_vars)).pack(side=LEFT, padx=4)
tb.Button(btn_frame, text="📥 Export CSV", bootstyle="primary", command=lambda: export_all_to_csv()).pack(side=LEFT, padx=4)
tb.Button(btn_frame, text="📄 Export PDF", bootstyle="primary", command=lambda: export_all_to_pdf()).pack(side=LEFT, padx=4)
tb.Button(btn_frame, text="⚠️ Mismatch CSV", bootstyle="warning", command=lambda: export_mismatch_to_csv()).pack(side=LEFT, padx=4)
tb.Button(btn_frame, text="⚠️ Mismatch PDF", bootstyle="warning", command=lambda: export_mismatch_to_pdf()).pack(side=LEFT, padx=4)
tb.Button(btn_frame, text="🗑️ Delete", bootstyle="danger", command=lambda: delete_selected(tree, load_data, search_var.get(), stat_vars)).pack(side=LEFT, padx=4)


# Treeview Cell Editing & Navigation
setup_tree_bindings(
    tree, root, EDITABLE_FIELDS,
    FIRST_EDITABLE_INDEX, EDITABLE_INDEXES, load_data, search_var, stat_vars
)


# -------------------------
# Init DB & Run
# -------------------------
init_db()
load_data(tree, search_var.get(), stat_vars) # Initial load
root.mainloop()