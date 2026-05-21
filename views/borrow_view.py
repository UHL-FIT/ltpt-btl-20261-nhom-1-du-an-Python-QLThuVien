# ==============================================================================
# Tệp: views/borrow_view.py
# Mục đích: Cung cấp giao diện Quản lý Mượn & Trả sách.
# Chức năng chính:
# - Tạo form nhập nhanh thông tin để lập Phiếu mượn (BorrowSlip).
# - Tích hợp các bảng phân chia rõ ràng trạng thái: Đang mượn, Quá hạn, và Lịch sử (Đã trả).
# ==============================================================================
import customtkinter as ctk
from controllers.borrow_controller import BorrowController
from controllers.student_controller import StudentController
from controllers.book_controller import BookController
from views.components.custom_dialog import show_custom_info, show_custom_error, show_custom_warning, show_custom_askyesno
from views.components.data_table import DataTable

class BorrowView(ctk.CTkFrame):
    # Lớp giao diện hiển thị xử lý nghiệp vụ mượn/trả.
    
    def __init__(self, parent, on_refresh=None):
        # Khởi tạo khung giao diện mượn trả
        super().__init__(parent, fg_color="transparent")
        self.on_refresh = on_refresh
        
        # Controller chính cho phiếu mượn
        self.controller = BorrowController()
        # Controller hỗ trợ tính năng tự động gợi ý (Autocomplete) sinh viên và sách
        self.student_ctrl = StudentController()
        self.book_ctrl = BookController()
        
        # Vẽ cấu trúc giao diện
        self.setup_ui()

    def setup_ui(self):
        # Phần tiêu đề của giao diện (Header)
        header = ctk.CTkLabel(
            self, text="Quản lý Mượn & Trả sách",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        header.pack(anchor="w", pady=(0, 20))
        
        # Khu vực nhập liệu (Action Panel) nằm ở phía trên cùng của giao diện
        self.action_frame = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=12)
        self.action_frame.pack(fill="x", pady=(0, 20), padx=5)
        
        self.action_frame.grid_columnconfigure((1, 3, 5), weight=1)

        ctk.CTkLabel(self.action_frame, text="Mã sinh viên:").grid(row=0, column=0, padx=15, pady=15, sticky="w")
        self.student_entry = ctk.CTkEntry(self.action_frame, placeholder_text="Mã sinh viên", fg_color="#0f172a", border_color="#475569")
        self.student_entry.grid(row=0, column=1, padx=10, pady=15, sticky="ew")
        self.student_entry.bind("<KeyRelease>", self.handle_student_typing)
        
        ctk.CTkLabel(self.action_frame, text="Mã sách (ISBN):").grid(row=0, column=2, padx=15, pady=15, sticky="w")
        self.isbn_entry = ctk.CTkEntry(self.action_frame, placeholder_text="Mã sách (ISBN)", fg_color="#0f172a", border_color="#475569")
        self.isbn_entry.grid(row=0, column=3, padx=10, pady=15, sticky="ew")
        self.isbn_entry.bind("<KeyRelease>", self.handle_isbn_typing)
        
        ctk.CTkLabel(self.action_frame, text="Hạn trả dự kiến:").grid(row=0, column=4, padx=15, pady=15, sticky="w")
        
        # Tùy chỉnh giao diện DateEntry bên trong một CTkFrame để tạo cảm giác giống với CTkEntry nguyên bản của CustomTkinter
        self.date_frame = ctk.CTkFrame(
            self.action_frame, 
            fg_color="#0f172a", 
            border_color="#475569", 
            border_width=1, 
            corner_radius=6,
            height=30
        )
        self.date_frame.grid(row=0, column=5, padx=10, pady=15, sticky="ew")
        self.date_frame.pack_propagate(False)
        
        from tkcalendar import DateEntry
        self.due_date_entry = DateEntry(
            self.date_frame,
            width=12,
            background='#3b82f6',          # Calendar Header Background (Blue)
            foreground='white',             # Calendar Header Text
            headersbackground='#0f172a',     # Calendar Weekday Headers
            headersforeground='#DCE4EE',     # Weekday text
            selectbackground='#3b82f6',     # Selected Day highlight
            selectforeground='white',
            
            # Entry text area styling matching CTkEntry properties
            bg='#0f172a',                   
            fg='#DCE4EE',                   
            insertbackground='#DCE4EE',     
            relief='flat',
            borderwidth=0,
            
            # Dropdown Calendar look and feel (Premium Dark Theme)
            normalbackground='#1e293b',     
            normalforeground='#DCE4EE',     
            weekendbackground='#111827',    
            weekendforeground='#ff7043',    
            othermonthbackground='#0f172a', 
            othermonthforeground='#555555', 
            
            date_pattern='yyyy-mm-dd',
            font=("Segoe UI", 11)
        )
        self.due_date_entry.pack(fill="both", expand=True, padx=8, pady=3)
        
        btn_frame = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        btn_frame.grid(row=0, column=6, padx=15, pady=15, sticky="e")

        self.issue_btn = ctk.CTkButton(
            btn_frame, text="Cho Mượn", command=self.handle_borrow, width=100,
            fg_color="#3b82f6", hover_color="#2563eb", font=ctk.CTkFont(weight="bold")
        )
        self.issue_btn.pack(side="left", padx=(0, 10))
        
        # Khung xổ xuống (Dropdown) chứa các gợi ý tìm kiếm. Được đặt trực tiếp trên giao diện gốc (self) để có thể hiển thị đè lên các tab bên dưới.
        self.student_dropdown = ctk.CTkScrollableFrame(self, height=120, width=300, fg_color="#1e293b", border_width=1, border_color="#475569")
        self.isbn_dropdown = ctk.CTkScrollableFrame(self, height=120, width=300, fg_color="#1e293b", border_width=1, border_color="#475569")

        # Khu vực kết hợp thanh tìm kiếm và các nút chức năng mở rộng
        search_frame_top = ctk.CTkFrame(self, fg_color="transparent")
        search_frame_top.pack(fill="x", pady=(0, 10), padx=5)

        # Vùng tìm kiếm bên trái màn hình
        self.search_entry = ctk.CTkEntry(
            search_frame_top, 
            placeholder_text="🔍 Tìm kiếm phiếu mượn (đang mượn & quá hạn)...", 
            width=400,
            fg_color="#1e293b",
            border_color="#475569"
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.handle_search_realtime)
        
        self.search_btn = ctk.CTkButton(
            search_frame_top, text="Tìm kiếm", command=self.handle_search, width=100,
            fg_color="#3b82f6", hover_color="#2563eb"
        )
        self.search_btn.pack(side="left", padx=(0, 10))

        self.refresh_btn = ctk.CTkButton(
            search_frame_top, text="Làm mới", command=self.refresh_list, width=100,
            fg_color="#475569", hover_color="#334155"
        )
        self.refresh_btn.pack(side="left")

        # Vùng nút chức năng bên phải màn hình (Nút trả sách được thiết kế màu xanh lá cây nổi bật)
        self.return_btn = ctk.CTkButton(
            search_frame_top, text="Xem Đơn / Trả Sách", 
            command=self.handle_return_selected, 
            width=160, fg_color="#10b981", hover_color="#059669",
            font=ctk.CTkFont(weight="bold")
        )
        self.return_btn.pack(side="right")

        # Tạo hệ thống Tabs để chia lịch sử mượn trả thành các nhóm: Đang mượn, Quá hạn và Lịch sử
        self.tabs = ctk.CTkTabview(
            self,
            fg_color="#1e293b",
            segmented_button_selected_color="#3b82f6",
            segmented_button_selected_hover_color="#2563eb",
            segmented_button_unselected_color="#0f172a",
            segmented_button_fg_color="#0f172a"
        )
        self.tabs.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.tab_active = self.tabs.add("Đang mượn")
        self.tab_overdue = self.tabs.add("Quá hạn")
        self.tab_history = self.tabs.add("Lịch sử")
        
        # Khởi tạo các Bảng dữ liệu (Data Tables) tương ứng cho từng Tab
        columns = ("id", "student_id", "isbn", "borrow_date", "due_date", "status")
        
        self.active_table = DataTable(self.tab_active, columns=columns)
        self.active_table.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.overdue_table = DataTable(self.tab_overdue, columns=columns)
        self.overdue_table.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.history_table = DataTable(self.tab_history, columns=columns)
        self.history_table.pack(fill="both", expand=True, padx=10, pady=10)
        
        for table in [self.active_table, self.overdue_table, self.history_table]:
            table.tree.heading("id", text="ID")
            table.tree.heading("student_id", text="Mã SV")
            table.tree.heading("isbn", text="Mã Sách")
            table.tree.heading("borrow_date", text="Ngày Mượn")
            table.tree.heading("due_date", text="Ngày Trả (Dự kiến)")
            table.tree.heading("status", text="Trạng Thái")
            
            table.set_column_width("id", 60)
            table.set_column_width("student_id", 150)
            table.set_column_width("isbn", 180)
            table.set_column_width("borrow_date", 150)
            table.set_column_width("due_date", 180)
            table.set_column_width("status", 150)
            
            table.tree.tag_configure("active", foreground="#f59e0b")   # Amber/Orange
            table.tree.tag_configure("overdue", foreground="#ef4444")  # Rose/Red
            table.tree.tag_configure("returned", foreground="#10b981") # Emerald/Green

        # Kích hoạt tính năng click đúp chuột (Double-click) vào hàng dữ liệu để xem/trả sách
        self.active_table.tree.bind("<Double-1>", self.on_row_double_click)
        self.overdue_table.tree.bind("<Double-1>", self.on_row_double_click)
        self.history_table.tree.bind("<Double-1>", self.on_row_double_click)
        
        self.refresh_list()

    def on_row_double_click(self, event):
        # Cho phép người dùng click đúp chuột để xem đơn trả hoặc trả sách
        current_tab = self.tabs.get()
        selected = None
        if current_tab == "Đang mượn":
            selected = self.active_table.get_selected()
        elif current_tab == "Quá hạn":
            selected = self.overdue_table.get_selected()
        elif current_tab == "Lịch sử":
            selected = self.history_table.get_selected()
            
        if selected:
            self.show_return_slip_dialog(selected[0])

    def handle_return_selected(self):
        current_tab = self.tabs.get()
        selected = None
        if current_tab == "Đang mượn":
            selected = self.active_table.get_selected()
        elif current_tab == "Quá hạn":
            selected = self.overdue_table.get_selected()
        elif current_tab == "Lịch sử":
            selected = self.history_table.get_selected()
            
        if not selected:
            show_custom_warning(self, "Chọn phiếu mượn", "Vui lòng chọn một phiếu mượn từ bảng để tiếp tục.")
            return
            
        slip_id = selected[0]
        self.show_return_slip_dialog(slip_id)

    def handle_student_typing(self, event):
        query = self.student_entry.get().strip()
        if not query:
            self.student_dropdown.place_forget()
            return
            
        students = self.student_ctrl.search_students(query)
        
        for widget in self.student_dropdown.winfo_children():
            widget.destroy()
            
        if not students:
            self.student_dropdown.place_forget()
            return
            
        for s in students[:5]:
            btn = ctk.CTkButton(
                self.student_dropdown, text=f"{s.student_id} - {s.name}",
                anchor="w", fg_color="transparent", hover_color=("gray70", "gray30"),
                text_color=("black", "white"),
                command=lambda s=s: self.select_student(s)
            )
            btn.pack(fill="x", pady=2)
            
        self.student_dropdown.place(in_=self.student_entry, rely=1.0, x=0, y=2)
        self.student_dropdown.lift()

    def select_student(self, student):
        self.student_entry.delete(0, 'end')
        self.student_entry.insert(0, student.student_id)
        self.student_dropdown.place_forget()

    def handle_isbn_typing(self, event):
        query = self.isbn_entry.get().strip()
        if not query:
            self.isbn_dropdown.place_forget()
            return
            
        books = self.book_ctrl.search_books(query)
        
        for widget in self.isbn_dropdown.winfo_children():
            widget.destroy()
            
        if not books:
            self.isbn_dropdown.place_forget()
            return
            
        for b in books[:5]:
            btn = ctk.CTkButton(
                self.isbn_dropdown, text=f"{b.isbn} - {b.name}",
                anchor="w", fg_color="transparent", hover_color=("gray70", "gray30"),
                text_color=("black", "white"),
                command=lambda b=b: self.select_book(b)
            )
            btn.pack(fill="x", pady=2)
            
        self.isbn_dropdown.place(in_=self.isbn_entry, rely=1.0, x=0, y=2)
        self.isbn_dropdown.lift()

    def select_book(self, book):
        self.isbn_entry.delete(0, 'end')
        self.isbn_entry.insert(0, book.isbn)
        self.isbn_dropdown.place_forget()

    def handle_borrow(self):
        sid = self.student_entry.get().strip()
        isbn = self.isbn_entry.get().strip()
        due_date = self.due_date_entry.get_date()
        
        if sid and isbn:
            if " - " in sid: sid = sid.split(" - ")[0]
            if " - " in isbn: isbn = isbn.split(" - ")[0]
            
            success, msg = self.controller.borrow_book(sid, isbn, expected_return=due_date)
            if success:
                self.refresh_list()
                if self.on_refresh:
                    self.on_refresh()
                self.student_entry.delete(0, 'end')
                self.isbn_entry.delete(0, 'end')
                show_custom_info(self, "Thành công", "Mượn sách thành công.")
            else:
                show_custom_error(self, "Lỗi Mượn Sách", msg)
        else:
            show_custom_warning(self, "Lỗi Nhập Liệu", "Vui lòng nhập cả Mã sinh viên và Mã sách (ISBN).")

    def show_return_slip_dialog(self, slip_id):
        from views.components.return_slip_dialog import ReturnSlipDialog
        dialog = ReturnSlipDialog(self.winfo_toplevel(), slip_id, on_success_callback=self.on_transaction_success)

    def on_transaction_success(self):
        self.refresh_list()
        if self.on_refresh:
            self.on_refresh()

    def handle_search_realtime(self, event):
        self.handle_search()

    def handle_search(self):
        query = self.search_entry.get().strip()
        if not query:
            self.refresh_list()
            return
            
        slips = self.controller.search_slips(query)
        self.populate_lists(slips)
        
        # Khi thực hiện tìm kiếm, hệ thống sẽ tự động chuyển hướng người dùng sang tab "Đang mượn" - nơi hiển thị kết quả tìm kiếm gộp
        self.tabs.set("Đang mượn")

    def refresh_list(self):
        self.search_entry.delete(0, 'end')
        slips = self.controller.get_active_slips() + self.controller.get_history_slips()
        self.populate_lists(slips)

    def populate_lists(self, all_slips):
        self.active_table.clear()
        self.overdue_table.clear()
        self.history_table.clear()
        
        is_searching = bool(self.search_entry.get().strip())
        
        for slip in all_slips:
            status_tag = "overdue" if slip.status == "Overdue" else ("returned" if slip.status == "Returned" else "active")
            status_vn = "Quá hạn" if slip.status == "Overdue" else ("Đã trả" if slip.status == "Returned" else "Đang mượn")
            
            row_data = (slip.id, slip.student_id, slip.book_isbn, slip.borrow_date, slip.expected_return_date, status_vn)
            
            if is_searching:
                # Nếu đang trong chế độ tìm kiếm, gộp cả 2 trạng thái "Đang mượn" và "Quá hạn" vào chung bảng active_table để hiển thị dễ dàng hơn
                if slip.status in ["Borrowed", "Overdue"]:
                    self.active_table.insert(row_data, tags=(status_tag,))
                else:
                    self.history_table.insert(row_data, tags=(status_tag,))
            else:
                # Nếu không tìm kiếm, phân loại và hiển thị dữ liệu bình thường theo từng tab riêng biệt
                if slip.status == "Borrowed":
                    self.active_table.insert(row_data, tags=(status_tag,))
                elif slip.status == "Overdue":
                    self.overdue_table.insert(row_data, tags=(status_tag,))
                else:
                    self.history_table.insert(row_data, tags=(status_tag,))
