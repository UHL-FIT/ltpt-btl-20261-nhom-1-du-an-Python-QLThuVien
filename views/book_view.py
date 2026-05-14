# ==============================================================================
# Tệp: views/book_view.py
# Mục đích: Xây dựng Giao diện (View) cho chức năng Quản lý Danh mục Sách.
# Chức năng:
# - Khởi tạo bố cục trang bao gồm thanh tìm kiếm, các nút hành động (thêm, sửa, xóa).
# - Tạo bảng dữ liệu hiển thị danh sách tất cả các cuốn sách.
# - Gọi trực tiếp đến BookController để truy vấn và cập nhật dữ liệu.
# ==============================================================================
import customtkinter as ctk
from controllers.book_controller import BookController
from tkinter import messagebox
from views.components.data_table import DataTable

class BookView(ctk.CTkFrame):
    # Lớp giao diện hiển thị và thao tác với dữ liệu Sách.
    # Kế thừa từ CTkFrame để có thể đặt (pack/grid) vào bên trong MainView.
    
    def __init__(self, parent, on_refresh=None):
        # Hàm khởi tạo: thiết lập controller và gọi hàm vẽ giao diện setup_ui()
        super().__init__(parent, fg_color="transparent")
        self.on_refresh = on_refresh
        
        # Khởi tạo instance của BookController để giao tiếp với cơ sở dữ liệu
        self.controller = BookController()
        
        # Bắt đầu vẽ các thành phần UI
        self.setup_ui()

    def setup_ui(self):
        # Khởi tạo phần tiêu đề (Header) của trang quản lý sách
        header = ctk.CTkLabel(
            self,
            text="Quản lý Danh mục Sách",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        header.pack(anchor="w", pady=(0, 20))
        


        # Khung chứa thanh tìm kiếm và các nút tính năng mở rộng (Thêm, Làm mới)
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 10), padx=5)

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="🔍 Tìm kiếm theo mã sách, tên sách, thể loại...", width=400)
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.handle_search_realtime)
        
        self.search_btn = ctk.CTkButton(search_frame, text="Tìm kiếm", command=self.handle_search, width=100)
        self.search_btn.pack(side="left", padx=(0, 10))

        self.refresh_btn = ctk.CTkButton(search_frame, text="Làm mới", command=self.refresh_list, width=100)
        self.refresh_btn.pack(side="left", padx=(0, 10))

        self.add_new_btn = ctk.CTkButton(search_frame, text="Thêm Mới", command=lambda: self.open_book_form(), width=100, fg_color="#4caf50", hover_color="#388e3c")
        self.add_new_btn.pack(side="left")

        # Nút xóa chức năng cấp độ hàng, được đặt ở bên phải của thanh tìm kiếm để tạo sự cân bằng đối xứng cho giao diện
        self.del_btn = ctk.CTkButton(
            search_frame, text="Xóa Sách Đã Chọn", 
            command=self.handle_delete, 
            width=150, fg_color="#b83535", hover_color="#8c2323",
            font=ctk.CTkFont(weight="bold")
        )
        self.del_btn.pack(side="right")

        # Khu vực chứa bảng dữ liệu (Data Table Panel) ở nửa dưới của giao diện
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
        
        # Tùy chỉnh màu sắc đánh dấu (tag) cho từng trạng thái của sách trong bảng
        self.table.tree.tag_configure("available", foreground="#4caf50") # Green
        self.table.tree.tag_configure("borrowed", foreground="#ff9800") # Orange
        
        self.table.tree.bind("<Double-1>", self.handle_edit)

        self.refresh_list()

    def handle_edit(self, event):
        selected = self.table.get_selected()
        if selected:
            self.open_book_form(book_data=selected)

    def open_book_form(self, book_data=None):
        form_window = ctk.CTkToplevel(self)
        form_window.title("Sửa Sách" if book_data else "Thêm Sách Mới")
        form_window.geometry("400x350")
        form_window.transient(self.winfo_toplevel())
        form_window.grab_set()

        ctk.CTkLabel(form_window, text="Mã sách (ISBN):").pack(pady=(20, 5), padx=20, anchor="w")
        isbn_entry = ctk.CTkEntry(form_window, placeholder_text="Ví dụ: 978-...")
        isbn_entry.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(form_window, text="Tên sách:").pack(pady=5, padx=20, anchor="w")
        name_entry = ctk.CTkEntry(form_window, placeholder_text="Tên sách")
        name_entry.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(form_window, text="Thể loại:").pack(pady=5, padx=20, anchor="w")
        genre_entry = ctk.CTkEntry(form_window, placeholder_text="Ví dụ: Tiểu thuyết")
        genre_entry.pack(fill="x", padx=20, pady=5)

        if book_data:
            isbn_entry.insert(0, str(book_data[0]))
            name_entry.insert(0, str(book_data[1]))
            genre_entry.insert(0, str(book_data[2]))

        def save_data():
            isbn = isbn_entry.get()
            name = name_entry.get()
            genre = genre_entry.get()

            if not (isbn and name):
                messagebox.showwarning("Lỗi nhập liệu", "Vui lòng điền các trường bắt buộc (Mã sách, Tên sách)")
                return

            if book_data:
                old_isbn = book_data[0]
                success, msg = self.controller.update_book(old_isbn, isbn, name, genre)
            else:
                success, msg = self.controller.add_book(isbn, name, genre)

            if success:
                self.refresh_list()
                if self.on_refresh:
                    self.on_refresh()
                messagebox.showinfo("Thành công", msg)
                form_window.destroy()
            else:
                messagebox.showerror("Lỗi", msg)

        save_btn = ctk.CTkButton(form_window, text="Lưu", command=save_data)
        save_btn.pack(pady=20)

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
