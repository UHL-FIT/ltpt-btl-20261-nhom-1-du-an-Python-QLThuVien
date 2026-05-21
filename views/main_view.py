# ==============================================================================
# Tệp: views/main_view.py
# Mục đích: Định nghĩa giao diện chính (Dashboard) của phần mềm quản lý thư viện.
# Chức năng:
# - Tạo khung điều hướng (Sidebar) với các nút bấm chức năng.
# - Dùng làm khung chứa (Container) để chuyển đổi giữa các màn hình (Views) khác nhau.
# ==============================================================================
import customtkinter as ctk
import time
from views.book_view import BookView
from views.borrow_view import BorrowView
from views.stats_view import StatsView
from views.student_view import StudentView
from utils.analysis import DataAnalyzer
from views.components.custom_dialog import show_custom_info, show_custom_error, show_custom_warning, show_custom_askyesno

class MainView:
    # Lớp giao diện điều hướng chính của ứng dụng.
    
    def __init__(self, root):
        self.root = root
        
        # Thiết lập nền tối Slate Dark cho cửa sổ chính
        self.root.configure(fg_color="#0f172a")
        
        # Cache lưu trữ các View đã khởi tạo để tránh load lại từ đầu
        self.views_cache = {}
        
        # Trạng thái theo dõi View hiện tại đang hoạt động
        self.active_view_key = None
        self.active_view = None
        
        # Cờ báo hiệu dữ liệu trong hệ thống có thay đổi (thêm, sửa, xóa, mượn, trả)
        self.data_changed = True
        
        # Trạng thái đóng/mở của thanh Sidebar
        self.sidebar_expanded = True
        
        # Thiết lập UI chính
        self.setup_ui()
        
        # Hiển thị mặc định màn hình sách khi khởi động
        self.show_books()

    def setup_ui(self):
        # Khởi tạo thanh điều hướng (Sidebar) ở bên trái màn hình
        self.sidebar = ctk.CTkFrame(self.root, width=240, corner_radius=0, fg_color="#1e293b")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False) # Giữ nguyên độ rộng của sidebar khi co giãn

        # Khung chứa logo và nút toggle đóng/mở sidebar
        self.logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.logo_frame.pack(fill="x", pady=(20, 30), padx=10)

        self.logo_label = ctk.CTkLabel(
            self.logo_frame, text="LMS-PRO X",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#3b82f6"
        )
        self.logo_label.pack(side="left", padx=10)

        self.toggle_btn = ctk.CTkButton(
            self.logo_frame, text="☰", width=35, height=35,
            fg_color="transparent", hover_color=("gray70", "gray30"),
            text_color="gray90", font=ctk.CTkFont(size=18, weight="bold"),
            command=self.toggle_sidebar
        )
        self.toggle_btn.pack(side="right")

        # Khởi tạo các nút điều hướng cơ bản
        self.books_btn = self.create_nav_btn("📚 Quản lý Sách", self.show_books)
        self.students_btn = self.create_nav_btn("🎓 Quản lý Học sinh", self.show_students)
        self.borrow_btn = self.create_nav_btn("🔄 Quản lý Mượn Trả", self.show_borrowing)
        self.stats_btn = self.create_nav_btn("📊 Thống kê & Phân tích", self.show_stats)
        self.credit_btn = self.create_nav_btn("💡 Giới thiệu", self.show_credit)

        # Lưu ánh xạ nút và văn bản/icon phục vụ đóng mở sidebar
        self.nav_buttons = {
            "books": self.books_btn,
            "students": self.students_btn,
            "borrow": self.borrow_btn,
            "stats": self.stats_btn,
            "credit": self.credit_btn
        }
        
        self.nav_info = {
            "books": {"text": "Quản lý Sách", "icon": "📚"},
            "students": {"text": "Quản lý Học sinh", "icon": "🎓"},
            "borrow": {"text": "Quản lý Mượn Trả", "icon": "🔄"},
            "stats": {"text": "Thống kê & Phân tích", "icon": "📊"},
            "credit": {"text": "Giới thiệu", "icon": "💡"}
        }

        # Khởi tạo nút Xuất Dữ Liệu ở cuối sidebar
        self.export_btn = ctk.CTkButton(
            self.sidebar, text="Xuất dữ liệu ra Excel",
            fg_color="#3b82f6", hover_color="#2563eb",
            command=self.handle_export,
            font=ctk.CTkFont(weight="bold")
        )
        self.export_btn.pack(side="bottom", pady=20, padx=15, fill="x")

        # Khu vực hiển thị nội dung chính của ứng dụng (Main Content Area)
        self.content_area = ctk.CTkFrame(
            self.root, corner_radius=0, fg_color="transparent"
        )
        self.content_area.pack(
            side="right", fill="both", expand=True, padx=25, pady=25
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

    def toggle_sidebar(self):
        self.sidebar_expanded = not self.sidebar_expanded
        
        target_width = 240 if self.sidebar_expanded else 70
        self.sidebar.configure(width=target_width)
        
        if self.sidebar_expanded:
            self.logo_label.pack(side="left", padx=10)
            self.toggle_btn.pack(side="right")
            self.export_btn.configure(text="Xuất dữ liệu ra Excel")
        else:
            self.logo_label.pack_forget()
            self.toggle_btn.pack(side="top", pady=5)
            self.export_btn.configure(text="📥")
            
        self.update_button_states()

    def update_button_states(self, force_collapsed=False):
        # Cập nhật văn bản, biểu tượng, căn lề và màu sắc của các nút dựa trên trạng thái active & đóng mở
        is_collapsed = not self.sidebar_expanded or force_collapsed
        for key, btn in self.nav_buttons.items():
            info = self.nav_info[key]
            
            # Cấu hình text dựa theo độ rộng Sidebar
            if not is_collapsed:
                btn_text = f"{info['icon']}  {info['text']}"
                btn_anchor = "w"
            else:
                btn_text = info['icon']
                btn_anchor = "center"
                
            # Cấu hình màu sắc dựa theo tab active (bỏ qua nút giới thiệu)
            if key == self.active_view_key and key != "credit":
                btn.configure(
                    text=btn_text,
                    anchor=btn_anchor,
                    fg_color="#3b82f6",
                    text_color="#ffffff",
                    font=ctk.CTkFont(size=14, weight="bold")
                )
            else:
                btn.configure(
                    text=btn_text,
                    anchor=btn_anchor,
                    fg_color="transparent",
                    text_color="gray90",
                    font=ctk.CTkFont(size=14, weight="normal")
                )

    def switch_view(self, view_key, view_class):
        # Lưu key của view active
        self.active_view_key = view_key
        
        # Ẩn view đang hiển thị hiện tại (không destroy)
        if self.active_view:
            self.active_view.pack_forget()
            
        # Khởi tạo view mới nếu chưa có trong Cache
        if view_key not in self.views_cache:
            self.views_cache[view_key] = view_class(self.content_area, on_refresh=self.notify_data_changed)
            
        # Hiển thị view tương ứng
        self.active_view = self.views_cache[view_key]
        self.active_view.pack(fill="both", expand=True)
        
        # Nếu chuyển sang tab Thống kê và dữ liệu hệ thống đã thay đổi, tự động refresh
        if view_key == "stats":
            if self.data_changed and hasattr(self.active_view, "refresh_stats"):
                self.active_view.refresh_stats()
                self.data_changed = False
                
        self.update_button_states()

    def notify_data_changed(self):
        # Đánh dấu cờ dữ liệu đã thay đổi khi các view thực hiện thao tác ghi
        self.data_changed = True
        # Tự động refresh danh sách các view khác nếu chúng đã được khởi tạo trong cache
        # Điều này đảm bảo dữ liệu hiển thị trên các bảng luôn được đồng bộ ngay lập tức
        for key, view in self.views_cache.items():
            if key != self.active_view_key and hasattr(view, "refresh_list"):
                view.refresh_list()

    def handle_export(self):
        import datetime
        from tkinter import filedialog
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"Library_Report_{timestamp}.xlsx"
        
        filepath = filedialog.asksaveasfilename(
            title="Lưu báo cáo hệ thống",
            initialfile=default_filename,
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if not filepath:
            return
            
        try:
            DataAnalyzer.export_to_excel(filepath)
            show_custom_info(self.root, "Thành công", f"Dữ liệu đã được xuất ra tệp:\n{filepath}")
        except Exception as e:
            show_custom_error(self.root, "Lỗi", str(e))
 
    def show_books(self):
        self.switch_view("books", BookView)
 
    def show_students(self):
        self.switch_view("students", StudentView)
 
    def show_borrowing(self):
        self.switch_view("borrow", BorrowView)
 
    def show_stats(self):
        self.switch_view("stats", StatsView)
 
    def show_credit(self):
        show_custom_info(
            self.root,
            "Thông tin Sản Phẩm",        
            "Phần mềm quản lý thư viện LMS-PRO X\nPhiên bản : 0.5-beta (Modernized UI)\n\nTác Giả:\n- Bùi Ngọc Lâm\n- Đỗ Mạnh Cường\n- Đặng Minh Thành\n- Nguyễn Văn Tuấn\n\nHướng dẫn: ThS. Vũ Duy Sơn"
        )