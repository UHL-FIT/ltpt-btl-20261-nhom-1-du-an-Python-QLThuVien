# ==============================================================================
# Tệp: controllers/book_controller.py
# Mục đích: Đóng vai trò là Bộ điều khiển (Controller) cho thực thể Sách (Book).
# Chức năng: Xử lý các logic nghiệp vụ liên quan đến sách bao gồm:
# - Thêm sách mới vào CSDL.
# - Cập nhật thông tin sách hiện có.
# - Lấy danh sách tất cả các sách.
# - Tìm kiếm sách theo từ khóa (FTS5).
# - Xóa sách khỏi CSDL.
# Controller giúp tách biệt hoàn toàn Giao diện người dùng (View) khỏi logic thao tác Dữ liệu (Model).
# ==============================================================================

from database.db_manager import get_session
from models.book import Book


class BookController:
    # Lớp điều khiển các thao tác dữ liệu cho đối tượng Book.
    
    def add_book(self, isbn, name, genre):
        # Hàm thêm một cuốn sách mới vào cơ sở dữ liệu.
        # Nhận đầu vào là mã sách (isbn), tên sách (name) và thể loại (genre).
        
        # Bước 1: Mở một phiên làm việc mới với cơ sở dữ liệu
        session = get_session()
        try:
            # Bước 2: Tạo một thể hiện (instance) mới của lớp Book với dữ liệu đầu vào
            new_book = Book(isbn=isbn, name=name, genre=genre)
            
            # Bước 3: Thêm đối tượng mới vào phiên giao dịch hiện tại
            session.add(new_book)
            
            # Bước 4: Lưu (commit) thay đổi xuống cơ sở dữ liệu thực sự
            session.commit()
            
            # Trả về cờ True (thành công) và thông báo
            return True, "Thêm sách thành công!"
        except Exception as e:
            # Nếu có lỗi (ví dụ: trùng mã ISBN), hủy bỏ toàn bộ các thay đổi trong phiên (rollback)
            session.rollback()
            # Trả về cờ False (thất bại) và chuỗi lỗi
            return False, str(e)
        finally:
            # Luôn đảm bảo đóng phiên làm việc để giải phóng kết nối tới cơ sở dữ liệu
            session.close()

    def update_book(self, old_isbn, new_isbn, name, genre):
        """Cập nhật thông tin sách hiện có."""
        session = get_session()
        try:
            book = session.query(Book).filter_by(isbn=old_isbn).first()
            if book:
                book.isbn = new_isbn
                book.name = name
                book.genre = genre
                session.commit()
                return True, "Cập nhật sách thành công!"
            return False, "Không tìm thấy sách"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    def get_all_books(self):
        """Lấy danh sách tất cả các cuốn sách."""
        session = get_session()
        books = session.query(Book).all()
        return books

    def search_books(self, query):
        """
        Tìm kiếm sách dựa trên chuỗi truy vấn.
        Sử dụng tính năng Full-Text Search (FTS5) qua bảng ảo books_fts.
        """
        from sqlalchemy import text
        from database.db_manager import remove_vietnamese_accents
        session = get_session()
        if not query.strip():
            return self.get_all_books()
            
        normalized_query = remove_vietnamese_accents(query)
        search_term = f"\"{normalized_query}\"*"
        sql = text("SELECT isbn FROM books_fts WHERE books_fts MATCH :query")
        result = session.execute(sql, {"query": search_term}).fetchall()
        
        if not result:
            session.close()
            return []
            
        isbns = [r[0] for r in result]
        books = session.query(Book).filter(Book.isbn.in_(isbns)).all()
        return books

    def delete_book(self, isbn):
        """Xóa sách khỏi cơ sở dữ liệu dựa vào mã ISBN."""
        session = get_session()
        book = session.query(Book).filter_by(isbn=isbn).first()
        if book:
            session.delete(book)
            session.commit()
            session.close()
            return True
        session.close()
        return False
