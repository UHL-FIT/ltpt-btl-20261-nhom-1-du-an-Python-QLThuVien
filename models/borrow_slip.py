# ==============================================================================
# Tệp: models/borrow_slip.py
# Mục đích: Định nghĩa bảng 'borrow_slips' (Phiếu mượn sách) trong cơ sở dữ liệu.
# Chức năng:
# - Lưu vết mọi giao dịch mượn/trả sách.
# - Thiết lập khóa ngoại (Foreign Key) liên kết với bảng Sách để kiểm tra tính toàn vẹn dữ liệu.
# ==============================================================================
from typing import Literal
from sqlalchemy import String, Integer, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from database.db_manager import Base
import datetime


class BorrowSlip(Base):
    # Lớp BorrowSlip lưu lại lịch sử mượn và trạng thái mượn hiện tại của một cuốn sách do một sinh viên mượn.
    
    __tablename__ = 'borrow_slips' # Khai báo bảng
    
    # Cột id: ID định danh của phiếu mượn. Thuộc tính autoincrement=True giúp tự động tăng số ID mà không cần truyền vào.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Cột student_id: Lưu mã sinh viên mượn sách (không đặt khóa ngoại cứng để linh hoạt trong trường hợp xóa sinh viên)
    student_id: Mapped[str] = mapped_column(String, nullable=False)
    
    # Cột book_isbn: Lưu mã sách (ISBN). Đây là khóa ngoại tham chiếu đến cột 'isbn' của bảng 'books'. Bắt buộc phải có.
    book_isbn: Mapped[str] = mapped_column(String, ForeignKey('books.isbn'), nullable=False)
    
    # Cột borrow_date: Ngày bắt đầu mượn. Mặc định là ngày tạo phiếu (datetime.date.today)
    borrow_date: Mapped[datetime.date] = mapped_column(Date, default=datetime.date.today)
    
    # Cột expected_return_date: Hạn trả dự kiến do người quản lý chọn hoặc hệ thống tự tính.
    expected_return_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    
    # Cột actual_return_date: Ngày khách hàng mang sách tới trả thực tế. Có thể trống (None) nếu sách vẫn đang được mượn.
    actual_return_date: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    
    # Cột status: Trạng thái tiến trình của phiếu mượn (Đang mượn, Đã trả, Quá hạn). Mặc định là 'Borrowed'.
    status: Mapped[Literal["Borrowed", "Returned", "Overdue"]] = mapped_column(String, default="Borrowed")

    def __repr__(self):
        # Hàm trả về chuỗi log
        return f"<BorrowSlip(student_id='{self.student_id}', book='{self.book_isbn}', status='{self.status}')>"
