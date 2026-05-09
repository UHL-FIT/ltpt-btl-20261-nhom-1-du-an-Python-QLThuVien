# 📚 LMS-PRO X: Hệ Thống Quản Lý Thư Viện Cao Cấp (Premium Library Management System)

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/GUI-CustomTkinter-indigo?style=for-the-badge&logo=expert&logoColor=white" alt="GUI Framework" />
  <img src="https://img.shields.io/badge/Database-SQLite%20%2F%20SQLAlchemy-red?style=for-the-badge&logo=sqlite&logoColor=white" alt="Database" />
  <img src="https://img.shields.io/badge/Analytics-Pandas%20%26%20Matplotlib-green?style=for-the-badge&logo=pandas&logoColor=white" alt="Analytics" />
  <img src="https://img.shields.io/badge/License-MIT-orange?style=for-the-badge" alt="License" />
</div>

---

**LMS-PRO X** là một phần mềm Desktop quản lý thư viện chuyên nghiệp, hiệu năng cao được xây dựng trên nền tảng ngôn ngữ Python. Ứng dụng sở hữu giao diện tối tân, tối ưu hóa trải nghiệm người dùng với chế độ tối (Dark Mode) thời thượng, kiến trúc chuẩn MVC (Model-View-Controller) khép kín, cùng hệ thống tìm kiếm toàn văn siêu tốc và bộ thống kê dữ liệu trực quan cực kỳ mạnh mẽ.

---

## ✨ Các Tính Năng Nổi Bật

### 💻 1. Giao diện Desktop Hiện đại & Cao cấp (Premium Dark GUI)
*   **CustomTkinter Engine:** Giao diện phẳng hiện đại, đồng bộ tối đa với chế độ Dark Mode tinh tế giúp chống mỏi mắt cho cán bộ thư viện trong thời gian dài làm việc.
*   **Thanh điều hướng Side-bar:** Quản lý chuyển đổi mượt mà giữa các tab chức năng không gây trễ hoặc lag.
*   **Bảng dữ liệu thông minh:** Component bảng dữ liệu tùy chỉnh [data_table.py](views/components/data_table.py) hỗ trợ hiển thị lưới trực quan, phân trang và cuộn trượt mượt mà.

### 🔍 2. Công nghệ Tìm kiếm Toàn văn Tiên tiến (Advanced FTS5 Engine)
*   **SQLite FTS5 Integration:** Tìm kiếm thông tin Sách, Sinh viên và Phiếu mượn tức thời thông qua máy ảo tìm kiếm toàn văn tích hợp sẵn trong SQLite.
*   **Tìm kiếm không dấu (Accent-Insensitive Search):** Tích hợp thư viện `unidecode` để tạo hàm SQLite tùy biến `unaccent()`. Người dùng có thể tìm kiếm không dấu (ví dụ: gõ "toan" vẫn ra sách "Toán học", gõ "Bui" vẫn ra sinh viên "Bùi Ngọc Lâm") với tốc độ phản hồi cực kỳ vượt trội.
*   **Đồng bộ tự động bằng Database Triggers:** Mọi hoạt động Thêm, Sửa, Xóa trên các bảng vật lý đều được đồng bộ thời gian thực sang bảng ảo FTS5 nhờ hệ thống SQLite Triggers thông minh được cấu hình trong [db_manager.py](database/db_manager.py).

### 📊 3. Thống kê & Trực quan hóa Số liệu (Data Analytics)
*   **8 Chỉ số KPI thư viện chính:** Cập nhật thời gian thực về Tổng số sách, Tổng số sinh viên, Tổng lượt mượn, Tỷ lệ quá hạn, Sách đang mượn, Sách sẵn có, Số phiếu quá hạn và Số phiếu đã trả.
*   **4 Biểu đồ trực quan sinh động (Matplotlib):**
    *   *Top 5 Sách được mượn nhiều nhất* (Biểu đồ thanh ngang).
    *   *Tỷ lệ thể loại sách* (Biểu đồ tròn cơ cấu sách).
    *   *Tình trạng sách trong kho* (Biểu đồ tròn phân tích Available vs Borrowed).
    *   *Xu hướng mượn sách theo tháng* (Biểu đồ đường biểu diễn sự tăng trưởng theo thời gian).

### 📁 4. Tích hợp Báo cáo Excel 1-Click
*   **Trích xuất dữ liệu nhanh:** Xuất toàn bộ danh sách sách và lịch sử phiếu mượn sang file Excel ([Library_Report.xlsx](Library_Report.xlsx)) chỉ với một nút bấm duy nhất ở góc Sidebar nhờ sức mạnh xử lý của thư viện Pandas và Openpyxl.

### ⚙️ 5. Kiến trúc MVC Chuẩn mực & Sạch sẽ
*   **Clean Architecture:** Phân tách hoàn toàn giữa tầng lưu trữ dữ liệu ([models/](models/)), tầng điều khiển nghiệp vụ ([controllers/](controllers/)) và tầng giao diện ([views/](views/)), giúp dự án cực kỳ dễ bảo trì, nâng cấp và mở rộng tính năng mới.

---

## 🛠 Công Nghệ Sử Dụng (Tech Stack)

| Phân lớp (Layer) | Công nghệ chính | Vai trò trong dự án |
| :--- | :--- | :--- |
| **Giao diện (UI)** | `CustomTkinter` | Thiết kế giao diện máy tính hiện đại, đồng bộ hóa Dark Mode. |
| **Chọn ngày** | `tkcalendar` | Hộp thoại chọn ngày mượn/trả trực quan, tránh lỗi sai định dạng ngày. |
| **Cơ sở dữ liệu** | `SQLite 3` | Lưu trữ dữ liệu cục bộ an toàn, nhẹ nhàng, không yêu cầu cài đặt server. |
| **Tương tác DB** | `SQLAlchemy` | Công cụ ORM mạnh mẽ quản lý schema, giao dịch (transactions). |
| **Tìm kiếm toàn văn** | `SQLite FTS5` & `unidecode` | Xử lý tìm kiếm thông tin không dấu tiếng Việt siêu tốc. |
| **Xử lý số liệu** | `Pandas` & `Numpy` | Biến đổi cấu trúc và tổng hợp báo cáo dữ liệu. |
| **Vẽ đồ thị** | `Matplotlib` | Tạo lập đồ thị chuyên sâu và tích hợp trực tiếp lên giao diện Tkinter. |
| **Kết xuất báo cáo** | `Openpyxl` | Xuất dữ liệu đa tầng ra định dạng file `.xlsx` đẹp mắt. |

---

## 📐 Kiến Trúc Luồng Dữ Liệu (Architecture & Flow)

Dưới đây là mô hình luồng hoạt động chuẩn MVC của hệ thống **LMS-PRO X**:

```mermaid
graph TD
    User([Người dùng / Thủ thư]) -->|Tương tác GUI| View[Views / Giao diện người dùng]
    View -->|Yêu cầu xử lý| Controller[Controllers / Bộ điều khiển]
    Controller -->|Truy vấn thực thể| Model[Models / Thực thể dữ liệu]
    Controller -->|Thao tác dữ liệu| DB_Mgr[Database Manager]
    DB_Mgr <-->|ORM / SQL Engine| SQLite[(SQLite library.db)]
    SQLite -->|Triggers| FTS[(FTS5 Virtual Tables)]
    
    style User fill:#4caf50,stroke:#388e3c,stroke-width:2px,color:#fff
    style View fill:#1f538d,stroke:#153d6b,stroke-width:2px,color:#fff
    style Controller fill:#9c27b0,stroke:#7b1fa2,stroke-width:2px,color:#fff
    style Model fill:#ff9800,stroke:#f57c00,stroke-width:2px,color:#fff
    style DB_Mgr fill:#00bcd4,stroke:#0097a7,stroke-width:2px,color:#fff
    style SQLite fill:#f44336,stroke:#d32f2f,stroke-width:2px,color:#fff
    style FTS fill:#e91e63,stroke:#c2185b,stroke-width:2px,color:#fff
```

---

## 💾 Thiết Kế Cơ Sở Dữ Liệu (Database Schema)

Hệ thống quản lý thông tin chặt chẽ thông qua 3 bảng chính:

```text
  ┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐
  │      BOOKS      │          │  BORROW_SLIPS   │          │    STUDENTS     │
  ├─────────────────┤          ├─────────────────┤          ├─────────────────┤
  │ isbn (PK)       │◄─────────┤ book_isbn       │          │ student_id (PK) │
  │ name            │          │ student_id      ├─────────►│ name            │
  │ genre           │          │ borrow_date     │          │ email           │
  │ status          │          │ expected_return │          │ phone           │
  └─────────────────┘          │ actual_return   │          └─────────────────┘
                               │ status          │
                               └─────────────────┘
```

### 1. Bảng `books` (Thông tin Sách)
*   `isbn` (String, Primary Key): Mã định danh chuẩn quốc tế của sách.
*   `name` (String, Not Null): Tiêu đề sách.
*   `genre` (String, Nullable): Thể loại sách.
*   `status` (String): Trạng thái của sách (`Available` - Có sẵn, `Borrowed` - Đang mượn, `Damaged` - Hỏng).

### 2. Bảng `students` (Thông tin Học sinh/Sinh viên)
*   `student_id` (String, Primary Key): Mã số sinh viên duy nhất.
*   `name` (String, Not Null): Họ và tên sinh viên.
*   `email` (String, Nullable): Địa chỉ thư điện tử.
*   `phone` (String, Nullable): Số điện thoại liên hệ.

### 3. Bảng `borrow_slips` (Phiếu mượn & trả sách)
*   `id` (Integer, Primary Key, Autoincrement): Mã số phiếu mượn tự động tăng.
*   `student_id` (String, Foreign Key): Liên kết đến mã số sinh viên mượn sách.
*   `book_isbn` (String, Foreign Key): Liên kết đến mã ISBN của cuốn sách được mượn.
*   `borrow_date` (Date): Ngày sinh viên mượn sách.
*   `expected_return_date` (Date, Not Null): Ngày hẹn trả sách dự kiến.
*   `actual_return_date` (Date, Nullable): Ngày sinh viên thực tế đem trả sách (nếu có).
*   `status` (String): Trạng thái phiếu mượn (`Borrowed` - Đang mượn, `Returned` - Đã trả, `Overdue` - Quá hạn).

---

## 🚀 Hướng Dẫn Cài Đặt & Sử Dụng

Vui lòng thực hiện theo các bước sau để thiết lập môi trường và chạy ứng dụng LMS-PRO X trên thiết bị của bạn:

### 1. Khởi tạo và Kích hoạt Môi trường ảo (Virtual Environment)
```bash
# Di chuyển vào thư mục dự án và khởi tạo .venv
python -m venv .venv

# Kích hoạt môi trường ảo (Hệ điều hành Windows)
.venv\Scripts\activate

# Kích hoạt môi trường ảo (Hệ điều hành macOS / Linux)
source .venv/bin/activate
```

### 2. Cài đặt các Thư viện phụ thuộc (Dependencies)
```bash
pip install -r requirements.txt
```

### 3. Nạp dữ liệu mẫu thử nghiệm (Database Seeding)
Dự án được trang bị sẵn một bộ tạo dữ liệu mẫu cực kỳ trực quan và thực tế bằng Tiếng Việt giúp bạn trải nghiệm ứng dụng ngay lập tức:
*   Sinh ngẫu nhiên **1,000 học sinh** với thông tin tên, email, sđt Việt Nam chân thực.
*   Sinh ngẫu nhiên **100 cuốn sách** thuộc nhiều thể loại đa dạng.
*   Thiết lập **3,000 phiếu mượn** trải dài trong vòng 1 năm qua (trong đó có 30 phiếu đang mượn hoạt động, 10 phiếu quá hạn và 2960 phiếu đã hoàn trả thành công).

Để chạy nạp dữ liệu mẫu, bạn chỉ cần thực hiện lệnh sau:
```bash
python seed_db.py
```
> [!NOTE]
> Nếu cơ sở dữ liệu `library.db` đã tồn tại từ trước, script sẽ tự động làm sạch (clean up) và tái tạo mới toàn bộ dữ liệu, giúp bạn luôn có một môi trường thử nghiệm sạch sẽ.

### 4. Khởi chạy Ứng dụng chính
Mọi thứ đã sẵn sàng! Chạy lệnh sau để khởi chạy ứng dụng GUI:
```bash
python main.py
```

---

## 📂 Cấu Trúc Thư Mục Dự Án

Bố cục mã nguồn được tổ chức khoa học và nhất quán theo kiến trúc phần mềm chuyên nghiệp:

```text
ProjectThuVien/
│
├── database/                   # Quản lý cấu hình & kết nối cơ sở dữ liệu
│   ├── __init__.py
│   └── db_manager.py           # Cấu hình SQLAlchemy Engine, Session, tạo bảng ảo FTS5 & Triggers
│
├── models/                     # Định nghĩa các SQLAlchemy ORM Entities
│   ├── __init__.py
│   ├── book.py                 # Lớp thực thể Book (Bảng books)
│   ├── student.py              # Lớp thực thể Student (Bảng students)
│   └── borrow_slip.py          # Lớp thực thể BorrowSlip (Bảng borrow_slips)
│
├── controllers/                # Tiếp nhận yêu cầu giao diện & xử lý Business Logic
│   ├── __init__.py
│   ├── book_controller.py      # Điều phối nghiệp vụ Sách
│   ├── student_controller.py   # Điều phối nghiệp vụ Sinh viên
│   └── borrow_controller.py    # Điều phối nghiệp vụ Mượn/Trả, cập nhật trạng thái
│
├── views/                      # Tầng giao diện người dùng (CustomTkinter GUI)
│   ├── __init__.py
│   ├── main_view.py            # Trình quản lý khung sườn chính, Side-bar và chuyển Tab
│   ├── book_view.py            # Giao diện nghiệp vụ Sách (Thêm, Sửa, Xóa, Tìm kiếm)
│   ├── student_view.py         # Giao diện nghiệp vụ Sinh viên
│   ├── borrow_view.py          # Giao diện nghiệp vụ Mượn/Trả, bộ lọc trạng thái mượn
│   ├── stats_view.py           # Giao diện Báo cáo Thống kê đồ họa tích hợp Matplotlib
│   └── components/             # Các thành phần giao diện dùng chung
│       └── data_table.py       # Thành phần bảng hiển thị dữ liệu lưới trực quan
│
├── utils/                      # Thư viện tiện ích và xử lý phân tích
│   ├── __init__.py
│   ├── analysis.py             # Xử lý tính toán thống kê (Pandas) và hàm Xuất Excel
│   └── styling.py              # Định nghĩa các thông số bảng màu, font chữ đồng bộ
│
├── library.db                  # File SQLite Database (Tự động sinh ra)
├── Library_Report.xlsx         # Báo cáo Excel kết xuất từ hệ thống (Tự động sinh ra khi click nút)
├── requirements.txt            # Định nghĩa danh sách thư viện phụ thuộc bắt buộc
├── seed_db.py                  # Script nạp 1,000 SV, 100 Sách, 3,000 Phiếu mượn mẫu tiếng Việt
└── main.py                     # Điểm khởi chạy chương trình (Main Entrypoint)
```

---

## 💡 Hướng Dẫn Sử Dụng Nhanh cho Thủ Thư

1.  **Theo dõi Thống kê (Dashboard):** Khi khởi động, bạn có thể chuyển tới Tab **Thống kê & Phân tích** để kiểm tra ngay biểu đồ tình hình thư viện hoạt động thực tế.
2.  **Quản lý Sách & Học sinh:** 
    *   Sử dụng thanh tìm kiếm ở đầu trang để lọc nhanh dữ liệu tức thì. 
    *   Hỗ trợ tìm kiếm không dấu (Ví dụ: Gõ `tiêu thuyet` vẫn tìm ra các sách thể loại `Tiểu thuyết`).
    *   Nút `Thêm`, `Sửa`, `Xóa` được tích hợp kèm hộp thoại cảnh báo an toàn tránh thao tác nhầm lẫn.
3.  **Tạo Phiếu Mượn mới:** 
    *   Vào Tab **Quản lý Mượn Trả**, chọn `Tạo phiếu mượn`. 
    *   Hộp thoại chọn ngày từ `tkcalendar` giúp bạn click chọn ngày hẹn trả cực nhanh và chính xác. Sách sau khi mượn sẽ tự động đổi trạng thái sang `Borrowed` (Đang mượn).
4.  **Trả Sách:** 
    *   Tại danh sách phiếu mượn, bạn có thể lọc nhanh theo trạng thái: *Đang mượn*, *Đã trả*, *Quá hạn*. 
    *   Chọn phiếu tương ứng và click `Trả sách` để cập nhật trạng thái phiếu và hoàn trả trạng thái sách về `Available` (Có sẵn).
5.  **Xuất file Báo cáo:** Click nút **Xuất dữ liệu ra Excel** ở Sidebar. File `Library_Report.xlsx` sẽ tự động được tạo ra tại thư mục chứa dự án với các sheet dữ liệu được phân chia vô cùng đẹp mắt.

---

## 🤝 Đội Ngũ Phát Triển (Credits)

Dự án được hoàn thiện dưới sự định hướng chuyên môn sâu sắc:

*   **Giảng viên Hướng dẫn:** ThS. Vũ Duy Sơn
*   **Thành viên thực hiện:**
    *   👨‍💻 **Bùi Ngọc Lâm**
    *   👨‍💻 **Đỗ Mạnh Cường**
    *   👨‍💻 **Đặng Minh Thành**
    *   👨‍💻 **Nguyễn Văn Tuấn**

---

## 📄 Giấy Phép (License)

Dự án được phân phối dưới giấy phép nguồn mở **MIT License**. Bạn được tự do học tập, nghiên cứu và phát triển thương mại phi lợi nhuận.

---
<p align="center">
  Chúc bạn có những trải nghiệm tuyệt vời cùng <b>LMS-PRO X</b>! 🚀
</p>
