from database.db_manager import get_session
from models.book import Book


class BookController:
    def add_book(self, isbn, name, genre):
        session = get_session()
        try:
            new_book = Book(isbn=isbn, name=name, genre=genre)
            session.add(new_book)
            session.commit()
            return True, "Book added successfully!"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    def get_all_books(self):
        session = get_session()
        books = session.query(Book).all()
        session.close()
        return books

    def search_books(self, query):
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
        session.close()
        return books

    def delete_book(self, isbn):
        session = get_session()
        book = session.query(Book).filter_by(isbn=isbn).first()
        if book:
            session.delete(book)
            session.commit()
            session.close()
            return True
        session.close()
        return False
