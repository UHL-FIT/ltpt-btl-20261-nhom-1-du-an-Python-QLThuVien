from unidecode import unidecode
from sqlalchemy import create_engine, text, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

def remove_vietnamese_accents(text_val):
    if text_val is None:
        return ""
    return unidecode(str(text_val))

Base = declarative_base()
engine = create_engine('sqlite:///library.db')

@event.listens_for(engine, "connect")
def receive_connect(dbapi_connection, connection_record):
    dbapi_connection.create_function("unaccent", 1, remove_vietnamese_accents)

Session = sessionmaker(bind=engine)

def setup_fts(connection):
    # Setup FTS5 for books
    connection.execute(text('''
        CREATE VIRTUAL TABLE IF NOT EXISTS books_fts USING fts5(
            isbn, name, genre,
            tokenize='unicode61 remove_diacritics 1'
        );
    '''))
    connection.execute(text('''
        CREATE TRIGGER IF NOT EXISTS books_ai AFTER INSERT ON books BEGIN
            INSERT INTO books_fts(rowid, isbn, name, genre) VALUES (new.rowid, unaccent(new.isbn), unaccent(new.name), unaccent(new.genre));
        END;
    '''))
    connection.execute(text('''
        CREATE TRIGGER IF NOT EXISTS books_ad AFTER DELETE ON books BEGIN
            DELETE FROM books_fts WHERE rowid = old.rowid;
        END;
    '''))
    connection.execute(text('''
        CREATE TRIGGER IF NOT EXISTS books_au AFTER UPDATE ON books BEGIN
            UPDATE books_fts SET 
                isbn = unaccent(new.isbn), 
                name = unaccent(new.name), 
                genre = unaccent(new.genre)
            WHERE rowid = old.rowid;
        END;
    '''))
    
    # Setup FTS5 for students
    connection.execute(text('''
        CREATE VIRTUAL TABLE IF NOT EXISTS students_fts USING fts5(
            student_id, name, email, phone,
            tokenize='unicode61 remove_diacritics 1'
        );
    '''))
    connection.execute(text('''
        CREATE TRIGGER IF NOT EXISTS students_ai AFTER INSERT ON students BEGIN
            INSERT INTO students_fts(rowid, student_id, name, email, phone) VALUES (new.rowid, unaccent(new.student_id), unaccent(new.name), unaccent(new.email), unaccent(new.phone));
        END;
    '''))
    connection.execute(text('''
        CREATE TRIGGER IF NOT EXISTS students_ad AFTER DELETE ON students BEGIN
            DELETE FROM students_fts WHERE rowid = old.rowid;
        END;
    '''))
    connection.execute(text('''
        CREATE TRIGGER IF NOT EXISTS students_au AFTER UPDATE ON students BEGIN
            UPDATE students_fts SET 
                student_id = unaccent(new.student_id), 
                name = unaccent(new.name), 
                email = unaccent(new.email), 
                phone = unaccent(new.phone)
            WHERE rowid = old.rowid;
        END;
    '''))
    
    # Setup FTS5 for borrow_slips
    connection.execute(text('''
        CREATE VIRTUAL TABLE IF NOT EXISTS borrow_slips_fts USING fts5(
            id, student_id, book_isbn, status,
            tokenize='unicode61 remove_diacritics 1'
        );
    '''))
    connection.execute(text('''
        CREATE TRIGGER IF NOT EXISTS borrow_slips_ai AFTER INSERT ON borrow_slips BEGIN
            INSERT INTO borrow_slips_fts(rowid, id, student_id, book_isbn, status) VALUES (new.id, unaccent(new.id), unaccent(new.student_id), unaccent(new.book_isbn), unaccent(new.status));
        END;
    '''))
    connection.execute(text('''
        CREATE TRIGGER IF NOT EXISTS borrow_slips_ad AFTER DELETE ON borrow_slips BEGIN
            DELETE FROM borrow_slips_fts WHERE rowid = old.id;
        END;
    '''))
    connection.execute(text('''
        CREATE TRIGGER IF NOT EXISTS borrow_slips_au AFTER UPDATE ON borrow_slips BEGIN
            UPDATE borrow_slips_fts SET 
                id = unaccent(new.id), 
                student_id = unaccent(new.student_id), 
                book_isbn = unaccent(new.book_isbn), 
                status = unaccent(new.status)
            WHERE rowid = old.id;
        END;
    '''))
    
    # Rebuild standalone FTS tables
    connection.execute(text("DELETE FROM books_fts;"))
    connection.execute(text('''
        INSERT INTO books_fts(rowid, isbn, name, genre) 
        SELECT rowid, unaccent(isbn), unaccent(name), unaccent(genre) FROM books;
    '''))
    
    connection.execute(text("DELETE FROM students_fts;"))
    connection.execute(text('''
        INSERT INTO students_fts(rowid, student_id, name, email, phone) 
        SELECT rowid, unaccent(student_id), unaccent(name), unaccent(email), unaccent(phone) FROM students;
    '''))
    
    connection.execute(text("DELETE FROM borrow_slips_fts;"))
    connection.execute(text('''
        INSERT INTO borrow_slips_fts(rowid, id, student_id, book_isbn, status) 
        SELECT id, unaccent(id), unaccent(student_id), unaccent(book_isbn), unaccent(status) FROM borrow_slips;
    '''))

def init_db():
    import models.book
    import models.borrow_slip
    import models.student
    Base.metadata.create_all(engine)
    with engine.begin() as conn:
        setup_fts(conn)

def get_session():
    return Session()
