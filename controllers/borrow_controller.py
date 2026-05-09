from database.db_manager import get_session
from models.borrow_slip import BorrowSlip
from models.book import Book
import datetime


class BorrowController:
    def borrow_book(self, student_id, book_isbn, expected_return=None):
        session = get_session()
        book = session.query(Book).filter_by(isbn=book_isbn).first()
        
        if not book or getattr(book, "status") != "Available":
            session.close()
            return False, "Sách hiện tại đã có người mượn."
            
        try:
            if expected_return is None:
                expected_return = datetime.date.today() + datetime.timedelta(days=14)
            elif isinstance(expected_return, str):
                expected_date = datetime.datetime.strptime(expected_return, "%Y-%m-%d").date()
                expected_return = expected_date
                
            slip = BorrowSlip(
                student_id=student_id,
                book_isbn=book_isbn,
                expected_return_date=expected_return
            )
            book.status = "Borrowed"
            session.add(slip)
            session.commit()
            return True, "Mượn sách thành công!"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    def get_slip(self, slip_id):
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
        session.close()
        return data

    def return_book(self, slip_id):
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
        session.close()
        return False

    def get_active_slips(self):
        session = get_session()
        slips = session.query(BorrowSlip).filter(BorrowSlip.status == "Borrowed").all()
        session.close()
        return slips

    def get_history_slips(self):
        session = get_session()
        from sqlalchemy import or_
        slips = session.query(BorrowSlip).filter(or_(BorrowSlip.status == "Returned", BorrowSlip.status == "Overdue")).all()
        session.close()
        return slips

    def search_slips(self, query):
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
