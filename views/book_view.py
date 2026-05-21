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
from views.components.custom_dialog import show_custom_info, show_custom_error, show_custom_warning, show_custom_askyesno
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

        self.search_entry = ctk.CTkEntry(
            search_frame, 
            placeholder_text="🔍 Tìm kiếm theo mã sách, tên sách, thể loại...", 
            width=400,
            border_color="#475569",
            fg_color="#1e293b"
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.handle_search_realtime)
        
        self.search_btn = ctk.CTkButton(
            search_frame, text="Tìm kiếm", command=self.handle_search, width=100,
            fg_color="#3b82f6", hover_color="#2563eb"
        )
        self.search_btn.pack(side="left", padx=(0, 10))

        self.refresh_btn = ctk.CTkButton(
            search_frame, text="Làm mới", command=self.refresh_list, width=100,
            fg_color="#475569", hover_color="#334155"
        )
        self.refresh_btn.pack(side="left", padx=(0, 10))

        # Nút xóa chức năng cấp độ hàng, được đặt ở bên phải của thanh tìm kiếm để tạo sự cân bằng đối xứng cho giao diện
        self.del_btn = ctk.CTkButton(
            search_frame, text="Xóa Sách Đã Chọn", 
            command=self.handle_delete, 
            width=150, fg_color="#ef4444", hover_color="#dc2626",
            font=ctk.CTkFont(weight="bold")
        )
        self.del_btn.pack(side="right", padx=(10, 0))

        self.export_btn = ctk.CTkButton(
            search_frame, text="Xuất Excel", command=self.handle_export_excel, width=100,
            fg_color="#3b82f6", hover_color="#2563eb", font=ctk.CTkFont(weight="bold")
        )
        self.export_btn.pack(side="right", padx=(10, 0))

        self.import_btn = ctk.CTkButton(
            search_frame, text="Nhập từ Excel", command=self.handle_import_excel, width=110,
            fg_color="#f59e0b", hover_color="#d97706", font=ctk.CTkFont(weight="bold")
        )
        self.import_btn.pack(side="right", padx=(10, 0))

        self.add_new_btn = ctk.CTkButton(
            search_frame, text="Thêm Mới", command=lambda: self.open_book_form(), width=100, 
            fg_color="#10b981", hover_color="#059669", font=ctk.CTkFont(weight="bold")
        )
        self.add_new_btn.pack(side="right", padx=(10, 0))

        # Khu vực chứa bảng dữ liệu (Data Table Panel) ở nửa dưới của giao diện
        self.table_frame = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=12)
        self.table_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        columns = ("isbn", "name", "genre", "status")
        self.table = DataTable(self.table_frame, columns=columns)
        self.table.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.table.tree.heading("isbn", text="Mã sách (ISBN)")
        self.table.tree.heading("name", text="Tên sách")
        self.table.tree.heading("genre", text="Thể loại")
        self.table.tree.heading("status", text="Trạng thái")
        
        self.table.set_column_width("isbn", 150)
        self.table.set_column_width("name", 350)
        self.table.set_column_width("genre", 150)
        self.table.set_column_width("status", 100)
        
        # Tùy chỉnh màu sắc đánh dấu (tag) cho từng trạng thái của sách trong bảng
        self.table.tree.tag_configure("available", foreground="#10b981") # Emerald Green
        self.table.tree.tag_configure("borrowed", foreground="#f59e0b") # Amber/Orange
        
        self.table.tree.bind("<Double-1>", self.handle_edit)

        self.refresh_list()

    def handle_edit(self, event):
        selected = self.table.get_selected()
        if selected:
            self.open_book_form(book_data=selected)

    def open_book_form(self, book_data=None):
        form_window = ctk.CTkToplevel(self)
        form_window.title("Sửa Sách" if book_data else "Thêm Sách Mới")
        form_window.geometry("420x400")
        form_window.resizable(False, False)
        form_window.configure(fg_color="#0f172a")
        form_window.transient(self.winfo_toplevel())
        form_window.grab_set()

        # Center relative to parent
        form_window.update_idletasks()
        try:
            parent = self.winfo_toplevel()
            parent_x = parent.winfo_rootx()
            parent_y = parent.winfo_rooty()
            parent_w = parent.winfo_width()
            parent_h = parent.winfo_height()
            x = parent_x + (parent_w - 420) // 2
            y = parent_y + (parent_h - 400) // 2
            form_window.geometry(f"+{x}+{y}")
        except Exception:
            form_window.geometry("420x400+500+250")

        # Outer Border Frame matching theme
        border_frame = ctk.CTkFrame(form_window, fg_color="#1e293b", corner_radius=12, border_color="#3b82f6", border_width=1)
        border_frame.pack(fill="both", expand=True, padx=12, pady=12)

        # Title Label
        title_lbl = ctk.CTkLabel(
            border_frame, 
            text="THÔNG TIN SÁCH" if not book_data else "CẬP NHẬT THÔNG TIN SÁCH",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#3b82f6"
        )
        title_lbl.pack(pady=(15, 10))

        ctk.CTkLabel(border_frame, text="Mã sách (ISBN):", font=ctk.CTkFont(size=12), text_color="#94a3b8").pack(pady=(5, 2), padx=25, anchor="w")
        isbn_entry = ctk.CTkEntry(border_frame, placeholder_text="Ví dụ: 978-...", fg_color="#0f172a", border_color="#475569")
        isbn_entry.pack(fill="x", padx=25, pady=(0, 10))

        ctk.CTkLabel(border_frame, text="Tên sách:", font=ctk.CTkFont(size=12), text_color="#94a3b8").pack(pady=(5, 2), padx=25, anchor="w")
        name_entry = ctk.CTkEntry(border_frame, placeholder_text="Tên sách", fg_color="#0f172a", border_color="#475569")
        name_entry.pack(fill="x", padx=25, pady=(0, 10))

        ctk.CTkLabel(border_frame, text="Thể loại:", font=ctk.CTkFont(size=12), text_color="#94a3b8").pack(pady=(5, 2), padx=25, anchor="w")
        genre_entry = ctk.CTkEntry(border_frame, placeholder_text="Ví dụ: Tiểu thuyết", fg_color="#0f172a", border_color="#475569")
        genre_entry.pack(fill="x", padx=25, pady=(0, 15))

        if book_data:
            isbn_entry.insert(0, str(book_data[0]) if book_data[0] is not None and str(book_data[0]).strip().lower() != 'none' else "")
            name_entry.insert(0, str(book_data[1]) if book_data[1] is not None and str(book_data[1]).strip().lower() != 'none' else "")
            genre_entry.insert(0, str(book_data[2]) if book_data[2] is not None and str(book_data[2]).strip().lower() != 'none' else "")

        def save_data():
            isbn = isbn_entry.get().strip()
            name = name_entry.get().strip()
            genre = genre_entry.get().strip()

            if not (isbn and name):
                show_custom_warning(form_window, "Lỗi nhập liệu", "Vui lòng điền các trường bắt buộc (Mã sách, Tên sách)")
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
                show_custom_info(form_window, "Thành công", msg)
                form_window.destroy()
            else:
                show_custom_error(form_window, "Lỗi", msg)

        save_btn = ctk.CTkButton(
            border_frame, text="Lưu thông tin", command=save_data,
            fg_color="#3b82f6", hover_color="#2563eb", font=ctk.CTkFont(weight="bold")
        )
        save_btn.pack(pady=(5, 15))

    def handle_search_realtime(self, event):
        self.handle_search()

    def handle_search(self):
        query = self.search_entry.get()
        if not query.strip():
            self.refresh_list()
            return
            
        self.table.clear()
        books = self.controller.search_books(query)
        rows = []
        for book in books:
            tag = "available" if book.status == "Available" else "borrowed"
            status_vn = "Có sẵn" if book.status == "Available" else "Đang mượn"
            rows.append(((book.isbn, book.name, book.genre, status_vn), (tag,)))
        self.table.insert_batch(rows)

    def refresh_list(self):
        self.table.clear()

        books = self.controller.get_all_books()
        rows = []
        for book in books:
            tag = "available" if book.status == "Available" else "borrowed"
            status_vn = "Có sẵn" if book.status == "Available" else "Đang mượn"
            rows.append(((book.isbn, book.name, book.genre, status_vn), (tag,)))
        self.table.insert_batch(rows)

    def handle_delete(self):
        selected = self.table.get_selected()
        if not selected:
            show_custom_warning(self, "Chọn sách", "Vui lòng chọn một quyển sách từ bảng để xóa.")
            return
 
        isbn = selected[0]
        if show_custom_askyesno(self, "Xác nhận", f"Bạn có chắc muốn xóa sách có mã {isbn}?"):
            if self.controller.delete_book(isbn):
                self.refresh_list()
                if self.on_refresh:
                    self.on_refresh()
                show_custom_info(self, "Thành công", "Xóa sách thành công.")
            else:
                show_custom_error(self, "Lỗi", "Không thể xóa sách này.")

    def handle_import_excel(self):
        from views.components.import_excel_dialog import ImportExcelDialog
        columns = ["Mã Sách (ISBN)", "Tên Sách", "Thể Loại", "Tác Giả", "Nhà Xuất Bản", "Năm Xuất Bản"]
        ImportExcelDialog(
            self, 
            title="Nhập dữ liệu Sách từ Excel", 
            template_columns=columns, 
            default_template_name="Template_Books.xlsx",
            on_import_click=self._process_import_excel
        )

    def _process_import_excel(self):
        import threading
        from tkinter import filedialog
        import pandas as pd
        
        filepath = filedialog.askopenfilename(
            title="Chọn tệp Excel",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if not filepath:
            return
            
        progress_win = ctk.CTkToplevel(self)
        progress_win.title("Nhập dữ liệu Excel")
        progress_win.geometry("400x150")
        progress_win.resizable(False, False)
        progress_win.configure(fg_color="#0f172a")
        progress_win.transient(self.winfo_toplevel())
        progress_win.grab_set()
        
        progress_win.update_idletasks()
        try:
            parent = self.winfo_toplevel()
            x = parent.winfo_rootx() + (parent.winfo_width() - 400) // 2
            y = parent.winfo_rooty() + (parent.winfo_height() - 150) // 2
            progress_win.geometry(f"+{x}+{y}")
        except:
            pass
            
        label = ctk.CTkLabel(progress_win, text="Đang chuẩn bị tệp tin...", text_color="#f8fafc", font=ctk.CTkFont(size=13))
        label.pack(pady=(20, 10))
        
        progress_bar = ctk.CTkProgressBar(progress_win, width=300)
        progress_bar.pack(pady=10)
        progress_bar.configure(mode="indeterminate")
        progress_bar.start()
        
        def do_import():
            try:
                label.configure(text="Đang phân tích dữ liệu Excel...")
                df = pd.read_excel(filepath)
                label.configure(text="Đang ghi vào cơ sở dữ liệu...")
                success, skipped, err = self.controller.import_books_from_df(df)
                
                self.after(0, lambda: import_finished(success, skipped, err))
            except Exception as e:
                self.after(0, lambda: import_finished(0, 0, str(e)))
                
        def import_finished(success, skipped, err):
            progress_bar.stop()
            progress_win.destroy()
            if err:
                show_custom_error(self, "Lỗi nhập Excel", err)
            else:
                self.refresh_list()
                if self.on_refresh:
                    self.on_refresh()
                show_custom_info(
                    self, 
                    "Nhập dữ liệu thành công", 
                    f"Đã nhập thành công {success} sách mới.\nBỏ qua {skipped} dòng (trùng mã hoặc dữ liệu không hợp lệ)."
                )
                
        threading.Thread(target=do_import, daemon=True).start()

    def handle_export_excel(self):
        import datetime
        from tkinter import filedialog
        import pandas as pd
        
        items = self.table.tree.get_children("")
        if not items:
            show_custom_warning(self, "Không có dữ liệu", "Không có dữ liệu hiển thị trên bảng để xuất.")
            return
            
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"Books_Filtered_{timestamp}.xlsx"
        
        filepath = filedialog.asksaveasfilename(
            title="Lưu báo cáo Excel",
            initialfile=default_filename,
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if not filepath:
            return
            
        data = []
        for item in items:
            values = self.table.tree.item(item)['values']
            if not values or isinstance(values, str) or len(values) < 4:
                continue
            data.append({
                'Mã Sách (ISBN)': values[0],
                'Tên Sách': values[1],
                'Thể Loại': values[2],
                'Trạng Thái': values[3]
            })
            
        try:
            df = pd.DataFrame(data)
            df.to_excel(filepath, index=False)
            show_custom_info(self, "Thành công", f"Đã xuất dữ liệu ra tệp:\n{filepath}")
        except Exception as e:
            show_custom_error(self, "Lỗi xuất file", str(e))
