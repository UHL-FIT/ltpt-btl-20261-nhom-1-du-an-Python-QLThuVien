# ==============================================================================
# Tệp: views/student_view.py
# Mục đích: Cung cấp giao diện Quản lý Học sinh / Sinh viên (Độc giả).
# Chức năng:
# - Hiển thị danh sách sinh viên dưới dạng bảng.
# - Cung cấp biểu mẫu (Form) để người dùng có thể Thêm hoặc Chỉnh sửa thông tin sinh viên.
# ==============================================================================
import customtkinter as ctk
from controllers.student_controller import StudentController
from tkinter import messagebox
from views.components.data_table import DataTable

class StudentView(ctk.CTkFrame):
    # Lớp giao diện hiển thị và thao tác với dữ liệu Sinh viên/Độc giả.
    
    def __init__(self, parent, on_refresh=None):
        # Hàm khởi tạo: gắn view này vào view cha (parent)
        super().__init__(parent, fg_color="transparent")
        self.on_refresh = on_refresh
        
        # Khởi tạo controller để xử lý logic DB
        self.controller = StudentController()
        
        # Bắt đầu vẽ UI
        self.setup_ui()

    def setup_ui(self):
        # Khởi tạo phần tiêu đề (Header) của trang quản lý sinh viên
        header = ctk.CTkLabel(
            self,
            text="Quản lý Học sinh / Sinh viên",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        header.pack(anchor="w", pady=(0, 20))
        


        # Khung chứa thanh tìm kiếm và các nút tính năng mở rộng (Thêm, Làm mới)
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 10), padx=5)

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="🔍 Tìm kiếm học sinh theo mã, tên...", width=400)
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.handle_search_realtime)
        
        self.search_btn = ctk.CTkButton(search_frame, text="Tìm kiếm", command=self.handle_search, width=100)
        self.search_btn.pack(side="left", padx=(0, 10))

        self.refresh_btn = ctk.CTkButton(search_frame, text="Làm mới", command=self.refresh_list, width=100)
        self.refresh_btn.pack(side="left", padx=(0, 10))

        self.add_new_btn = ctk.CTkButton(search_frame, text="Thêm Mới", command=lambda: self.open_student_form(), width=100, fg_color="#4caf50", hover_color="#388e3c")
        self.add_new_btn.pack(side="left")

        # Nút xóa được thiết kế nằm ở phía bên phải để giao diện trông cân xứng và chuyên nghiệp hơn
        self.del_btn = ctk.CTkButton(
            search_frame, text="Xóa SV Đã Chọn", 
            command=self.handle_delete, 
            width=150, fg_color="#b83535", hover_color="#8c2323",
            font=ctk.CTkFont(weight="bold")
        )
        self.del_btn.pack(side="right")

        # Khung chứa bảng dữ liệu sinh viên hiển thị ở dưới cùng của giao diện
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        columns = ("student_id", "name", "email", "phone")
        self.table = DataTable(self.table_frame, columns=columns)
        self.table.pack(fill="both", expand=True, padx=2, pady=2)
        
        self.table.tree.heading("student_id", text="Mã Sinh Viên")
        self.table.tree.heading("name", text="Họ và Tên")
        self.table.tree.heading("email", text="Email")
        self.table.tree.heading("phone", text="Số Điện Thoại")
        
        self.table.set_column_width("student_id", 150)
        self.table.set_column_width("name", 250)
        self.table.set_column_width("email", 200)
        self.table.set_column_width("phone", 150)
        
        self.table.tree.bind("<Double-1>", self.handle_edit)

        self.refresh_list()

    def handle_edit(self, event):
        selected = self.table.get_selected()
        if selected:
            self.open_student_form(student_data=selected)

    def open_student_form(self, student_data=None):
        form_window = ctk.CTkToplevel(self)
        form_window.title("Sửa Sinh Viên" if student_data else "Thêm Sinh Viên Mới")
        form_window.geometry("400x420")
        form_window.transient(self.winfo_toplevel())
        form_window.grab_set()

        ctk.CTkLabel(form_window, text="Mã SV:").pack(pady=(20, 5), padx=20, anchor="w")
        id_entry = ctk.CTkEntry(form_window, placeholder_text="Mã SV")
        id_entry.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(form_window, text="Họ Tên:").pack(pady=5, padx=20, anchor="w")
        name_entry = ctk.CTkEntry(form_window, placeholder_text="Họ Tên")
        name_entry.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(form_window, text="Email:").pack(pady=5, padx=20, anchor="w")
        email_entry = ctk.CTkEntry(form_window, placeholder_text="Email")
        email_entry.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(form_window, text="Số ĐT:").pack(pady=5, padx=20, anchor="w")
        phone_entry = ctk.CTkEntry(form_window, placeholder_text="Số điện thoại")
        phone_entry.pack(fill="x", padx=20, pady=5)

        if student_data:
            id_entry.insert(0, str(student_data[0]))
            name_entry.insert(0, str(student_data[1]))
            email_entry.insert(0, str(student_data[2]) if student_data[2] != 'None' else "")
            phone_entry.insert(0, str(student_data[3]) if student_data[3] != 'None' else "")

        def save_data():
            sid = id_entry.get()
            name = name_entry.get()
            email = email_entry.get()
            phone = phone_entry.get()

            if not (sid and name):
                messagebox.showwarning("Lỗi nhập liệu", "Vui lòng điền các trường bắt buộc (Mã SV, Họ Tên)")
                return

            if student_data:
                old_id = student_data[0]
                success, msg = self.controller.update_student(old_id, sid, name, email, phone)
            else:
                success, msg = self.controller.add_student(sid, name, email, phone)

            if success:
                self.refresh_list()
                if self.on_refresh:
                    self.on_refresh()
                messagebox.showinfo("Thành công", msg)
                form_window.destroy()
            else:
                messagebox.showerror("Lỗi", msg)

        save_btn = ctk.CTkButton(form_window, text="Lưu", command=save_data)
        save_btn.pack(pady=20)

    def handle_search_realtime(self, event):
        self.handle_search()

    def handle_search(self):
        query = self.search_entry.get()
        if not query.strip():
            self.refresh_list()
            return
            
        self.table.clear()
        students = self.controller.search_students(query)
        for student in students:
            self.table.insert((student.student_id, student.name, student.email, student.phone))

    def refresh_list(self):
        self.table.clear()

        students = self.controller.get_all_students()
        for student in students:
            self.table.insert((student.student_id, student.name, student.email, student.phone))

    def handle_delete(self):
        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("Chọn sinh viên", "Vui lòng chọn một sinh viên từ bảng để xóa.")
            return

        sid = selected[0]
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa sinh viên có mã {sid}?"):
            if self.controller.delete_student(sid):
                self.refresh_list()
                if self.on_refresh:
                    self.on_refresh()
                messagebox.showinfo("Thành công", "Xóa sinh viên thành công.")
            else:
                messagebox.showerror("Lỗi", "Không thể xóa sinh viên này.")
