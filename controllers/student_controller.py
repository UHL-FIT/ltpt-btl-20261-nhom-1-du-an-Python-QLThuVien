# ==============================================================================
# Tệp: controllers/student_controller.py
# Mục đích: Xử lý các logic trung gian (Controller) đối với sinh viên/độc giả.
# Chức năng chính: 
# - Xử lý thêm, cập nhật, xóa thông tin sinh viên bằng session SQLAlchemy.
# - Quản lý việc truy vấn Full-Text Search giúp tìm kiếm sinh viên linh hoạt.
# ==============================================================================
from database.db_manager import get_session
from models.student import Student
from sqlalchemy import text


class StudentController:
    # Lớp điều khiển xử lý logic riêng biệt của mô đun Sinh viên.
    
    def import_students_from_df(self, df):
        """
        Import sinh viên hàng loạt từ DataFrame pandas.
        Trả về: (success_count, skipped_count, error_msg)
        """
        import pandas as pd
        # Chuẩn hóa tên cột
        id_col = None
        name_col = None
        email_col = None
        phone_col = None
        
        for col in df.columns:
            c_low = str(col).lower().strip()
            if "student_id" in c_low or "mã sv" in c_low or "ma sv" in c_low or "mã sinh viên" in c_low or "ma sinh vien" in c_low or "mã số" in c_low or "ma so" in c_low or "id" == c_low:
                id_col = col
            elif "họ tên" in c_low or "ho ten" in c_low or "tên" in c_low or "ten" in c_low or "name" in c_low or "họ và tên" in c_low or "ho va ten" in c_low:
                name_col = col
            elif "email" in c_low or "thư điện tử" in c_low or "thu dien tu" in c_low:
                email_col = col
            elif "phone" in c_low or "sđt" in c_low or "sdt" in c_low or "điện thoại" in c_low or "dien thoai" in c_low or "số đt" in c_low or "so dt" in c_low:
                phone_col = col
                
        if not id_col or not name_col:
            return 0, 0, "Không tìm thấy cột 'Mã SV' hoặc 'Họ Tên' hợp lệ trong tệp Excel."
            
        session = get_session()
        success_count = 0
        skipped_count = 0
        try:
            # Lấy tập hợp student_id hiện có để kiểm tra trùng lặp nhanh
            existing_ids = {s[0] for s in session.query(Student.student_id).all()}
            
            for _, row in df.iterrows():
                sid = str(row[id_col]).strip()
                name = str(row[name_col]).strip()
                email = str(row[email_col]).strip() if (email_col and pd.notna(row[email_col])) else ""
                phone = str(row[phone_col]).strip() if (phone_col and pd.notna(row[phone_col])) else ""
                
                # Định dạng số điện thoại nếu cần (bỏ số thập phân từ excel nếu có)
                if phone.endswith(".0"):
                    phone = phone[:-2]
                if sid.endswith(".0"):
                    sid = sid[:-2]
                
                # Bỏ qua các hàng trống mã hoặc tên
                if not sid or sid == "nan" or not name or name == "nan":
                    skipped_count += 1
                    continue
                    
                if sid in existing_ids:
                    skipped_count += 1
                    continue
                    
                # Tạo student mới
                new_student = Student(student_id=sid, name=name, email=email if email != "nan" else "", phone=phone if phone != "nan" else "")
                session.add(new_student)
                existing_ids.add(sid)
                success_count += 1
                
            session.commit()
            return success_count, skipped_count, None
        except Exception as e:
            session.rollback()
            return 0, 0, str(e)
        finally:
            session.close()

    def add_student(self, student_id, name, email, phone):
        # Hàm khởi tạo và thêm một sinh viên mới.
        
        # Bước 1: Lấy session để giao tiếp với cơ sở dữ liệu
        session = get_session()
        try:
            # Bước 2: Khởi tạo đối tượng Student
            new_student = Student(student_id=student_id, name=name, email=email, phone=phone)
            
            # Bước 3: Thêm sinh viên vào session
            session.add(new_student)
            
            # Bước 4: Lưu thay đổi và giải phóng khóa bảo vệ
            session.commit()
            return True, "Thêm sinh viên thành công!"
        except Exception as e:
            # Nếu gặp lỗi (mã sinh viên đã tồn tại, lỗi kết nối..), hoàn tác transaction
            session.rollback()
            return False, str(e)
        finally:
            # Dọn dẹp session
            session.close()

    def update_student(self, old_id, new_id, name, email, phone):
        """Cập nhật thông tin của một sinh viên/độc giả."""
        session = get_session()
        try:
            student = session.query(Student).filter_by(student_id=old_id).first()
            if student:
                student.student_id = new_id
                student.name = name
                student.email = email
                student.phone = phone
                session.commit()
                return True, "Cập nhật sinh viên thành công!"
            return False, "Không tìm thấy sinh viên"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    def get_all_students(self):
        """Lấy toàn bộ danh sách sinh viên/độc giả trong CSDL."""
        session = get_session()
        students = session.query(Student).all()
        return students

    def search_students(self, query):
        """
        Tìm kiếm sinh viên/độc giả bằng FTS5 (Full-Text Search).
        Hỗ trợ tìm kiếm không dấu qua từ khóa truyền vào.
        """
        from database.db_manager import remove_vietnamese_accents
        session = get_session()
        if not query.strip():
            return self.get_all_students()
            
        normalized_query = remove_vietnamese_accents(query)
        search_term = f"\"{normalized_query}\"*"  # FTS5 prefix search
        
        sql = text("SELECT student_id FROM students_fts WHERE students_fts MATCH :query")
        result = session.execute(sql, {"query": search_term}).fetchall()
        
        if not result:
            session.close()
            return []
            
        student_ids = [r[0] for r in result]
        students = session.query(Student).filter(Student.student_id.in_(student_ids)).all()
        
        return students

    def delete_student(self, student_id):
        """Xóa sinh viên khỏi hệ thống dựa theo mã sinh viên."""
        session = get_session()
        student = session.query(Student).filter_by(student_id=student_id).first()
        if student:
            session.delete(student)
            session.commit()
            session.close()
            return True
        session.close()
        return False
