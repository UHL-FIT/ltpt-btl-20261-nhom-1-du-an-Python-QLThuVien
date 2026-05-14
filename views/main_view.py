# ==============================================================================
# Tệp: views/main_view.py
# Mục đích: Định nghĩa giao diện chính (Dashboard) của phần mềm quản lý thư viện.
# Chức năng:
# - Tạo khung điều hướng (Sidebar) với các nút bấm chức năng.
# - Dùng làm khung chứa (Container) để chuyển đổi giữa các màn hình (Views) khác nhau.
# ==============================================================================
import customtkinter as ctk
from views.book_view import BookView
from views.borrow_view import BorrowView
from views.stats_view import StatsView
from views.student_view import StudentView
from utils.analysis import DataAnalyzer
from tkinter import messagebox

class MainView:
    # Lớp giao diện điều hướng chính của ứng dụng.
    
    def __init__(self, root):
        # Lưu trữ đối tượng cửa sổ gốc
        self.root = root
        
        # Biến theo dõi view hiện tại đang hiển thị
        self.active_view = None
        
        # Khởi tạo giao diện
        self.setup_ui()
        
        # Hiển thị mặc định màn hình sách khi vừa bật app
        self.show_books()

    def setup_ui(self):
        # Khởi tạo thanh điều hướng (Sidebar) ở bên trái màn hình
        self.sidebar = ctk.CTkFrame(self.root, width=240, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        self.logo_label = ctk.CTkLabel(
            self.sidebar, text="LMS-PRO X",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#1f538d"
        )
        self.logo_label.pack(pady=(30, 40))

        # Khởi tạo các nút bấm chức năng trên thanh điều hướng
        self.books_btn = self.create_nav_btn("📚 Quản lý Sách", self.show_books)
        self.students_btn = self.create_nav_btn ("🎓 Quản lý Học sinh", self.show_students)
        self.borrow_btn = self.create_nav_btn("🔄 Quản lý Mượn Trả", self.show_borrowing)
        self.stats_btn = self.create_nav_btn("📊 Thống kê & Phân tích", self.show_stats)
        self.credit_btn = self.create_nav_btn("ℹ️ Giới thiệu", self.show_credit)

        # Khởi tạo nút Xuất Dữ Liệu và đặt nó ở vị trí dưới cùng của thanh điều hướng
        self.export_btn = ctk.CTkButton(
            self.sidebar, text="Xuất dữ liệu ra Excel",
            fg_color="#1f538d", hover_color="#14375e",
            command=self.handle_export
        )
        self.export_btn.pack(side="bottom", pady=20, padx=20, fill="x")

        # Khu vực hiển thị nội dung chính của ứng dụng (Main Content Area)
        self.content_area = ctk.CTkFrame(
            self.root, corner_radius=0, fg_color="transparent"
        )
        self.content_area.pack(
            side="right", fill="both", expand=True, padx=30, pady=30
        )
        
    def create_nav_btn(self, text, command):
        btn = ctk.CTkButton(
            self.sidebar, text=text, command=command,
            fg_color="transparent", anchor="w",
            text_color="gray90",
            hover_color=("gray70", "gray30"),
            font=ctk.CTkFont(size=14)
        )
        btn.pack(fill="x", padx=10, pady=5)
        return btn

    def switch_view(self, view_class):
        # Hàm xử lý logic chuyển đổi giữa các màn hình (Views) khác nhau.
        
        # Bước 1: Xóa toàn bộ nội dung cũ trong khu vực hiển thị (content_area)
        for widget in self.content_area.winfo_children():
            widget.destroy()

        # Bước 2: Khởi tạo view mới từ class được truyền vào và gắn nó vào content_area
        self.active_view = view_class(self.content_area, on_refresh=None)
        self.active_view.pack(fill="both", expand=True)

    def handle_export(self):
        try:
            DataAnalyzer.export_to_excel("Library_Report.xlsx")
            messagebox.showinfo("Thành công", "Dữ liệu đã được xuất ra file Library_Report.xlsx thành công.")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def show_books(self):
        self.switch_view(BookView)

    def show_students(self):
        self.switch_view(StudentView)

    def show_borrowing(self):
        self.switch_view(BorrowView)

    def show_stats(self):
        self.switch_view(StatsView)

    def show_credit(self):
        messagebox.showinfo(
            icon="info",
            title="Thông tin Sản Phẩm",        
            message="Phần mềm quản lý thư viện LMS-PRO X",
            detail="Phiên bản : 0.2-alpha\n-----------------------------------\nTác Giả:\n  - Bùi Ngọc Lâm\n  - Đỗ Mạnh Cường\n  - Đặng Minh Thành\n  - Nguyễn Văn Tuấn\nDưới sự hướng dẫn của ThS.Vũ Duy Sơn"
        )