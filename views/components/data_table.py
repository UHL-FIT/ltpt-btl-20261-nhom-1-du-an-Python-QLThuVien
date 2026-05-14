# ==============================================================================
# Tệp: views/components/data_table.py
# Mục đích: Định nghĩa thành phần bảng dữ liệu (DataTable) dùng chung (Reusable Component).
# Chức năng:
# - Bao bọc (wrap) ttk.Treeview của Tkinter.
# - Thiết lập màu nền, font chữ và thanh cuộn (scrollbar) để hòa hợp với phong cách Dark Mode của CustomTkinter.
# ==============================================================================
import customtkinter as ctk
from tkinter import ttk
import tkinter as tk

class DataTable(ctk.CTkFrame):
    # Lớp Custom DataTable kế thừa từ CTkFrame.
    
    def __init__(self, master, columns, **kwargs):
        # Khởi tạo thành phần DataTable
        super().__init__(master, **kwargs)
        
        # Configure Grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Setup Style for Treeview to match CustomTkinter Dark Theme
        self.style = ttk.Style(self)
        self.style.theme_use("default")
        
        # Basic Colors
        bg_color = "#2b2b2b"
        fg_color = "#ffffff"
        selected_bg = "#1f538d"
        header_bg = "#1f1f1f"
        
        self.style.configure("Treeview",
                             background=bg_color,
                             foreground=fg_color,
                             fieldbackground=bg_color,
                             borderwidth=0,
                             rowheight=35,
                             font=("Inter", 11))
                             
        self.style.map("Treeview",
                       background=[("selected", selected_bg)])
                       
        self.style.configure("Treeview.Heading",
                             background=header_bg,
                             foreground=fg_color,
                             borderwidth=0,
                             font=("Inter", 12, "bold"))
                             
        self.style.map("Treeview.Heading",
                       background=[("active", "#333333")])

        # Create Treeview
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        
        # Setup Scrollbar
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Setup Headings
        for col in columns:
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=100, anchor="w")

    def insert(self, values, tags=()):
        self.tree.insert("", "end", values=values, tags=tags)
        
    def clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
    def get_selected(self):
        selected_item = self.tree.selection()
        if selected_item:
            return self.tree.item(selected_item[0])['values']
        return None

    def set_column_width(self, col, width):
        self.tree.column(col, width=width)
