def open_add_stock_window():
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Select", "⚠️ Please select a product first.")
        return
    item = sel[0]
    vals = tree.item(item, "values")
    prod_id = vals[0]
    prod_name = vals[1]
    cur_good = int(vals[7] or 0)
    cur_damaged = int(vals[8] or 0)

    win = tb.Toplevel(root)
    win.title("Add Stock")
    win.geometry("450x550")
    win.transient(root)
    win.grab_set()

    # Header
    header_frame = tb.Frame(win, bootstyle="info")
    header_frame.pack(fill="x")
    tb.Label(header_frame, text="📦Add Stock ", font=("Arial", 18, "bold"), bootstyle="inverse").pack(pady=12)

    # Info
    info_frame = tb.Frame(win, padding=15)
    info_frame.pack(fill="x")
    tb.Label(info_frame, text=f"Product: {prod_name}", font=("Arial", 13, "bold")).pack(anchor="w", pady=4)
    tb.Label(info_frame, text=f"Current Good: {cur_good} | Damaged: {cur_damaged}", 
             font=("Arial", 11)).pack(anchor="w", pady=4)

    # Form
    form = tb.Frame(win, padding=15)
    form.pack(fill="both", expand=True)

    tb.Label(form, text="Good Stock:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(8,2))
    good_e = tb.Entry(form, font=FONT)
    good_e.pack(fill="x", pady=(0,8))
    good_e.insert(0, "0")
    good_e.focus()

    tb.Label(form, text="Damaged Stock:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(8,2))
    damaged_e = tb.Entry(form, font=FONT)
    damaged_e.pack(fill="x", pady=(0,8))
    damaged_e.insert(0, "0")

    tb.Label(form, text="Gift Stock:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(8,2))
    gift_e = tb.Entry(form, font=FONT)
    gift_e.pack(fill="x", pady=(0,8))
    gift_e.insert(0, "0")

    tb.Label(form, text="Note (optional):", font=("Arial", 11, "bold")).pack(anchor="w", pady=(8,2))
    note_e = tb.Entry(form, font=FONT)
    note_e.pack(fill="x", pady=(0,8))

    def add_stock_action():
        try:
            g = int(float(good_e.get() or 0))
            d = int(float(damaged_e.get() or 0))
            gf = int(float(gift_e.get() or 0))
            note = note_e.get().strip() or None
            
            if g < 0 or d < 0 or gf < 0:
                messagebox.showerror("Error", "Quantities cannot be negative.")
                return
            if g == 0 and d == 0 and gf == 0:
                messagebox.showwarning("Warning", "Please enter at least one quantity.")
                return
                
            res = update_product_quantities(prod_id, g, d, gf, note)
            if not res:
                messagebox.showerror("Error", "Failed to add stock.")
                return
                
            new_good, new_damaged, new_gift, new_note = res
            win.destroy()
            load_data(search_var.get())
            messagebox.showinfo("Success", 
                f"✅ Stock added successfully!\n\n"
                f"New Good Stock: {new_good}\n"
                f"New Damaged Stock: {new_damaged}\n"
                f"New Gift Stock: {new_gift}\n"
                f"New Total Stock: {new_good + new_damaged + new_gift}")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values.")

    # Buttons
    btnf = tb.Frame(form)
    btnf.pack(pady=15)
    save_btn = tb.Button(btnf, text="✅ Save", bootstyle="success", command=add_stock_action)
    save_btn.pack(side=LEFT, padx=6)
    cancel_btn = tb.Button(btnf, text="❌ Cancel", bootstyle="danger", command=win.destroy)
    cancel_btn.pack(side=LEFT, padx=6)

    # Tab navigation - Fixed
    def focus_next_widget(event, next_widget):
        next_widget.focus()
        return "break"

    good_e.bind("<Tab>", lambda e: focus_next_widget(e, damaged_e))
    good_e.bind("<Return>", lambda e: focus_next_widget(e, damaged_e))
    
    damaged_e.bind("<Tab>", lambda e: focus_next_widget(e, gift_e))
    damaged_e.bind("<Return>", lambda e: focus_next_widget(e, gift_e))
    
    gift_e.bind("<Tab>", lambda e: focus_next_widget(e, note_e))
    gift_e.bind("<Return>", lambda e: focus_next_widget(e, note_e))
    
    note_e.bind("<Tab>", lambda e: focus_next_widget(e, save_btn))
    note_e.bind("<Return>", lambda e: (add_stock_action(), "break")[1])
    
    # Escape to cancel
    win.bind("<Escape>", lambda e: win.destroy())
