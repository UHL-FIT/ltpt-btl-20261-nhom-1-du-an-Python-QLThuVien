# ==============================================================================
# Tệp: models/book.py
# Mục đích: Định nghĩa cấu trúc bảng 'books' (Danh mục Sách) trong cơ sở dữ liệu.
# Chức năng:
# - Sử dụng SQLAlchemy ORM để ánh xạ lớp Book thành một bảng thực tế trong DB.
# - Thiết lập các ràng buộc dữ liệu: khóa chính (Primary Key), các trường bắt buộc (Nullable=False).
# ==============================================================================
from typing import Literal
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from database.db_manager import Base


class Book(Base):
    # Lớp Book đại diện cho một cuốn sách trong thư viện.
    # Kế thừa từ lớp Base của SQLAlchemy để kết nối với DB Engine.
    
    __tablename__ = 'books' # Khai báo tên bảng sẽ được tạo trong cơ sở dữ liệu
    
    # Cột isbn: Mã số chuẩn quốc tế của sách. Đây là Khóa chính (Primary Key), không được phép trùng lặp
    isbn: Mapped[str] = mapped_column(String, primary_key=True)
    
    # Cột name: Tên sách. Đây là trường thông tin Bắt buộc (nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    
    # Cột genre: Thể loại sách. Đây là trường Tùy chọn (nullable=True), có thể để trống (None)
    genre: Mapped[str | None] = mapped_column(String, nullable=True)
    
    # Cột status: Trạng thái hiện tại của sách.
    # Sử dụng kiểu Literal để giới hạn chỉ chấp nhận 3 giá trị: Sẵn sàng, Đã mượn, hoặc Hư hỏng.
    # Mặc định (default) khi tạo sách mới là "Available" (Sẵn sàng)
    status: Mapped[Literal["Available", "Borrowed", "Damaged"]] = mapped_column(String, default="Available")

    def __repr__(self):
        # Hàm __repr__ dùng để hiển thị chuỗi đại diện khi in đối tượng này ra console (tiện cho việc debug)
        return f"<Book(name='{self.name}', isbn='{self.isbn}', status='{self.status}')>"
