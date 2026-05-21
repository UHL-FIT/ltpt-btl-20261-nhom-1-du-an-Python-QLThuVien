# ==============================================================================
# Tệp: views/components/return_slip_dialog.py
# Mục đích: Định nghĩa hộp thoại "Đơn trả sách" chi tiết.
# Chức năng:
# - Hiển thị thông tin người mượn, sách, ngày mượn, hạn trả và ngày trả thực tế.
# - Tính toán và hiển thị số ngày quá hạn, tiền phạt (100.000 VNĐ / ngày).
# - Hỗ trợ nút trả sách đối với phiếu chưa trả và hiển thị thông tin lịch sử đối với phiếu cũ.
# ==============================================================================
import customtkinter as ctk
import datetime
from database.db_manager import get_session
from models.student import Student
from models.book import Book
from models.borrow_slip import BorrowSlip
from views.components.custom_dialog import show_custom_info, show_custom_error

class ReturnSlipDialog(ctk.CTkToplevel):
    def __init__(self, master, slip_id, on_success_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.title("Đơn trả sách - LMS-PRO X")
        self.geometry("540x720")
        self.resizable(True, True)
        self.configure(fg_color="#0f172a") # Slate Dark
        
        # Safe cast slip_id to integer
        try:
            self.slip_id = int(slip_id)
        except (ValueError, TypeError):
            self.slip_id = slip_id
            
        self.on_success_callback = on_success_callback
        self.confirmed = False
        
        # Modal configuration
        self.transient(master)
        self.grab_set()
        self.attributes("-topmost", True)
        
        # Center relative to master
        self.update_idletasks()
        try:
            master_x = master.winfo_rootx()
            master_y = master.winfo_rooty()
            master_w = master.winfo_width()
            master_h = master.winfo_height()
            x = master_x + (master_w - 540) // 2
            y = master_y + (master_h - 720) // 2
            self.geometry(f"+{x}+{y}")
        except Exception:
            self.geometry("540x720+450+150")
        
        # Load details & setup UI
        self.load_details()
        self.setup_ui()

    def load_details(self):
        session = get_session()
        try:
            self.slip = session.query(BorrowSlip).get(self.slip_id)
            if not self.slip:
                # Fallback values
                self.student_id = "N/A"
                self.student_name = "N/A"
                self.book_isbn = "N/A"
                self.book_name = "N/A"
                self.borrow_date = datetime.date.today()
                self.expected_return_date = datetime.date.today()
                self.actual_return_date = None
                self.status = "N/A"
                self.overdue_days = 0
                self.is_overdue = False
                self.fine = 0
                return
                
            # Get student and book details
            student = session.query(Student).filter_by(student_id=self.slip.student_id).first()
            book = session.query(Book).filter_by(isbn=self.slip.book_isbn).first()
            
            self.student_id = str(self.slip.student_id)
            self.student_name = str(student.name) if student else "Độc giả không xác định"
            self.book_isbn = str(self.slip.book_isbn)
            self.book_name = str(book.name) if book else "Sách không xác định"
            
            # Date properties might be strings or date objects depending on DB load state
            self.borrow_date = self.parse_date(self.slip.borrow_date) or datetime.date.today()
            self.expected_return_date = self.parse_date(self.slip.expected_return_date) or datetime.date.today()
            self.actual_return_date = self.parse_date(self.slip.actual_return_date) if self.slip.actual_return_date else None
            self.status = str(self.slip.status)
            
            # Overdue analysis
            end_date = self.actual_return_date if self.actual_return_date else datetime.date.today()
            
            if end_date > self.expected_return_date:
                self.overdue_days = (end_date - self.expected_return_date).days
                self.is_overdue = True
                self.fine = self.overdue_days * 100000 # 100,000 VND fine per day
            else:
                self.overdue_days = 0
                self.is_overdue = False
                self.fine = 0
        finally:
            session.close()

    def parse_date(self, val):
        if not val:
            return None
        if isinstance(val, str):
            try:
                return datetime.datetime.strptime(val.split(" ")[0], "%Y-%m-%d").date()
            except Exception:
                try:
                    return datetime.date.fromisoformat(val.split(" ")[0])
                except Exception:
                    return datetime.date.today()
        if isinstance(val, datetime.datetime):
            return val.date()
        if isinstance(val, datetime.date):
            return val
        return val

    def setup_ui(self):
        # Outer Border Frame
        main_frame = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=12, border_color="#3b82f6", border_width=1)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Title of Receipt
        receipt_title = ctk.CTkLabel(
            main_frame, text="ĐƠN TRẢ SÁCH / PHIẾU GIAO DỊCH",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#3b82f6"
        )
        receipt_title.pack(pady=(20, 5))
        
        sub_title = ctk.CTkLabel(
            main_frame, text=f"Mã phiếu mượn: #{self.slip_id}",
            font=ctk.CTkFont(size=12, weight="normal"),
            text_color="#94a3b8"
        )
        sub_title.pack(pady=(0, 15))
        
        # Separator line 1
        sep1 = ctk.CTkFrame(main_frame, height=1, fg_color="#334155")
        sep1.pack(fill="x", padx=20, pady=(0, 15))
        
        # 1. BUTTON LAYOUT packed first at bottom to guarantee visibility
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(side="bottom", fill="x", pady=(10, 20))
        
        if not self.actual_return_date:
            # Action: Return Book
            cancel_btn = ctk.CTkButton(
                btn_frame, text="Hủy bỏ", width=120, fg_color="#475569", hover_color="#334155",
                font=ctk.CTkFont(weight="bold"), command=self.on_cancel
            )
            cancel_btn.pack(side="left", padx=25)
            
            confirm_btn = ctk.CTkButton(
                btn_frame, text="Xác nhận Trả Sách", width=165, fg_color="#10b981", hover_color="#059669",
                font=ctk.CTkFont(weight="bold"), command=self.on_confirm_return
            )
            confirm_btn.pack(side="right", padx=25)
        else:
            # Review only
            close_btn = ctk.CTkButton(
                btn_frame, text="Đóng", width=130, fg_color="#3b82f6", hover_color="#2563eb",
                font=ctk.CTkFont(weight="bold"), command=self.on_cancel
            )
            close_btn.pack(pady=5)
            
        # 2. INFORMATION LAYOUT FRAME packed next, fills remaining space
        info_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        info_frame.pack(fill="both", expand=True, padx=25, pady=(0, 10))
        
        # Helper to create key-value rows inside info_frame
        def add_info_row(label_text, value_text, value_color="#f8fafc"):
            row = ctk.CTkFrame(info_frame, fg_color="transparent")
            row.pack(fill="x", pady=5)
            lbl = ctk.CTkLabel(row, text=label_text, font=ctk.CTkFont(size=13), text_color="#94a3b8")
            lbl.pack(side="left")
            val = ctk.CTkLabel(row, text=str(value_text), font=ctk.CTkFont(size=13, weight="bold"), text_color=value_color, anchor="e")
            val.pack(side="right")
            
        add_info_row("Mã sinh viên:", self.student_id)
        add_info_row("Tên người mượn:", self.student_name, "#3b82f6")
        add_info_row("Mã sách (ISBN):", self.book_isbn)
        add_info_row("Tên sách:", self.book_name, "#10b981")
        add_info_row("Ngày mượn:", self.borrow_date.strftime("%Y-%m-%d"))
        add_info_row("Hạn trả dự kiến:", self.expected_return_date.strftime("%Y-%m-%d"))
        
        # Actual return date / Status
        if self.actual_return_date:
            add_info_row("Ngày trả thực tế:", self.actual_return_date.strftime("%Y-%m-%d"), "#10b981")
            status_text = "Đã trả"
            status_color = "#10b981"
        else:
            add_info_row("Ngày trả thực tế:", "Chưa trả (Đang mượn)", "#f59e0b")
            status_text = "Đang mượn" if self.status == "Borrowed" else "Quá hạn"
            status_color = "#f59e0b" if self.status == "Borrowed" else "#ef4444"
            
        add_info_row("Trạng thái:", status_text, status_color)
        
        # Separator line 2 inside info_frame
        sep2 = ctk.CTkFrame(info_frame, height=1, fg_color="#334155")
        sep2.pack(fill="x", pady=12)
        
        # Overdue detail rows
        overdue_lbl = "Có" if self.is_overdue else "Không"
        overdue_color = "#ef4444" if self.is_overdue else "#10b981"
        add_info_row("Có quá hạn hay không:", overdue_lbl, overdue_color)
        
        if self.is_overdue:
            add_info_row("Số ngày quá hạn:", f"{self.overdue_days} ngày", "#ef4444")
            add_info_row("Tiền phạt tương ứng:", f"{self.fine:,.0f} VNĐ", "#ef4444")
        else:
            add_info_row("Số ngày quá hạn:", "0 ngày", "#10b981")
            add_info_row("Tiền phạt tương ứng:", "0 VNĐ", "#10b981")

    def on_confirm_return(self):
        from controllers.borrow_controller import BorrowController
        ctrl = BorrowController()
        if ctrl.return_book(self.slip_id):
            self.confirmed = True
            show_custom_info(self, "Thành công", "Đã trả sách và lưu đơn trả thành công.")
            self.grab_release()
            self.destroy()
            if self.on_success_callback:
                self.on_success_callback()
        else:
            show_custom_error(self, "Lỗi", "Không thể xử lý trả sách.")
            
    def on_cancel(self):
        self.grab_release()
        self.destroy()
