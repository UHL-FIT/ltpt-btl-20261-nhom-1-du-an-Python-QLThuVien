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
        
        # Basic Colors (Slate Dark Theme)
        bg_color = "#1e293b"      # slate-800
        fg_color = "#f8fafc"      # slate-50
        selected_bg = "#3b82f6"   # blue-500
        header_bg = "#0f172a"     # slate-900
        
        self.style.configure("Treeview",
                             background=bg_color,
                             foreground=fg_color,
                             fieldbackground=bg_color,
                             borderwidth=0,
                             rowheight=35,
                             font=("Segoe UI", 11))
                             
        self.style.map("Treeview",
                       background=[("selected", selected_bg)])
                       
        self.style.configure("Treeview.Heading",
                             background=header_bg,
                             foreground=fg_color,
                             borderwidth=0,
                             font=("Segoe UI", 11, "bold"))
                             
        self.style.map("Treeview.Heading",
                       background=[("active", "#1e293b")])

        # Create Treeview
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        
        # Setup Scrollbar
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Setup Headings
        self.columns = columns
        for col in columns:
            self.tree.heading(col, text=col.title(), command=lambda c=col: self.sort_by(c, False))
            self.tree.column(col, width=100, anchor="w")

    def sort_by(self, col, reverse):
        # Lấy tất cả id các dòng trong bảng
        items = self.tree.get_children("")
        if not items:
            return
            
        # Thu thập dữ liệu của cột cần sắp xếp kèm theo item ID tương ứng
        data = []
        for item in items:
            val = self.tree.set(item, col)
            data.append((val, item))
            
        # Hàm xác định khóa sắp xếp thông minh theo kiểu dữ liệu
        def get_sort_key(element):
            val = element[0]
            val_str = str(val).strip()
            if not val_str:
                return (0, "")
                
            # Thử parse số nguyên
            try:
                return (1, int(val_str))
            except ValueError:
                pass
                
            # Thử parse số thực
            try:
                return (2, float(val_str))
            except ValueError:
                pass
                
            # Trả về chữ thường để sắp xếp không phân biệt hoa thường
            return (3, val_str.lower())
            
        data.sort(key=get_sort_key, reverse=reverse)
        
        # Sắp xếp lại thứ tự hiển thị trong Treeview
        for index, (_, item) in enumerate(data):
            self.tree.move(item, "", index)
            
        # Đổi hành động click kế tiếp để đảo ngược chiều sắp xếp
        self.tree.heading(col, command=lambda c=col: self.sort_by(c, not reverse))
        
        # Cập nhật ký hiệu mũi tên (▲/▼) trên các cột
        for c in self.columns:
            current_text = self.tree.heading(c, "text")
            # Xóa các mũi tên cũ nếu có
            if current_text.endswith(" ▲") or current_text.endswith(" ▼"):
                current_text = current_text[:-2]
                
            if c == col:
                arrow = " ▼" if reverse else " ▲"
                self.tree.heading(c, text=current_text + arrow)
            else:
                self.tree.heading(c, text=current_text)

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
