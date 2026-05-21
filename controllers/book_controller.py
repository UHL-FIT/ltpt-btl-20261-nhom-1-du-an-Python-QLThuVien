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
    
    def import_books_from_df(self, df):
        """
        Import sách hàng loạt từ DataFrame pandas.
        Trả về: (success_count, skipped_count, error_msg)
        """
        import pandas as pd
        # Chuẩn hóa tên cột
        isbn_col = None
        name_col = None
        genre_col = None
        
        for col in df.columns:
            c_low = str(col).lower().strip()
            if "isbn" in c_low or "mã sách" in c_low or "ma sach" in c_low:
                isbn_col = col
            elif "tên sách" in c_low or "ten sach" in c_low or "tên" in c_low or "ten" in c_low or "name" in c_low or "tiêu đề" in c_low or "tieu de" in c_low:
                name_col = col
            elif "thể loại" in c_low or "the loai" in c_low or "genre" in c_low or "nhóm" in c_low or "nhom" in c_low:
                genre_col = col
                
        if not isbn_col or not name_col:
            return 0, 0, "Không tìm thấy cột 'Mã Sách' (ISBN) hoặc 'Tên Sách' hợp lệ trong tệp Excel."
            
        session = get_session()
        success_count = 0
        skipped_count = 0
        try:
            # Lấy tập hợp ISBN hiện có để kiểm tra trùng lặp nhanh
            existing_isbns = {b[0] for b in session.query(Book.isbn).all()}
            
            for _, row in df.iterrows():
                isbn = str(row[isbn_col]).strip()
                name = str(row[name_col]).strip()
                genre = str(row[genre_col]).strip() if (genre_col and pd.notna(row[genre_col])) else ""
                
                # Bỏ qua các hàng trống mã hoặc tên
                if not isbn or isbn == "nan" or not name or name == "nan":
                    skipped_count += 1
                    continue
                    
                if isbn in existing_isbns:
                    skipped_count += 1
                    continue
                    
                # Tạo book mới
                new_book = Book(isbn=isbn, name=name, genre=genre, status="Available")
                session.add(new_book)
                existing_isbns.add(isbn)
                success_count += 1
                
            session.commit()
            return success_count, skipped_count, None
        except Exception as e:
            session.rollback()
            return 0, 0, str(e)
        finally:
            session.close()

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
