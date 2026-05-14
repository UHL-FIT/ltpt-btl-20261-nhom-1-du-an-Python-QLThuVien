# ==============================================================================
# Tệp: seed_db.py
# Mục đích: Tập lệnh (Script) tự động tạo dữ liệu mẫu (mock data) cho hệ thống.
# Chức năng:
# - Xóa toàn bộ dữ liệu cũ trong cơ sở dữ liệu nếu đã tồn tại.
# - Sử dụng thư viện Faker để sinh ra thông tin giả mạo nhưng chân thực (Tên người Việt, Email, SĐT).
# - Tạo 1,000 Sinh viên, 100 Cuốn sách với mã ISBN thực tế, và 3,000 Phiếu mượn ngẫu nhiên.
# - Rất hữu ích trong quá trình phát triển (development) và kiểm thử (testing).
# ==============================================================================
from database.db_manager import init_db, get_session
from models.book import Book
from models.borrow_slip import BorrowSlip
from models.student import Student
from sqlalchemy import text
from faker import Faker
import datetime
import random

def seed_data():
    # Hàm thực thi chính để xóa dữ liệu cũ và chèn dữ liệu mẫu mới vào cơ sở dữ liệu.
    
    # Bước 1: Khởi tạo database (đảm bảo các bảng đã được tạo)
    init_db()
    
    # Mở phiên làm việc
    session = get_session()
    
    # Check if data already exists
    if session.query(Book).count() > 0 or session.query(Student).count() > 0:
        print("Dữ liệu đã tồn tại. Đang xóa dữ liệu cũ để tạo mới...")
        session.query(BorrowSlip).delete()
        session.query(Book).delete()
        session.query(Student).delete()
        
        # Xóa dữ liệu ở bảng FTS để tránh rác nếu trigger không xử lý hết khi bulk delete
        session.execute(text("DELETE FROM books_fts"))
        session.execute(text("DELETE FROM students_fts"))
        session.execute(text("DELETE FROM borrow_slips_fts"))
        
        session.commit()

    print("Đang tạo 1,000 sinh viên...")
    fake = Faker('vi_VN')
    
    students = []
    student_ids = []
    for i in range(1000):
        sid = f"SV{10000 + i}"
        student_ids.append(sid)
        students.append(Student(
            student_id=sid,
            name=fake.name(),
            email=fake.email(),
            phone=fake.phone_number()
        ))
        
    session.bulk_save_objects(students)
    session.commit()

    print("Đang tạo 100 sách...")
    genres = ['Tiểu thuyết', 'Khoa học', 'Bí ẩn', 'Lãng mạn', 'Kỹ năng sống', 'Lịch sử', 'Giả tưởng', 'Kinh điển', 'Kinh dị', 'Thiếu nhi']
    
    books = []
    isbns = set()
    while len(isbns) < 100:
        isbns.add(fake.isbn13(separator="-"))
        
    isbns = list(isbns)
    
    for i in range(100):
        title = fake.sentence(nb_words=5).replace('.', '')
        books.append(Book(
            isbn=isbns[i],
            name=title.title(),
            genre=random.choice(genres),
            status="Available"
        ))
        
    session.bulk_save_objects(books)
    session.commit()
    
    print("Đang tạo 3,000 phiếu mượn...")
    all_books = session.query(Book).all()
    books_to_borrow = random.choices(all_books, k=3000)
    
    slips = []
    today = datetime.date.today()
    
    # Tạo danh sách trạng thái cố định: 30 Đang mượn, 10 Quá hạn, 2960 Đã trả
    statuses = ["Borrowed"] * 30 + ["Overdue"] * 10 + ["Returned"] * 2960
    random.shuffle(statuses)
    
    borrowed_book_isbns = set()
    
    for idx, book in enumerate(books_to_borrow):
        status = statuses[idx]
        actual_return_date = None
        
        if status == "Borrowed":
            # Ngày trả dự kiến ở tương lai (đang mượn)
            expected_return_date = today + datetime.timedelta(days=random.randint(1, 14))
            borrow_date = expected_return_date - datetime.timedelta(days=14)
            borrowed_book_isbns.add(book.isbn)
        elif status == "Overdue":
            # Ngày trả dự kiến ở quá khứ (quá hạn)
            expected_return_date = today - datetime.timedelta(days=random.randint(1, 30))
            borrow_date = expected_return_date - datetime.timedelta(days=14)
            borrowed_book_isbns.add(book.isbn)
        else:
            # Đã trả xong
            borrow_date = fake.date_between(start_date="-1y", end_date="-15d")
            expected_return_date = borrow_date + datetime.timedelta(days=14)
            actual_return_date = fake.date_between(start_date=borrow_date, end_date=today)
            
        slip = BorrowSlip(
            student_id=random.choice(student_ids),
            book_isbn=book.isbn,
            borrow_date=borrow_date,
            expected_return_date=expected_return_date,
            actual_return_date=actual_return_date,
            status=status
        )
        slips.append(slip)
        
    # Cập nhật trạng thái sách trong DB dựa vào các sách thực sự đang mượn
    for book in all_books:
        if book.isbn in borrowed_book_isbns:
            book.status = "Borrowed"
        else:
            book.status = "Available"
        
    session.bulk_save_objects(slips)
    session.commit()
    
    session.close()
    print("Dữ liệu mẫu (Tiếng Việt) đã được tạo thành công.")

if __name__ == "__main__":
    seed_data()
