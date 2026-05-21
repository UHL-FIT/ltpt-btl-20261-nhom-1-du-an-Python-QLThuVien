# ==============================================================================
# Tệp: utils/analysis.py
# Mục đích: Phân tích dữ liệu trong hệ thống và xuất báo cáo.
# Chức năng chính:
# - Gom nhóm, tính toán các chỉ số thống kê (sách đang mượn, phân bố thể loại).
# - Sử dụng thư viện Pandas để hỗ trợ xử lý dữ liệu và xuất file Excel (.xlsx).
# ==============================================================================
import pandas as pd
from database.db_manager import get_session
from models.book import Book
from models.borrow_slip import BorrowSlip
from models.student import Student
from datetime import date


class DataAnalyzer:
    # Lớp phân tích dữ liệu chứa các phương thức tĩnh (staticmethod) gọi không cần khởi tạo.
    
    @staticmethod
    def get_library_stats():
        # Hàm tính toán và đóng gói một loạt các số liệu thống kê.
        # Trả về một đối tượng Dictionary chứa các cặp key-value để hiển thị lên Dashboard.
        
        session = get_session()
        
        # 1. Tải toàn bộ dữ liệu từ CSDL
        books = session.query(Book).all()
        students = session.query(Student).all()
        slips = session.query(BorrowSlip).all()
        session.close()
        
        total_books = len(books)
        total_students = len(students)
        
        # Tạo mapping để tra cứu nhanh thông tin
        student_map = {str(s.student_id): str(s.name) for s in students}
        book_map = {str(b.isbn): {"name": str(b.name), "genre": str(b.genre), "status": str(b.status)} for b in books}
        
        # Sách đang mượn vs Sẵn có vs Hư hỏng & Phân bố thể loại (Gom vào 1 vòng lặp duy nhất để tối ưu hiệu năng)
        borrowed_books = 0
        damaged_books = 0
        genre_counts = {}
        available_by_genre = {}
        
        for b in books:
            if b.status == "Borrowed":
                borrowed_books += 1
            elif b.status == "Damaged":
                damaged_books += 1
                
            if b.genre:
                genre_counts[b.genre] = genre_counts.get(b.genre, 0) + 1
                if b.status == "Available":
                    available_by_genre[b.genre] = available_by_genre.get(b.genre, 0) + 1
                    
        available_books = total_books - borrowed_books - damaged_books
                
        # Khởi tạo các giá trị mặc định cho thống kê phiếu mượn nếu chưa có phiếu nào
        default_stats = {
            "total_books": total_books,
            "total_students": total_students,
            "borrowed_books": borrowed_books,
            "available_books": available_books,
            "damaged_books": damaged_books,
            "total_borrows": 0,
            "overdue_rate": 0,
            "overdue_count": 0,
            "returned_count": 0,
            "popular_books": [],
            "genre_counts": genre_counts,
            "borrows_by_month": {},
            "top_students": [],
            "slip_status_counts": {"Borrowed": 0, "Returned": 0, "Overdue": 0},
            "return_punctuality": {"OnTime": 0, "Late": 0},
            "fine_trend": {},
            "borrow_by_weekday": {"Thứ 2": 0, "Thứ 3": 0, "Thứ 4": 0, "Thứ 5": 0, "Thứ 6": 0, "Thứ 7": 0, "Chủ Nhật": 0},
            "borrow_by_genre": {},
            "avg_duration_by_genre": {},
            "duration_distribution": {"< 7 ngày": 0, "7-14 ngày": 0, "14-30 ngày": 0, "> 30 ngày": 0},
            "available_by_genre": {},
            "most_overdue_books": []
        }
        
        if not slips:
            return default_stats
            
        # Chuyển đổi phiếu mượn thành DataFrame để phân tích bằng Pandas
        df_slips = pd.DataFrame([{
            'id': s.id,
            'student_id': s.student_id,
            'isbn': s.book_isbn,
            'borrow_date': s.borrow_date,
            'expected_return': s.expected_return_date,
            'actual_return': s.actual_return_date,
            'status': s.status
        } for s in slips])
        
        # Top 5 sách mượn nhiều nhất
        most_borrowed = df_slips['isbn'].value_counts().head(5)
        popular_books = [{"name": book_map.get(str(isbn), {}).get("name", str(isbn)), "count": int(count)} 
                         for isbn, count in most_borrowed.items()]
                         
        # Độc giả mượn sách nhiều nhất (Top 5)
        most_active = df_slips['student_id'].value_counts().head(5)
        top_students = [{"name": student_map.get(str(sid), f"SV {sid}"), "count": int(count)} 
                        for sid, count in most_active.items()]
                        
        # Số lượng phiếu mượn theo trạng thái
        status_counts = df_slips['status'].value_counts()
        slip_status_counts = {
            "Borrowed": int(status_counts.get("Borrowed", 0)),
            "Returned": int(status_counts.get("Returned", 0)),
            "Overdue": int(status_counts.get("Overdue", 0))
        }
        
        # Tính toán tỷ lệ trễ hạn & số phiếu quá hạn
        overdue_count = slip_status_counts["Overdue"]
        returned_count = slip_status_counts["Returned"]
        
        today = date.today()
        today_dt = pd.to_datetime(today)
        currently_late = len(df_slips[(df_slips['status'] == 'Borrowed') & (pd.to_datetime(df_slips['expected_return']) < today_dt)])
        total_overdue_count = overdue_count + currently_late
        overdue_rate = (total_overdue_count / len(df_slips)) * 100
        
        # Tỷ lệ trả sách đúng hạn vs trễ hạn (trong số các phiếu đã trả)
        df_returned = df_slips[df_slips['status'] == 'Returned'].copy()
        if len(df_returned) > 0:
            df_returned['is_late'] = pd.to_datetime(df_returned['actual_return']) > pd.to_datetime(df_returned['expected_return'])
            late_count = int(df_returned['is_late'].sum()) # type: ignore
            on_time_count = len(df_returned) - late_count
        else:
            late_count = 0
            on_time_count = 0
        return_punctuality = {"OnTime": on_time_count, "Late": late_count}
        
        # Xu hướng tiền phạt phát sinh theo tháng (6 tháng gần nhất)
        # Tối ưu hoá (Vectorization) để tăng tốc độ tính toán tiền phạt
        expected = pd.to_datetime(df_slips['expected_return'], errors='coerce')
        actual = pd.to_datetime(df_slips['actual_return'], errors='coerce')
        
        cond_returned_late = (df_slips['status'] == 'Returned') & (actual.notna()) & (actual > expected)
        fine_returned_late = (actual - expected).dt.days * 5000
        
        cond_overdue = (df_slips['status'] == 'Overdue') | ((df_slips['status'] == 'Borrowed') & (today_dt > expected))
        fine_overdue = (today_dt - expected).dt.days * 5000
        
        df_slips['fine'] = 0
        df_slips.loc[cond_returned_late, 'fine'] = fine_returned_late[cond_returned_late]
        df_slips.loc[cond_overdue, 'fine'] = fine_overdue[cond_overdue]
        df_slips['month'] = df_slips['borrow_date'].astype(str).str[:7]
        fine_by_month = df_slips.groupby('month')['fine'].sum().sort_index().tail(6)
        fine_trend = {str(m): float(val) for m, val in fine_by_month.items()}
        
        # Tần suất mượn sách theo ngày trong tuần (Thứ 2 - Chủ Nhật)
        df_slips['weekday'] = pd.to_datetime(df_slips['borrow_date']).dt.dayofweek # type: ignore
        weekday_counts = df_slips['weekday'].value_counts().sort_index()
        weekday_names = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]
        borrow_by_weekday = {weekday_names[int(w)]: int(cnt) for w, cnt in weekday_counts.items() if 0 <= int(w) < 7}# type: ignore
        for name in weekday_names:
            if name not in borrow_by_weekday:
                borrow_by_weekday[name] = 0
                
        # Lượt mượn sách theo thể loại (Vectorized map)
        genre_mapping = {str(k): v.get("genre", "Không xác định") for k, v in book_map.items()}
        df_slips['genre'] = df_slips['isbn'].astype(str).map(genre_mapping).fillna("Không xác định")
        genre_borrow_counts = df_slips['genre'].value_counts()
        borrow_by_genre = {str(g): int(cnt) for g, cnt in genre_borrow_counts.items()}
        
        # Thời gian mượn trung bình theo thể loại (chỉ tính phiếu đã trả)
        df_ret = df_slips[(df_slips['status'] == 'Returned') & (df_slips['actual_return'].notna())].copy()
        if len(df_ret) > 0:
            df_ret['duration'] = (pd.to_datetime(df_ret['actual_return']) - pd.to_datetime(df_ret['borrow_date'])).dt.days # type: ignore
            df_ret['genre'] = df_ret['isbn'].astype(str).map(genre_mapping).fillna("Không xác định")
            avg_dur = df_ret.groupby('genre')['duration'].mean()
            avg_duration_by_genre = {str(g): round(float(v), 1) for g, v in avg_dur.items()}
        else:
            avg_duration_by_genre = {}
            
        # Phân bố số ngày mượn thực tế (chỉ tính phiếu đã trả)
        duration_distribution = {"< 7 ngày": 0, "7-14 ngày": 0, "14-30 ngày": 0, "> 30 ngày": 0}
        if len(df_ret) > 0:
            durations = (pd.to_datetime(df_ret['actual_return']) - pd.to_datetime(df_ret['borrow_date'])).dt.days
            # Vectorization bằng hàm cắt bin của Pandas để đếm tốc độ cao
            bins = [-float('inf'), 6, 14, 30, float('inf')]
            labels = ["< 7 ngày", "7-14 ngày", "14-30 ngày", "> 30 ngày"]
            counts = pd.cut(durations, bins=bins, labels=labels).value_counts()
            for k in labels:
                duration_distribution[k] = int(counts.get(k, 0))
                     
        # Số lượng sách có sẵn trong kho theo thể loại đã được tính toán tối ưu ở vòng lặp đầu tiên
                
        # Top 5 sách bị quá hạn nhiều nhất (đang quá hạn hoặc từng bị trả trễ hạn)
        # Tối ưu hoá (Vectorization) để tránh lặp từng hàng (gây treo UI)
        expected = pd.to_datetime(df_slips['expected_return'], errors='coerce')
        actual = pd.to_datetime(df_slips['actual_return'], errors='coerce')
        
        cond1 = df_slips['status'] == 'Overdue'
        cond2 = (df_slips['status'] == 'Returned') & (actual.notna()) & (actual > expected)#type: ignore
        
        df_slips['ever_overdue'] = cond1 | cond2
        df_overdue_slips = df_slips[df_slips['ever_overdue']]
        overdue_book_counts = df_overdue_slips['isbn'].value_counts().head(5)
        most_overdue_books = [{"name": book_map.get(str(isbn), {}).get("name", str(isbn)), "count": int(count)} 
                               for isbn, count in overdue_book_counts.items()]
                               
        # Lượt mượn theo tháng (6 tháng gần nhất)
        df_slips['month'] = df_slips['borrow_date'].astype(str).str[:7]
        monthly_counts = df_slips['month'].value_counts().sort_index().tail(6)
        borrows_by_month = {str(m): int(val) for m, val in monthly_counts.items()}
        
        return {
            "total_books": total_books,
            "total_students": total_students,
            "borrowed_books": borrowed_books,
            "available_books": available_books,
            "damaged_books": damaged_books,
            "total_borrows": len(df_slips),
            "overdue_rate": round(overdue_rate, 2),
            "overdue_count": total_overdue_count,
            "returned_count": returned_count,
            "popular_books": popular_books,
            "genre_counts": genre_counts,
            "borrows_by_month": borrows_by_month,
            "top_students": top_students,
            "slip_status_counts": slip_status_counts,
            "return_punctuality": return_punctuality,
            "fine_trend": fine_trend,
            "borrow_by_weekday": borrow_by_weekday,
            "borrow_by_genre": borrow_by_genre,
            "avg_duration_by_genre": avg_duration_by_genre,
            "duration_distribution": duration_distribution,
            "available_by_genre": available_by_genre,
            "most_overdue_books": most_overdue_books
        }

    @staticmethod
    def export_to_excel(filename="Library_Data.xlsx"):
        # Hàm xuất toàn bộ dữ liệu danh mục sách và các phiếu mượn trả ra định dạng Excel (.xlsx).
        # Sử dụng đối tượng pd.DataFrame để tạo bảng 2 chiều và pd.ExcelWriter để lưu file.
        
        session = get_session()
        
        # Xuất dữ liệu Sách
        books = session.query(Book).all()
        df_books = pd.DataFrame([{
            'Mã Sách (ISBN)': b.isbn, 'Tên Sách': b.name, 'Thể Loại': b.genre, 'Trạng Thái': "Có sẵn" if b.status == "Available" else "Đang mượn"
        } for b in books])
        
        # Xuất dữ liệu Phiếu mượn
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
