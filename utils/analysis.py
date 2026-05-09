import pandas as pd
from database.db_manager import get_session
from models.book import Book
from models.borrow_slip import BorrowSlip
from datetime import date


class DataAnalyzer:
    @staticmethod
    def get_library_stats():
        from models.student import Student
        session = get_session()
        
        total_books = session.query(Book).count()
        total_students = session.query(Student).count()
        
        # Sách đang mượn vs Sẵn có
        borrowed_books = session.query(Book).filter(Book.status == "Borrowed").count()
        available_books = total_books - borrowed_books
        
        # Phân bố thể loại sách
        genres_data = session.query(Book.genre).all()
        genres_counts = {}
        for g in genres_data:
            if g[0]:
                genres_counts[g[0]] = genres_counts.get(g[0], 0) + 1
            
        slips = session.query(BorrowSlip).all()
        if not slips:
            session.close()
            return {
                "total_books": total_books,
                "total_students": total_students,
                "borrowed_books": borrowed_books,
                "available_books": available_books,
                "total_borrows": 0,
                "overdue_rate": 0,
                "overdue_count": 0,
                "returned_count": 0,
                "popular_books": [],
                "genre_counts": genres_counts,
                "borrows_by_month": {}
            }
        
        df_slips = pd.DataFrame([{
            'isbn': s.book_isbn,
            'status': s.status,
            'borrow_date': s.borrow_date,
            'expected_return': s.expected_return_date
        } for s in slips])
        
        # Top 5 sách mượn nhiều nhất
        most_borrowed = df_slips['isbn'].value_counts().head(5)
        popular_books = []
        for isbn, count in most_borrowed.items():
            book = session.query(Book).filter_by(isbn=isbn).first()
            popular_books.append({"name": book.name if book else isbn, "count": count})
            
        # Tính toán Quá hạn & Đã trả
        overdue_count = len(df_slips[df_slips['status'] == 'Overdue'])
        returned_count = len(df_slips[df_slips['status'] == 'Returned'])
        
        today = date.today()
        today_dt = pd.to_datetime(today)
        currently_late = len(df_slips[(df_slips['status'] == 'Borrowed') & (pd.to_datetime(df_slips['expected_return']) < today_dt)])
        total_overdue = overdue_count + currently_late
        overdue_rate = (total_overdue / len(df_slips)) * 100 if len(df_slips) > 0 else 0
        
        # Lượt mượn theo tháng (6 tháng gần nhất)
        df_slips['month'] = df_slips['borrow_date'].astype(str).str[:7]
        monthly_counts = df_slips['month'].value_counts().sort_index().tail(6)
        borrows_by_month = {str(m): int(val) for m, val in monthly_counts.items()}
        
        session.close()
        
        return {
            "total_books": total_books,
            "total_students": total_students,
            "borrowed_books": borrowed_books,
            "available_books": available_books,
            "total_borrows": len(df_slips),
            "overdue_rate": round(overdue_rate, 2),
            "overdue_count": total_overdue,
            "returned_count": returned_count,
            "popular_books": popular_books,
            "genre_counts": genres_counts,
            "borrows_by_month": borrows_by_month
        }

    @staticmethod
    def export_to_excel(filename="Library_Data.xlsx"):
        session = get_session()
        
        # Export Books
        books = session.query(Book).all()
        df_books = pd.DataFrame([{
            'Mã Sách (ISBN)': b.isbn, 'Tên Sách': b.name, 'Thể Loại': b.genre, 'Trạng Thái': "Có sẵn" if b.status == "Available" else "Đang mượn"
        } for b in books])
        
        # Export Slips
        slips = session.query(BorrowSlip).all()
        df_slips = pd.DataFrame([{
            'ID': s.id, 'Mã Sinh Viên': s.student_id, 'Mã Sách': s.book_isbn,
            'Ngày Mượn': s.borrow_date, 'Ngày Trả Dự Kiến': s.expected_return_date,
            'Ngày Trả Thực Tế': s.actual_return_date, 'Trạng Thái': "Quá hạn" if s.status == "Overdue" else ("Đã trả" if s.status == "Returned" else "Đang mượn")
        } for s in slips])
        
        with pd.ExcelWriter(filename) as writer:
            df_books.to_excel(writer, sheet_name='Danh_Muc_Sach', index=False)
            df_slips.to_excel(writer, sheet_name='Phieu_Muon', index=False)
        
        session.close()
        return True
