from database.db_manager import get_session
from models.student import Student
from sqlalchemy import text


class StudentController:
    def add_student(self, student_id, name, email, phone):
        session = get_session()
        try:
            new_student = Student(student_id=student_id, name=name, email=email, phone=phone)
            session.add(new_student)
            session.commit()
            return True, "Thêm sinh viên thành công!"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    def update_student(self, old_id, new_id, name, email, phone):
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
        session = get_session()
        students = session.query(Student).all()
        session.close()
        return students

    def search_students(self, query):
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
        
        session.close()
        return students

    def delete_student(self, student_id):
        session = get_session()
        student = session.query(Student).filter_by(student_id=student_id).first()
        if student:
            session.delete(student)
            session.commit()
            session.close()
            return True
        session.close()
        return False
