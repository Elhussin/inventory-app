# window_manager.py
from tkinter import messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from app.utils.dp_utils import insert_product 
from app.constants.index import Fields as fields, FONT





def open_add_window(root, load_data_func, tree, search_term, stat_vars):
    win = tb.Toplevel(root)
    win.title("Add New Product")
    win.geometry("500x550")
    win.transient(root)
    win.grab_set()

    # Header
    header_frame = tb.Frame(win, bootstyle="success")
    header_frame.pack(fill="x")
    tb.Label(header_frame, text="➕ Add New Product", font=("Arial", 18, "bold"), bootstyle="inverse").pack(pady=12)

    # Form
    form = tb.Frame(win, padding=15)
    form.pack(fill="both", expand=True)
    
    entries = {}
    entry_list = []
    
    # Create a frame for the form with grid layout
    form_frame = tb.Frame(form)
    form_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    # Configure grid weights
    form_frame.columnconfigure(0, weight=1)
    form_frame.columnconfigure(1, weight=1)
    
    for i, (key, label) in enumerate(fields):
        row = i // 2
        col = i % 2
        
        # Create a frame for each field to maintain consistent spacing
        field_frame = tb.Frame(form_frame)
        field_frame.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
        field_frame.columnconfigure(0, weight=1)
        
        # Add label and entry
        tb.Label(field_frame, text=label, font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 2))
        e = tb.Entry(field_frame, font=FONT)
        e.pack(fill="x")
        entries[key] = e
        entry_list.append(e)

    # Set default values
    entries["good_qty"].insert(0, "0")
    entries["damaged_qty"].insert(0, "0")
    entries["gift"].insert(0, "0")
    entries["name"].focus()
    
    # Required note
    tb.Label(form, text="* Required fields", font=("Arial", 9, "italic"), bootstyle="danger").pack(anchor="w", pady=8)

    def add_action():
        try:
            
            code = entries["code"].get().strip()
            
            if not code:
                messagebox.showerror("Error", "Product code is required!")
                entries["code"].focus()
                return
            name = entries["name"].get().strip()    
            description = entries["description"].get().strip()
            cost = float(entries["cost"].get() or 0)
            retail = float(entries["retail"].get() or 0)
            required_qty = int(float(entries["required_qty"].get() or 0))
            good_qty = int(float(entries["good_qty"].get() or 0))
            damaged_qty = int(float(entries["damaged_qty"].get() or 0))
            gift = int(float(entries["gift"].get() or 0))
            note = entries["note"].get().strip()

            total_qty = good_qty + damaged_qty + gift
            data = (name, code, description, cost, retail, required_qty, good_qty, damaged_qty, total_qty, gift, note)
            
            ok, msg = insert_product(data)
            if not ok:
                messagebox.showerror("Error", f"❌ {msg}")
                return
                
            win.destroy()
            load_data_func(tree, search_term, stat_vars)
            messagebox.showinfo("Success", "✅ Product added successfully.")
        except ValueError as e:
            messagebox.showerror("Error", f"Please enter valid numeric values.\n{e}")

    # Buttons
    btnf = tb.Frame(form)
    btnf.pack(pady=15)
    save_btn = tb.Button(btnf, text="💾 Save", bootstyle="success", command=add_action)
    save_btn.pack(side=LEFT, padx=6)
    cancel_btn = tb.Button(btnf, text="❌ Cancel", bootstyle="danger", command=win.destroy)
    cancel_btn.pack(side=LEFT, padx=6)

    # Tab navigation between fields
    def setup_tab_navigation():
        for i in range(len(entry_list)):
            if i < len(entry_list) - 1:
                entry_list[i].bind("<Tab>", lambda e, idx=i: (entry_list[idx + 1].focus(), "break")[1])
                entry_list[i].bind("<Return>", lambda e, idx=i: (entry_list[idx + 1].focus(), "break")[1])
            else:
                entry_list[i].bind("<Tab>", lambda e: (save_btn.focus(), "break")[1])
                entry_list[i].bind("<Return>", lambda e: (add_action(), "break")[1])
    
    setup_tab_navigation()
    win.bind("<Escape>", lambda e: win.destroy())

    def setup_tab_navigation():
        for i in range(len(entry_list)):
            if i < len(entry_list) - 1:
                # go to next field on Tab or Return
                entry_list[i].bind("<Tab>", lambda e, idx=i: (entry_list[idx + 1].focus(), "break")[1])
                entry_list[i].bind("<Return>", lambda e, idx=i: (entry_list[idx + 1].focus(), "break")[1])
            else:
                # go to save button on Tab or Return
                entry_list[i].bind("<Tab>", lambda e: (save_btn.focus(), "break")[1])
                entry_list[i].bind("<Return>", lambda e: (add_action(), "break")[1])
    
    # make sure the save button also accepts Return/Enter when focused
    save_btn.bind("<Return>", lambda e: (add_action(), "break")[1])

    setup_tab_navigation()

