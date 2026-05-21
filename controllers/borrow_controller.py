# ==============================================================================
# Tệp: controllers/borrow_controller.py
# Mục đích: Xử lý nghiệp vụ phức tạp liên quan đến mượn sách, trả sách và quản lý các phiếu mượn.
# Chức năng chính:
# - Tạo phiếu mượn mới, đồng thời cập nhật trạng thái của Sách thành "Đang mượn".
# - Xử lý việc trả sách: cập nhật trạng thái phiếu mượn, cập nhật ngày trả thực tế và đặt lại trạng thái Sách.
# - Theo dõi và phân loại các phiếu mượn: đang mượn, đã trả, hoặc quá hạn.
# ==============================================================================
from database.db_manager import get_session
from models.borrow_slip import BorrowSlip
from models.book import Book
import datetime

class BorrowController:
    # Lớp điều khiển các thao tác dữ liệu cho giao dịch Mượn/Trả sách.
    
    def borrow_book(self, student_id, book_isbn, expected_return=None):
        # Hàm xử lý nghiệp vụ mượn sách.
        # Các bước xử lý:
        # 1. Kiểm tra sách có tồn tại và đang "Sẵn sàng" không.
        # 2. Tạo một phiếu mượn (BorrowSlip) mới.
        # 3. Cập nhật trạng thái sách thành "Đã mượn" (Borrowed).
        
        session = get_session()
        # Lấy thông tin sách dựa vào ISBN
        book = session.query(Book).filter_by(isbn=book_isbn).first()
        
        # Kiểm tra tính hợp lệ của sách
        if not book or getattr(book, "status") != "Available":
            session.close()
            return False, "Sách hiện tại đã có người mượn hoặc không tồn tại."
            
        try:
            # Xử lý ngày trả dự kiến (expected_return)
            if expected_return is None:
                # Mặc định cho mượn 14 ngày nếu không có ngày cụ thể
                expected_return = datetime.date.today() + datetime.timedelta(days=14)
            elif isinstance(expected_return, str):
                # Chuyển đổi chuỗi ngày tháng sang đối tượng kiểu Date
                expected_date = datetime.datetime.strptime(expected_return, "%Y-%m-%d").date()
                expected_return = expected_date
                
            # Tạo bản ghi phiếu mượn mới
            slip = BorrowSlip(
                student_id=student_id,
                book_isbn=book_isbn,
                expected_return_date=expected_return
            )
            
            # Cập nhật trạng thái sách để người khác không mượn được nữa
            book.status = "Borrowed"
            
            # Thêm phiếu mượn vào session và lưu (commit)
            session.add(slip)
            session.commit()
            return True, "Mượn sách thành công!"
        except Exception as e:
            # Nếu có lỗi, hoàn tác lại (rollback) để tránh sai lệch dữ liệu
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    def get_slip(self, slip_id):
        """Lấy thông tin của một phiếu mượn cụ thể thông qua ID."""
        session = get_session()
        slip = session.query(BorrowSlip).get(slip_id)
        if slip:
            # detach to safely use outside session if needed, but easier to just extract dict
            data = {
                "id": slip.id,
                "status": slip.status,
                "expected_return_date": slip.expected_return_date
            }
        else:
            data = None
        return data

    def return_book(self, slip_id):
        """
        Xử lý nghiệp vụ trả sách.
        Cập nhật ngày trả thực tế, trạng thái phiếu mượn và trạng thái sách thành 'Available'.
        """
        session = get_session()
        slip = session.query(BorrowSlip).get(slip_id)
        if slip and getattr(slip, "status") in ["Borrowed", "Overdue"]:
            slip.actual_return_date = datetime.date.today()
            slip.status = "Returned"
            
            book = session.query(Book).filter_by(isbn=slip.book_isbn).first()
            if book:
                book.status = "Available"
                
            session.commit()
            session.close()
            return True
        return False

    def check_and_update_overdue(self):
        """
        Quét toàn bộ phiếu mượn đang ở trạng thái 'Borrowed' (Đang mượn)
        nhưng có expected_return_date nhỏ hơn ngày hiện tại,
        và cập nhật trạng thái của chúng thành 'Overdue' (Quá hạn).
        """
        session = get_session()
        today = datetime.date.today()
        try:
            # Tối ưu hóa bằng Bulk Update trực tiếp trên SQL thay vì tải vòng lặp Python
            updated_count = session.query(BorrowSlip).filter(
                BorrowSlip.status == "Borrowed",
                BorrowSlip.expected_return_date < today
            ).update({"status": "Overdue"}, synchronize_session=False)
            
            if updated_count > 0:
                session.commit()
        except Exception as e:
            session.rollback()
            print("Lỗi khi cập nhật trạng thái quá hạn:", e)
        finally:
            session.close()

    def get_active_slips(self):
        """Lấy danh sách các phiếu mượn đang hoạt động (chưa trả sách)."""
        session = get_session()
        slips = session.query(BorrowSlip).filter(BorrowSlip.status == "Borrowed").all()
        return slips

    def get_history_slips(self):
        """Lấy lịch sử các phiếu mượn (đã trả hoặc quá hạn)."""
        session = get_session()
        from sqlalchemy import or_
        slips = session.query(BorrowSlip).filter(or_(BorrowSlip.status == "Returned", BorrowSlip.status == "Overdue")).all()
        return slips
        
    def get_all_slips_for_view(self):
        """Tối ưu hóa: Kiểm tra quá hạn 1 lần duy nhất và lấy toàn bộ phiếu mượn để view tự phân loại."""
        self.check_and_update_overdue()
        session = get_session()
        slips = session.query(BorrowSlip).all()
        return slips

    def search_slips(self, query):
        """
        Tìm kiếm phiếu mượn bằng FTS5 (Full-Text Search).
        Hỗ trợ tìm kiếm không phân biệt dấu.
        """
        self.check_and_update_overdue()
        from sqlalchemy import text
        from database.db_manager import remove_vietnamese_accents
        session = get_session()
        if not query.strip():
            return self.get_active_slips()
            
        normalized_query = remove_vietnamese_accents(query)
        search_term = f"\"{normalized_query}\"*"
        sql = text("SELECT id FROM borrow_slips_fts WHERE borrow_slips_fts MATCH :query")
        result = session.execute(sql, {"query": search_term}).fetchall()
        
        if not result:
            session.close()
            return []
            
        slip_ids = [r[0] for r in result]
        slips = session.query(BorrowSlip).filter(BorrowSlip.id.in_(slip_ids)).all()
        session.close()
        return slips

