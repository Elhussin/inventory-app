# ui_components.py
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from constants.index import COLUMNS,column_display_names,FONT

# -------------------------
# UI Setup Functions
# -------------------------

def setup_main_window():
    app = tb.Window(title="Inventory Management System", themename="flatly", size=(1400, 800))
    root = app
    style = tb.Style(theme="superhero")
    return app, root

def setup_header(root):
    # Top Frame (Header)
    header = tb.Frame(root, bootstyle="primary")
    header.pack(fill="x")
    title = tb.Label(header, text="📦 Inventory Management System", font=("Arial", 22, "bold"), bootstyle="inverse")
    title.pack(pady=15)

def setup_top_controls(root, search_var):
    # Top Controls Frame
    top_frame = tb.Frame(root)
    top_frame.pack(fill="x", padx=15, pady=10)

    # Search
    search_lbl = tb.Label(top_frame, text="🔍 Search:", font=FONT)
    search_lbl.pack(side=LEFT, padx=(2, 8))
    search_entry = tb.Entry(top_frame, textvariable=search_var, width=45, font=FONT)
    search_entry.pack(side=LEFT)
    
    # Buttons Frame
    btn_frame = tb.Frame(top_frame)
    btn_frame.pack(side=RIGHT)
    
    return top_frame, search_entry, btn_frame

def create_stat_box(parent, text, color="secondary"):
    frame = tb.Frame(parent, bootstyle=color, padding=10)
    label = tb.Label(frame, text=text, font=("Arial", 11, "bold"), bootstyle=f"{color}-inverse")
    value = tb.Label(frame, text="0", font=("Arial", 14, "bold"), bootstyle=f"{color}-inverse")
    label.pack()
    value.pack()
    return frame, value

def setup_stats_frame(container):
    stats_frame = tb.Frame(container)
    stats_frame.pack(fill="x", pady=(0,10))

    stat_req_frame, stat_req_val = create_stat_box(stats_frame, "📋 Total Required", "secondary")
    stat_req_frame.pack(side=LEFT, expand=True, fill="x", padx=4)
    stat_good_frame, stat_good_val = create_stat_box(stats_frame, "✅ Total Good", "success")
    stat_good_frame.pack(side=LEFT, expand=True, fill="x", padx=4)
    stat_dam_frame, stat_dam_val = create_stat_box(stats_frame, "❌ Total Damaged", "danger")
    stat_dam_frame.pack(side=LEFT, expand=True, fill="x", padx=4)
    stat_gift_frame, stat_gift_val = create_stat_box(stats_frame, "🎁 Total Gift", "warning")
    stat_gift_frame.pack(side=LEFT, expand=True, fill="x", padx=4)
    stat_tot_frame, stat_tot_val = create_stat_box(stats_frame, "📦 Total Stock", "info")
    stat_tot_frame.pack(side=LEFT, expand=True, fill="x", padx=4)
    
    stat_vars = (stat_req_val, stat_good_val, stat_dam_val, stat_gift_val, stat_tot_val)
    return stats_frame, stat_vars

def setup_treeview(container):
    columns = tuple(COLUMNS)
    tree_frame = tb.Frame(container)
    tree_frame.pack(fill="both", expand=True)

    tree = tb.Treeview(tree_frame, columns=columns, show="headings", bootstyle="secondary")

    # Scrollbars
    vsb = tb.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    hsb = tb.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscroll=vsb.set, xscroll=hsb.set)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")
    tree.pack(fill="both", expand=True)

    # Styling
    style = tb.Style()
    style.configure("Treeview", rowheight=50, font=("Arial", 12, "bold"), padding=6)
    style.configure("Treeview.Heading", font=("Arial", 12, "bold"), padding=6)


    # Set headings and column widths
    for col in columns:
        tree.heading(col, text=column_display_names.get(col, col))
        # Dynamic column widths
        if col == "id":
            tree.column(col, width=0, minwidth=0, anchor="center", stretch=False)
            # tree.column(col, width=70, minwidth=50, anchor="center", stretch=False, )
        elif col == "description":
            tree.column(col, width=250, minwidth=150, anchor="w", stretch=True)
        elif col == "name":
            tree.column(col, width=0, minwidth=0, anchor="center", stretch=False)

            # tree.column(col, width=150, minwidth=120, anchor="w", stretch=True)
        elif col == "code":
            tree.column(col, width=120, minwidth=80, anchor="center", stretch=True)
        elif col == "note":
            tree.column(col, width=150, minwidth=100, anchor="w", stretch=True)
        elif col in ["cost", "retail"]:
            tree.column(col, width=100, minwidth=80, anchor="center", stretch=True)
        else:
            tree.column(col, width=100, minwidth=70, anchor="center", stretch=True)

    # Row styles
    tree.tag_configure('evenrow', background='#e7e7e7', font=("Arial", 11) ,foreground='#000')
    tree.tag_configure('oddrow', background='#ffffff', font=("Arial", 11) ,foreground='#000')

    return tree, style