# ==============================================================================
# Tệp: models/student.py
# Mục đích: Định nghĩa cấu trúc bảng 'students' (Sinh viên/Độc giả) trong cơ sở dữ liệu.
# Chức năng:
# - Ánh xạ lớp Student thành bảng CSDL.
# - Định nghĩa mã sinh viên (student_id) làm khóa chính.
# ==============================================================================
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from database.db_manager import Base


class Student(Base):
    # Lớp Student lưu thông tin của một người mượn sách.
    # Kế thừa từ lớp Base để kết nối với kiến trúc ORM.
    
    __tablename__ = 'students' # Tên bảng vật lý trong CSDL là 'students'
    
    # Cột student_id: Mã số sinh viên. Định dạng là khóa chính để định danh duy nhất.
    student_id: Mapped[str] = mapped_column(String, primary_key=True)
    
    # Cột name: Tên đầy đủ của sinh viên. Bắt buộc phải có (nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    
    # Cột email: Địa chỉ email liên hệ. Có thể trống (nullable=True)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    
    # Cột phone: Số điện thoại liên hệ. Có thể trống (nullable=True)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)

    def __repr__(self):
        # Trả về chuỗi đại diện ngắn gọn của sinh viên giúp in ra log dễ đọc
        return f"<Student(name='{self.name}', student_id='{self.student_id}')>"
