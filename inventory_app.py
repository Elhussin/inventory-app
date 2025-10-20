import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

DB_FILE = "inventory.db"

# ========== Colors ==========
COLORS = {
    'primary': '#2c3e50',
    'secondary': '#3498db',
    'success': '#27ae60',
    'danger': '#e74c3c',
    'warning': '#f39c12',
    'light': '#ecf0f1',
    'white': '#ffffff',
    'text': '#2c3e50',
    'hover': '#2980b9',
    'info': '#16a085'
}

# ========== Database Setup ==========
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            code TEXT UNIQUE,
            description TEXT,
            cost REAL,
            retail REAL,
            required_qty INTEGER,
            good_qty INTEGER,
            damaged_qty INTEGER,
            total_qty INTEGER
        )
    """)
    conn.commit()
    conn.close()

def fetch_products(search_text=""):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    if search_text:
        c.execute("""
            SELECT * FROM products
            WHERE name LIKE ? OR code LIKE ?
        """, (f"%{search_text}%", f"%{search_text}%"))
    else:
        c.execute("SELECT * FROM products")
    rows = c.fetchall()
    conn.close()
    return rows

def get_product_by_id(prod_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE id=?", (prod_id,))
    row = c.fetchone()
    conn.close()
    return row

def update_product_quantities(prod_id, good_qty_to_add, damaged_qty_to_add):
    """Add quantities to existing quantities"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Get current quantities
    c.execute("SELECT good_qty, damaged_qty FROM products WHERE id=?", (prod_id,))
    current = c.fetchone()
    
    if current:
        new_good_qty = current[0] + good_qty_to_add
        new_damaged_qty = current[1] + damaged_qty_to_add
        new_total_qty = new_good_qty + new_damaged_qty
        
        c.execute("""
            UPDATE products
            SET good_qty=?, damaged_qty=?, total_qty=?
            WHERE id=?
        """, (new_good_qty, new_damaged_qty, new_total_qty, prod_id))
        conn.commit()
    
    conn.close()
    return new_good_qty if current else 0, new_damaged_qty if current else 0

def update_product_full(prod_id, name, code, description, cost, retail, required_qty, good_qty, damaged_qty):
    """Update all product fields"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    total_qty = good_qty + damaged_qty
    try:
        c.execute("""
            UPDATE products
            SET name=?, code=?, description=?, cost=?, retail=?, required_qty=?, good_qty=?, damaged_qty=?, total_qty=?
            WHERE id=?
        """, (name, code, description, cost, retail, required_qty, good_qty, damaged_qty, total_qty, prod_id))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def insert_product(data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO products (name, code, description, cost, retail, required_qty, good_qty, damaged_qty, total_qty)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data)
        conn.commit()
        conn.close()
        return True, "Product added successfully!"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Product code already exists!"

def delete_product(prod_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE id=?", (prod_id,))
    conn.commit()
    conn.close()

# ========== PDF Export ==========
def export_all_to_pdf():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")]
    )
    if not file_path:
        return

    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT * FROM products")
        rows = c.fetchall()
        conn.close()

        # Create PDF
        doc = SimpleDocTemplate(file_path, pagesize=landscape(A4))
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#7f8c8d'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        # Title
        title = Paragraph("📦 Complete Inventory Report", title_style)
        elements.append(title)
        
        # Date
        date_text = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subtitle = Paragraph(date_text, subtitle_style)
        elements.append(subtitle)
        elements.append(Spacer(1, 20))
        
        # Calculate totals
        total_required = sum(row[6] for row in rows if row[6])
        total_good = sum(row[7] for row in rows if row[7])
        total_damaged = sum(row[8] for row in rows if row[8])
        total_stock = sum(row[9] for row in rows if row[9])
        
        # Summary box
        summary_data = [
            ['Summary', 'Required', 'Good', 'Damaged', 'Total Stock'],
            ['Totals', f'{total_required:,}', f'{total_good:,}', f'{total_damaged:,}', f'{total_stock:,}']
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 30))
        
        # Table headers
        headers = ['ID', 'Name', 'Code', 'Description', 'Cost', 'Retail', 'Required', 'Good', 'Damaged', 'Total']
        
        # Prepare data
        table_data = [headers]
        for row in rows:
            table_data.append([
                str(row[0]),
                str(row[1])[:20],  # Limit name length
                str(row[2]),
                str(row[3])[:25] if row[3] else '',  # Limit description
                f'${row[4]:.2f}' if row[4] else '$0.00',
                f'${row[5]:.2f}' if row[5] else '$0.00',
                str(row[6]) if row[6] else '0',
                str(row[7]) if row[7] else '0',
                str(row[8]) if row[8] else '0',
                str(row[9]) if row[9] else '0'
            ])
        
        # Create table
        col_widths = [0.4*inch, 1.2*inch, 0.8*inch, 1.5*inch, 0.7*inch, 0.7*inch, 0.8*inch, 0.6*inch, 0.8*inch, 0.6*inch]
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Table style
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(table)
        
        # Footer
        elements.append(Spacer(1, 30))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#7f8c8d'),
            alignment=TA_CENTER
        )
        footer = Paragraph(f"Total Products: {len(rows)} | © 2025 Inventory Management System", footer_style)
        elements.append(footer)
        
        # Build PDF
        doc.build(elements)
        
        messagebox.showinfo("Export Success", f"✅ PDF report exported successfully to:\n{file_path}")
        
    except Exception as e:
        messagebox.showerror("Export Error", f"❌ Error creating PDF:\n{str(e)}")

def export_mismatch_to_pdf():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")]
    )
    if not file_path:
        return

    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
            SELECT * FROM products
            WHERE required_qty != total_qty
        """)
        rows = c.fetchall()
        conn.close()

        if not rows:
            messagebox.showinfo("No Data", "ℹ️ No mismatched products found!")
            return

        # Create PDF
        doc = SimpleDocTemplate(file_path, pagesize=landscape(A4))
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#e74c3c'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#7f8c8d'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        # Title
        title = Paragraph("⚠️ Mismatched Inventory Report", title_style)
        elements.append(title)
        
        # Date
        date_text = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subtitle = Paragraph(date_text, subtitle_style)
        elements.append(subtitle)
        elements.append(Spacer(1, 20))
        
        # Warning message
        warning_style = ParagraphStyle(
            'Warning',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#e74c3c'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        warning = Paragraph(f"⚠️ {len(rows)} products have quantity mismatches (Required ≠ Total)", warning_style)
        elements.append(warning)
        elements.append(Spacer(1, 20))
        
        # Table headers
        headers = ['ID', 'Name', 'Code', 'Description', 'Required', 'Good', 'Damaged', 'Total', 'Variance']
        
        # Prepare data
        table_data = [headers]
        for row in rows:
            variance = (row[9] if row[9] else 0) - (row[6] if row[6] else 0)
            variance_str = f"{variance:+d}"  # Show + or - sign
            
            table_data.append([
                str(row[0]),
                str(row[1])[:20],
                str(row[2]),
                str(row[3])[:30] if row[3] else '',
                str(row[6]) if row[6] else '0',
                str(row[7]) if row[7] else '0',
                str(row[8]) if row[8] else '0',
                str(row[9]) if row[9] else '0',
                variance_str
            ])
        
        # Create table
        col_widths = [0.4*inch, 1.5*inch, 0.8*inch, 2*inch, 0.8*inch, 0.7*inch, 0.8*inch, 0.7*inch, 0.8*inch]
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Table style
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            
            # Highlight variance column
            ('BACKGROUND', (8, 1), (8, -1), colors.HexColor('#fff3cd')),
            ('TEXTCOLOR', (8, 1), (8, -1), colors.HexColor('#856404')),
            ('FONTNAME', (8, 1), (8, -1), 'Helvetica-Bold'),
        ]))
        
        elements.append(table)
        
        # Footer
        elements.append(Spacer(1, 30))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#7f8c8d'),
            alignment=TA_CENTER
        )
        footer = Paragraph(f"Mismatched Products: {len(rows)} | © 2025 Inventory Management System", footer_style)
        elements.append(footer)
        
        # Build PDF
        doc.build(elements)
        
        messagebox.showinfo("Export Success", f"✅ PDF report exported successfully to:\n{file_path}")
        
    except Exception as e:
        messagebox.showerror("Export Error", f"❌ Error creating PDF:\n{str(e)}")

# ========== CSV Export ==========
def export_all_to_csv():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    rows = c.fetchall()
    headers = [d[0] for d in c.description]
    conn.close()

    with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    messagebox.showinfo("Export Success", f"✅ Data exported successfully to:\n{file_path}")

def export_mismatch_to_csv():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT * FROM products
        WHERE required_qty != total_qty
    """)
    rows = c.fetchall()
    headers = [d[0] for d in c.description]
    conn.close()

    with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    messagebox.showinfo("Export Success", f"✅ Mismatched data exported successfully to:\n{file_path}")

# ========== UI ==========
root = tk.Tk()
root.title("Inventory Management System")
root.geometry("1400x750")
root.configure(bg=COLORS['light'])

# Custom Style
style = ttk.Style()
style.theme_use('clam')

# Button Styles
style.configure('Primary.TButton', 
                background=COLORS['secondary'],
                foreground='white',
                borderwidth=0,
                focuscolor='none',
                padding=10,
                font=('Arial', 10, 'bold'))
style.map('Primary.TButton',
          background=[('active', COLORS['hover'])])

style.configure('Success.TButton',
                background=COLORS['success'],
                foreground='white',
                borderwidth=0,
                focuscolor='none',
                padding=10,
                font=('Arial', 10, 'bold'))
style.map('Success.TButton',
          background=[('active', '#229954')])

style.configure('Danger.TButton',
                background=COLORS['danger'],
                foreground='white',
                borderwidth=0,
                focuscolor='none',
                padding=10,
                font=('Arial', 10, 'bold'))
style.map('Danger.TButton',
          background=[('active', '#c0392b')])

style.configure('Warning.TButton',
                background=COLORS['warning'],
                foreground='white',
                borderwidth=0,
                focuscolor='none',
                padding=10,
                font=('Arial', 10, 'bold'))
style.map('Warning.TButton',
          background=[('active', '#e67e22')])

style.configure('Info.TButton',
                background=COLORS['info'],
                foreground='white',
                borderwidth=0,
                focuscolor='none',
                padding=10,
                font=('Arial', 10, 'bold'))
style.map('Info.TButton',
          background=[('active', '#138d75')])

# Treeview Style
style.configure('Treeview',
                background=COLORS['white'],
                foreground=COLORS['text'],
                fieldbackground=COLORS['white'],
                rowheight=30,
                font=('Arial', 10))
style.configure('Treeview.Heading',
                background=COLORS['primary'],
                foreground='white',
                font=('Arial', 11, 'bold'),
                relief='flat')
style.map('Treeview.Heading',
          background=[('active', COLORS['secondary'])])

# Header Frame
header_frame = tk.Frame(root, bg=COLORS['primary'], height=80)
header_frame.pack(fill=tk.X)
header_frame.pack_propagate(False)

title_label = tk.Label(header_frame, 
                       text="📦 Inventory Management System",
                       font=('Arial', 24, 'bold'),
                       bg=COLORS['primary'],
                       fg='white')
title_label.pack(pady=20)

# Top Controls Frame
top_frame = tk.Frame(root, bg=COLORS['light'])
top_frame.pack(fill=tk.X, pady=15, padx=20)

# Search Section
search_frame = tk.Frame(top_frame, bg=COLORS['light'])
search_frame.pack(side=tk.LEFT)

search_label = tk.Label(search_frame, 
                        text="🔍 Search:",
                        font=('Arial', 11, 'bold'),
                        bg=COLORS['light'],
                        fg=COLORS['text'])
search_label.pack(side=tk.LEFT, padx=5)

search_var = tk.StringVar()
search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30, font=('Arial', 11))
search_entry.pack(side=tk.LEFT, padx=5)

def search_products(*_):
    load_data(search_var.get())

search_entry.bind("<KeyRelease>", search_products)

# Buttons Section
buttons_frame = tk.Frame(top_frame, bg=COLORS['light'])
buttons_frame.pack(side=tk.RIGHT)

ttk.Button(buttons_frame, text="➕ Add Product", 
           style='Success.TButton',
           command=lambda: open_add_window()).pack(side=tk.LEFT, padx=5)

ttk.Button(buttons_frame, text="📦 Add Stock", 
           style='Info.TButton',
           command=lambda: open_add_stock_window()).pack(side=tk.LEFT, padx=5)

# ttk.Button(buttons_frame, text="💾 Save", 
#            style='Primary.TButton',
#            command=lambda: messagebox.showinfo("Info", "✅ All changes are auto-saved!")).pack(side=tk.LEFT, padx=5)

ttk.Button(buttons_frame, text="📥 Export All ", 
           style='Primary.TButton',
           command=export_all_to_csv).pack(side=tk.LEFT, padx=5)

ttk.Button(buttons_frame, text="📄 Print ALL", 
           style='Primary.TButton',
           command=export_all_to_pdf).pack(side=tk.LEFT, padx=5)

ttk.Button(buttons_frame, text="📥 Export Resualt", 
           style='Warning.TButton',
           command=export_mismatch_to_csv).pack(side=tk.LEFT, padx=5)

ttk.Button(buttons_frame, text="📄 Print Resualt", 
           style='Warning.TButton',
           command=export_mismatch_to_pdf).pack(side=tk.LEFT, padx=5)

def delete_selected():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "⚠️ Please select a product to delete first!")
        return
    
    item = selected[0]
    values = tree.item(item, "values")
    prod_id = values[0]
    prod_name = values[1]
    prod_code = values[2]
    
    # Confirmation dialog
    result = messagebox.askyesno(
        "Confirm Delete",
        f"⚠️ Are you sure you want to delete this product?\n\n"
        f"🏷️ Name: {prod_name}\n"
        f"🔢 Code: {prod_code}\n"
        f"🆔 ID: {prod_id}\n\n"
        f"⛔ This action cannot be undone!",
        icon='warning'
    )
    
    if result:
        delete_product(prod_id)
        load_data(search_var.get())
        messagebox.showinfo("Success", "✅ Product deleted successfully!")

ttk.Button(buttons_frame, text="🗑️ Delete Product", 
           style='Danger.TButton',
           command=delete_selected).pack(side=tk.LEFT, padx=5)

# Table Container Frame
table_container = tk.Frame(root, bg=COLORS['white'], relief=tk.RAISED, borderwidth=2)
table_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

# Table Frame
frame = tk.Frame(table_container, bg=COLORS['white'])
frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

columns = (
    "id", "name", "code", "description", "cost", "retail",
    "required_qty", "good_qty", "damaged_qty", "total_qty"
)

tree = ttk.Treeview(frame, columns=columns, show="headings")

# Scrollbars
vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
tree.configure(yscroll=vsb.set, xscroll=hsb.set)
vsb.pack(side=tk.RIGHT, fill=tk.Y)
hsb.pack(side=tk.BOTTOM, fill=tk.X)
tree.pack(fill=tk.BOTH, expand=True)

# Column Configuration
column_names = {
    "id": "ID",
    "name": "Product Name",
    "code": "Code",
    "description": "Description",
    "cost": "Cost",
    "retail": "Retail Price",
    "required_qty": "Required Qty",
    "good_qty": "Good Qty",
    "damaged_qty": "Damaged Qty",
    "total_qty": "Total Qty"
}

for col in columns:
    tree.heading(col, text=column_names[col])
    if col == "id":
        tree.column(col, width=60, anchor="center")
    elif col in ["description"]:
        tree.column(col, width=200, anchor="w")
    elif col in ["name"]:
        tree.column(col, width=150, anchor="w")
    else:
        tree.column(col, width=110, anchor="center")

# Statistics Frame (before table)
stats_frame = tk.Frame(table_container, bg=COLORS['white'], relief=tk.GROOVE, borderwidth=2)
stats_frame.pack(fill=tk.X, padx=2, pady=(2, 0))

# Statistics Labels
stats_labels = {}

def create_stat_box(parent, label, value, color):
    box = tk.Frame(parent, bg=color, relief=tk.RAISED, borderwidth=2)
    box.pack(side=tk.LEFT, padx=10, pady=10, expand=True, fill=tk.BOTH)
    
    tk.Label(box, 
             text=label,
             font=('Arial', 10, 'bold'),
             bg=color,
             fg='white').pack(pady=(8, 2))
    
    value_label = tk.Label(box, 
                          text=value,
                          font=('Arial', 18, 'bold'),
                          bg=color,
                          fg='white')
    value_label.pack(pady=(2, 8))
    
    return value_label

stats_labels['required'] = create_stat_box(stats_frame, "📋 Total Required", "0", COLORS['secondary'])
stats_labels['good'] = create_stat_box(stats_frame, "✅ Total Good", "0", COLORS['success'])
stats_labels['damaged'] = create_stat_box(stats_frame, "❌ Total Damaged", "0", COLORS['danger'])
stats_labels['total'] = create_stat_box(stats_frame, "📦 Total Stock", "0", COLORS['primary'])

# Row coloring and statistics update
def load_data(search=""):
    tree.delete(*tree.get_children())
    
    # Initialize totals
    total_required = 0
    total_good = 0
    total_damaged = 0
    total_stock = 0
    
    for idx, row in enumerate(fetch_products(search)):
        tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
        tree.insert("", tk.END, values=row, tags=(tag,))
        
        # Calculate totals
        total_required += row[6] if row[6] else 0  # required_qty
        total_good += row[7] if row[7] else 0      # good_qty
        total_damaged += row[8] if row[8] else 0   # damaged_qty
        total_stock += row[9] if row[9] else 0     # total_qty
    
    tree.tag_configure('evenrow', background='#f8f9fa')
    tree.tag_configure('oddrow', background='#ffffff')
    
    # Update statistics
    stats_labels['required'].config(text=f"{total_required:,}")
    stats_labels['good'].config(text=f"{total_good:,}")
    stats_labels['damaged'].config(text=f"{total_damaged:,}")
    stats_labels['total'].config(text=f"{total_stock:,}")

load_data()

# Editing cells - Direct edit (replace values)
def on_double_click(event):
    item = tree.identify_row(event.y)
    column = tree.identify_column(event.x)
    if not item or column == "#1":  # Don't edit ID
        return

    x, y, width, height = tree.bbox(item, column)
    col_index = int(column.replace("#", "")) - 1
    value = tree.item(item, "values")[col_index]

    entry = tk.Entry(tree, font=('Arial', 10))
    entry.place(x=x, y=y, width=width, height=height)
    entry.insert(0, value)
    entry.focus()
    entry.select_range(0, tk.END)

    def save_edit(event=None):
        new_val = entry.get().strip()
        values = list(tree.item(item, "values"))
        prod_id = values[0]
        
        try:
            # Prepare data for update
            name = str(values[1])
            code = str(values[2])
            description = str(values[3])
            cost = float(values[4])
            retail = float(values[5])
            required_qty = int(values[6])
            good_qty = int(values[7])
            damaged_qty = int(values[8])
            
            # Update the specific field based on column
            if col_index == 1:  # name
                name = new_val
            elif col_index == 2:  # code
                code = new_val
            elif col_index == 3:  # description
                description = new_val
            elif col_index == 4:  # cost
                cost = float(new_val)
            elif col_index == 5:  # retail
                retail = float(new_val)
            elif col_index == 6:  # required_qty
                required_qty = int(new_val)
            elif col_index == 7:  # good_qty - Direct replacement
                good_qty = int(new_val)
            elif col_index == 8:  # damaged_qty - Direct replacement
                damaged_qty = int(new_val)
            
            # Update database
            success = update_product_full(prod_id, name, code, description, cost, retail, required_qty, good_qty, damaged_qty)
            
            if success:
                entry.destroy()
                load_data(search_var.get())
                messagebox.showinfo("Success", "✅ Field updated successfully!")
            else:
                messagebox.showerror("Error", "❌ Product code already exists!")
                entry.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "❌ Invalid input! Please enter a valid value.")
            entry.destroy()

    entry.bind("<Return>", save_edit)
    entry.bind("<FocusOut>", save_edit)
    entry.bind("<Escape>", lambda e: entry.destroy())

tree.bind("<Double-1>", on_double_click)

# Add Stock Window (Adds to existing quantities)
def open_add_stock_window():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "⚠️ Please select a product first!")
        return
    
    item = selected[0]
    values = tree.item(item, "values")
    prod_id = values[0]
    prod_name = values[1]
    current_good = values[7]
    current_damaged = values[8]
    
    stock_win = tk.Toplevel(root)
    stock_win.title("Add Stock Quantities")
    stock_win.geometry("450x450")
    stock_win.configure(bg=COLORS['light'])
    stock_win.transient(root)
    stock_win.grab_set()

    # Header
    header = tk.Frame(stock_win, bg=COLORS['info'], height=60)
    header.pack(fill=tk.X)
    header.pack_propagate(False)
    
    tk.Label(header, 
             text="📦 Add Stock to Inventory",
             font=('Arial', 18, 'bold'),
             bg=COLORS['info'],
             fg='white').pack(pady=15)

    # Info Frame
    info_frame = tk.Frame(stock_win, bg=COLORS['white'], relief=tk.RAISED, borderwidth=2)
    info_frame.pack(fill=tk.X, padx=30, pady=20)
    
    tk.Label(info_frame, 
             text=f"Product: {prod_name}",
             font=('Arial', 12, 'bold'),
             bg=COLORS['white'],
             fg=COLORS['text']).pack(pady=5)
    
    tk.Label(info_frame, 
             text=f"Current Good Qty: {current_good} | Current Damaged Qty: {current_damaged}",
             font=('Arial', 10),
             bg=COLORS['white'],
             fg=COLORS['secondary']).pack(pady=5)

    # Form Frame
    form_frame = tk.Frame(stock_win, bg=COLORS['light'])
    form_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

    tk.Label(form_frame, 
             text="Good Quantity to Add:",
             font=('Arial', 11, 'bold'),
             bg=COLORS['light'],
             fg=COLORS['text']).pack(anchor='w', pady=(10, 2))
    
    good_entry = ttk.Entry(form_frame, font=('Arial', 11))
    good_entry.pack(fill=tk.X, pady=(0, 5))
    good_entry.insert(0, "0")

    tk.Label(form_frame, 
             text="Damaged Quantity to Add:",
             font=('Arial', 11, 'bold'),
             bg=COLORS['light'],
             fg=COLORS['text']).pack(anchor='w', pady=(10, 2))
    
    damaged_entry = ttk.Entry(form_frame, font=('Arial', 11))
    damaged_entry.pack(fill=tk.X, pady=(0, 5))
    damaged_entry.insert(0, "0")

    def add_stock():
        try:
            good_to_add = int(good_entry.get() or 0)
            damaged_to_add = int(damaged_entry.get() or 0)
            
            if good_to_add < 0 or damaged_to_add < 0:
                messagebox.showerror("Error", "❌ Quantities cannot be negative!")
                return
            
            if good_to_add == 0 and damaged_to_add == 0:
                messagebox.showwarning("Warning", "⚠️ Please enter at least one quantity to add!")
                return
            
            new_good, new_damaged = update_product_quantities(prod_id, good_to_add, damaged_to_add)
            
            stock_win.destroy()
            load_data(search_var.get())
            messagebox.showinfo("Success", 
                              f"✅ Stock added successfully!\n\n"
                              f"New Good Qty: {new_good}\n"
                              f"New Damaged Qty: {new_damaged}\n"
                              f"New Total: {new_good + new_damaged}")
        except ValueError:
            messagebox.showerror("Error", "❌ Please enter valid numeric values!")

    # Buttons
    btn_frame = tk.Frame(form_frame, bg=COLORS['light'])
    btn_frame.pack(pady=20)
    
    ttk.Button(btn_frame, text="✅ Add Stock", 
               style='Success.TButton',
               command=add_stock).pack(side=tk.LEFT, padx=5)
    
    ttk.Button(btn_frame, text="❌ Cancel", 
               style='Danger.TButton',
               command=stock_win.destroy).pack(side=tk.LEFT, padx=5)

# Add product window
def open_add_window():
    add_win = tk.Toplevel(root)
    add_win.title("Add New Product")
    add_win.geometry("450x650")
    add_win.configure(bg=COLORS['light'])
    add_win.transient(root)
    add_win.grab_set()

    # Header
    header = tk.Frame(add_win, bg=COLORS['success'], height=60)
    header.pack(fill=tk.X)
    header.pack_propagate(False)
    
    tk.Label(header, 
             text="➕ Add New Product",
             font=('Arial', 18, 'bold'),
             bg=COLORS['success'],
             fg='white').pack(pady=15)

    # Form Frame
    form_frame = tk.Frame(add_win, bg=COLORS['light'])
    form_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

    fields = {
        "name": "Product Name *",
        "code": "Product Code *",
        "description": "Description",
        "cost": "Cost Price",
        "retail": "Retail Price",
        "required_qty": "Required Quantity",
        "good_qty": "Good Quantity",
        "damaged_qty": "Damaged Quantity"
    }
    
    entries = {}

    for field, label in fields.items():
        label_widget = tk.Label(form_frame, 
                               text=label,
                               font=('Arial', 11, 'bold'),
                               bg=COLORS['light'],
                               fg=COLORS['text'])
        label_widget.pack(anchor='w', pady=(10, 2))
        
        entry = ttk.Entry(form_frame, font=('Arial', 11))
        entry.pack(fill=tk.X, pady=(0, 5))
        entries[field] = entry

    # Required fields note
    tk.Label(form_frame, 
             text="* Required fields",
             font=('Arial', 9, 'italic'),
             bg=COLORS['light'],
             fg=COLORS['danger']).pack(anchor='w', pady=5)

    def add_product():
        try:
            # Get values from entries
            name = entries['name'].get().strip()
            code = entries['code'].get().strip()
            description = entries['description'].get().strip()
            cost = entries['cost'].get().strip()
            retail = entries['retail'].get().strip()
            required_qty = entries['required_qty'].get().strip()
            good_qty = entries['good_qty'].get().strip()
            damaged_qty = entries['damaged_qty'].get().strip()
            
            # Validate required fields
            if not name:
                messagebox.showerror("Error", "❌ Product Name is required!")
                entries['name'].focus()
                return
            
            if not code:
                messagebox.showerror("Error", "❌ Product Code is required!")
                entries['code'].focus()
                return
            
            # Convert to proper types
            vals = [
                name,
                code,
                description if description else "",
                float(cost) if cost else 0.0,
                float(retail) if retail else 0.0,
                int(required_qty) if required_qty else 0,
                int(good_qty) if good_qty else 0,
                int(damaged_qty) if damaged_qty else 0
            ]
            
            total_qty = vals[6] + vals[7]
            vals.append(total_qty)
            
            success, message = insert_product(vals)
            
            if success:
                add_win.destroy()
                load_data()
                messagebox.showinfo("Success", "✅ Product added successfully!")
            else:
                messagebox.showerror("Error", f"❌ {message}")
                
        except ValueError as e:
            messagebox.showerror("Error", f"❌ Please enter valid numeric values!\n{str(e)}")

    # Buttons Frame
    btn_frame = tk.Frame(form_frame, bg=COLORS['light'])
    btn_frame.pack(pady=20)
    
    ttk.Button(btn_frame, text="💾 Save Product", 
               style='Success.TButton',
               command=add_product).pack(side=tk.LEFT, padx=5)
    
    ttk.Button(btn_frame, text="❌ Cancel", 
               style='Danger.TButton',
               command=add_win.destroy).pack(side=tk.LEFT, padx=5)

# Footer
footer = tk.Frame(root, bg=COLORS['primary'], height=35)
footer.pack(fill=tk.X, side=tk.BOTTOM)
footer.pack_propagate(False)

footer_label = tk.Label(footer,
                        text="© 2025 Inventory Management System - All Rights Reserved",
                        font=('Arial', 9),
                        bg=COLORS['primary'],
                        fg='white')
footer_label.pack(pady=8)

# Initialize DB
init_db()
root.mainloop()