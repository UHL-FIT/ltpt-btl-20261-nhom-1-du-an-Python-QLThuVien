# ==============================================================================
# Tệp: main.py
# Mục đích: Đây là tệp thực thi chính (entry point) của ứng dụng quản lý thư viện LMS-PRO X.
# Chức năng chính:
# 1. Kết nối và khởi tạo cơ sở dữ liệu SQLite ngay khi ứng dụng bắt đầu.
# 2. Cấu hình giao diện đồ họa sử dụng thư viện CustomTkinter.
# 3. Khởi tạo đối tượng cửa sổ chính (MainView) và bắt đầu vòng lặp sự kiện (mainloop).
# ==============================================================================

import customtkinter as ctk
from database.db_manager import init_db
from views.main_view import MainView
from utils.debug_logger import setup_debug_logger

import sys

def main():
    # Kích hoạt hệ thống Debug Logger thời gian thực nếu có tham số devmode
    if "--devmode" in sys.argv or "devmode" in sys.argv:
        setup_debug_logger()
    
    # Bước 1: Khởi tạo cơ sở dữ liệu
    # Gọi hàm init_db() từ db_manager để tạo các bảng (books, students, borrow_slips) nếu chưa tồn tại
    # và thiết lập các tính năng tìm kiếm Full-Text Search (FTS5).
    init_db()
    
    # Bước 2: Thiết lập giao diện người dùng (UI)
    # Cấu hình giao diện CustomTkinter sang chế độ giao diện Dark Mode (Nền tối) giúp bảo vệ mắt
    ctk.set_appearance_mode("Dark")  # Các chế độ hỗ trợ: "System" (Hệ thống), "Dark" (Tối), "Light" (Sáng)
    # Cài đặt chủ đề màu sắc mặc định là "blue" (các nút bấm, thanh tiến trình sẽ có màu xanh)
    ctk.set_default_color_theme("blue") 
    
    # Bước 3: Tạo cửa sổ ứng dụng chính
    # Khởi tạo đối tượng CTk, đóng vai trò là cửa sổ (window) gốc của ứng dụng
    app = ctk.CTk()
    # Thiết lập tiêu đề hiển thị trên thanh tiêu đề của cửa sổ
    app.title("Phần mềm quản lý thư viện LMS-PRO X")
    # Thiết lập kích thước mặc định của cửa sổ là 1700 pixel chiều rộng và 900 pixel chiều cao
    app.geometry("1700x900") 
    
    # Bước 4: Khởi tạo Giao diện (View) chính
    # Truyền đối tượng cửa sổ gốc 'app' vào lớp MainView để xây dựng các thành phần UI bên trong (Sidebar, Content area)
    MainView(app)
    
    # Bước 5: Chạy vòng lặp sự kiện
    # Gọi mainloop() để ứng dụng luôn mở và chờ đợi các thao tác từ người dùng (như click chuột, gõ phím)
    app.mainloop()

# Khối lệnh này kiểm tra xem file có đang được chạy trực tiếp không.
# Nếu chạy trực tiếp (python main.py), hàm main() sẽ được gọi.
if __name__ == "__main__":
    main()
