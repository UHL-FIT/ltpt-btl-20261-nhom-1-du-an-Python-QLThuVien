# ==============================================================================
# Tệp: utils/styling.py
# Mục đích: Chứa các tham số cấu hình tĩnh (Constant) dùng cho Giao diện.
# Chức năng:
# - Cấu hình bảng màu chuẩn.
# - Cấu hình font chữ, kích thước, và tên theme (Giao diện mẫu).
# ==============================================================================

class StyleConfig:
    # Lớp tiện ích cấu hình tham số tĩnh (không cần khởi tạo)
    
    PRIMARY = "#4e73df" # Xanh lam chủ đạo (cho các nút lệnh chính)
    SECONDARY = "#858796"
    SUCCESS = "#1cc88a"
    INFO = "#36b9cc"
    WARNING = "#f6c23e"
    DANGER = "#e74a3b"
    DARK = "#5a5c69"    # Xám đậm
    LIGHT = "#f8f9fc"   # Trắng/xám nhạt

    # Font chữ
    FONT_FAMILY = "Segoe UI"
    HEADER_SIZE = 18
    BODY_SIZE = 10

    # Theme (Giao diện) mặc định
    THEME_NAME = "cosmo"  


def apply_custom_styles(root):
    # Khối chức năng có thể được mở rộng sau này, 
    # hiện tại là hàm trống để dự trù áp dụng các tuỳ biến ttk widget.
    pass