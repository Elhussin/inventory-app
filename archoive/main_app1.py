import tkinter as tk
from tkinter import ttk
import inventory_csv_manager  # Import the CSV manager module

class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("🏢 Main Inventory System")
        self.root.geometry("600x400")
        self.root.configure(bg="#f0f0f0")
        
        # Configure style
        style = ttk.Style()
        style.theme_use("clam")
        
        # Main frame
        main_frame = ttk.Frame(root, padding=20)
        main_frame.pack(expand=True, fill="both")
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="🏢 Main Inventory Management System",
            font=("Segoe UI", 16, "bold"),
            foreground="#0078D7"
        )
        title_label.pack(pady=20)
        
        # Description
        desc_label = ttk.Label(
            main_frame,
            text="Welcome to the main system. Choose an option below:",
            font=("Segoe UI", 10),
            foreground="#666"
        )
        desc_label.pack(pady=10)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=20)
        
        # Button 1: Open CSV Manager
        btn_csv_manager = ttk.Button(
            buttons_frame,
            text="📦 CSV Import/Export Manager",
            command=self.open_csv_manager,
            width=35
        )
        btn_csv_manager.pack(pady=10)
        
        # Button 2: Other function (example)
        btn_inventory = ttk.Button(
            buttons_frame,
            text="📊 View Inventory",
            command=self.view_inventory,
            width=35
        )
        btn_inventory.pack(pady=10)
        
        # Button 3: Other function (example)
        btn_reports = ttk.Button(
            buttons_frame,
            text="📈 Generate Reports",
            command=self.generate_reports,
            width=35
        )
        btn_reports.pack(pady=10)
        
        # Status bar
        self.status_bar = ttk.Label(
            root,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Segoe UI", 9)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def open_csv_manager(self):
        """Opens the CSV Manager as a child window"""
        self.status_bar.config(text="Opening CSV Manager...")
        
        # Call the CSV manager with parent window
        inventory_csv_manager.open_csv_manager(parent=self.root)
        
        self.status_bar.config(text="CSV Manager opened")
    
    def view_inventory(self):
        """Placeholder for inventory view function"""
        self.status_bar.config(text="Opening Inventory View... (Not implemented yet)")
        # Add your inventory view code here
    
    def generate_reports(self):
        """Placeholder for reports function"""
        self.status_bar.config(text="Generating Reports... (Not implemented yet)")
        # Add your reports code here


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()