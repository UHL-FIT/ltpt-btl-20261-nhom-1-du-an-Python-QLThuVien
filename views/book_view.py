import customtkinter as ctk
from controllers.book_controller import BookController
from tkinter import messagebox
from views.components.data_table import DataTable

class BookView(ctk.CTkFrame):
    def __init__(self, parent, on_refresh=None):
        super().__init__(parent, fg_color="transparent")
        self.on_refresh = on_refresh
        self.controller = BookController()
        
        self.setup_ui()

    def setup_ui(self):
        # Header
        header = ctk.CTkLabel(
            self,
            text="Quản lý Danh mục Sách",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        header.pack(anchor="w", pady=(0, 20))
        
        # Action Panel (Top)
        action_frame = ctk.CTkFrame(self)
        action_frame.pack(fill="x", pady=(0, 20), padx=5)
        
        action_frame.grid_columnconfigure((1, 3, 5), weight=1)

        ctk.CTkLabel(action_frame, text="Mã sách (ISBN):").grid(row=0, column=0, padx=10, pady=15, sticky="w")
        self.isbn_entry = ctk.CTkEntry(action_frame, placeholder_text="Ví dụ: 978-...")
        self.isbn_entry.grid(row=0, column=1, padx=10, pady=15, sticky="ew")

        ctk.CTkLabel(action_frame, text="Tên sách:").grid(row=0, column=2, padx=10, pady=15, sticky="w")
        self.name_entry = ctk.CTkEntry(action_frame, placeholder_text="Tên sách")
        self.name_entry.grid(row=0, column=3, padx=10, pady=15, sticky="ew")

        ctk.CTkLabel(action_frame, text="Thể loại:").grid(row=0, column=4, padx=10, pady=15, sticky="w")
        self.genre_entry = ctk.CTkEntry(action_frame, placeholder_text="Ví dụ: Tiểu thuyết")
        self.genre_entry.grid(row=0, column=5, padx=10, pady=15, sticky="ew")

        btn_frame = ctk.CTkFrame(action_frame, fg_color="transparent")
        btn_frame.grid(row=0, column=6, padx=10, pady=15, sticky="e")

        self.add_btn = ctk.CTkButton(btn_frame, text="Thêm Sách", command=self.handle_add, width=120)
        self.add_btn.pack(side="left")

        # Search Bar & List Actions
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 10), padx=5)

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="🔍 Tìm kiếm theo mã sách, tên sách, thể loại...", width=400)
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.handle_search_realtime)
        
        self.search_btn = ctk.CTkButton(search_frame, text="Tìm kiếm", command=self.handle_search, width=100)
        self.search_btn.pack(side="left", padx=(0, 10))

        self.refresh_btn = ctk.CTkButton(search_frame, text="Làm mới", command=self.refresh_list, width=100)
        self.refresh_btn.pack(side="left")

        # Row level action placed on the right side of search bar for symmetrical ERP UI
        self.del_btn = ctk.CTkButton(
            search_frame, text="Xóa Sách Đã Chọn", 
            command=self.handle_delete, 
            width=150, fg_color="#b83535", hover_color="#8c2323",
            font=ctk.CTkFont(weight="bold")
        )
        self.del_btn.pack(side="right")

        # Data Table Panel (Bottom)
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        columns = ("isbn", "name", "genre", "status")
        self.table = DataTable(self.table_frame, columns=columns)
        self.table.pack(fill="both", expand=True, padx=2, pady=2)
        
        self.table.tree.heading("isbn", text="Mã sách (ISBN)")
        self.table.tree.heading("name", text="Tên sách")
        self.table.tree.heading("genre", text="Thể loại")
        self.table.tree.heading("status", text="Trạng thái")
        
        self.table.set_column_width("isbn", 150)
        self.table.set_column_width("name", 350)
        self.table.set_column_width("genre", 150)
        self.table.set_column_width("status", 100)
        
        # Customize tags for status colors
        self.table.tree.tag_configure("available", foreground="#4caf50") # Green
        self.table.tree.tag_configure("borrowed", foreground="#ff9800") # Orange
        
        self.refresh_list()

    def handle_add(self):
        isbn = self.isbn_entry.get()
        name = self.name_entry.get()
        genre = self.genre_entry.get()
        
        if isbn and name:
            success, msg = self.controller.add_book(isbn, name, genre)
            if success:
                self.refresh_list()
                if self.on_refresh:
                    self.on_refresh()
                self.isbn_entry.delete(0, 'end')
                self.name_entry.delete(0, 'end')
                self.genre_entry.delete(0, 'end')
                messagebox.showinfo("Thành công", msg)
            else:
                messagebox.showerror("Lỗi", msg)
        else:
            messagebox.showwarning(
                "Lỗi nhập liệu", "Vui lòng điền các trường bắt buộc (Mã sách, Tên sách)"
            )

    def handle_search_realtime(self, event):
        self.handle_search()

    def handle_search(self):
        query = self.search_entry.get()
        if not query.strip():
            self.refresh_list()
            return
            
        self.table.clear()
        books = self.controller.search_books(query)
        for book in books:
            tag = "available" if book.status == "Available" else "borrowed"
            status_vn = "Có sẵn" if book.status == "Available" else "Đang mượn"
            self.table.insert((book.isbn, book.name, book.genre, status_vn), tags=(tag,))

    def refresh_list(self):
        self.table.clear()

        books = self.controller.get_all_books()
        for book in books:
            tag = "available" if book.status == "Available" else "borrowed"
            status_vn = "Có sẵn" if book.status == "Available" else "Đang mượn"
            self.table.insert((book.isbn, book.name, book.genre, status_vn), tags=(tag,))

    def handle_delete(self):
        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("Chọn sách", "Vui lòng chọn một quyển sách từ bảng để xóa.")
            return

        isbn = selected[0]
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa sách có mã {isbn}?"):
            if self.controller.delete_book(isbn):
                self.refresh_list()
                if self.on_refresh:
                    self.on_refresh()
                messagebox.showinfo("Thành công", "Xóa sách thành công.")
            else:
                messagebox.showerror("Lỗi", "Không thể xóa sách này.")
