import customtkinter as ctk
from controllers.student_controller import StudentController
from tkinter import messagebox
from views.components.data_table import DataTable

class StudentView(ctk.CTkFrame):
    def __init__(self, parent, on_refresh=None):
        super().__init__(parent, fg_color="transparent")
        self.on_refresh = on_refresh
        self.controller = StudentController()
        
        self.setup_ui()

    def setup_ui(self):
        # Header
        header = ctk.CTkLabel(
            self,
            text="Quản lý Học sinh / Sinh viên",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        header.pack(anchor="w", pady=(0, 20))
        
        # Action Panel (Top)
        action_frame = ctk.CTkFrame(self)
        action_frame.pack(fill="x", pady=(0, 20), padx=5)
        
        action_frame.grid_columnconfigure((1, 3, 5, 7), weight=1)

        ctk.CTkLabel(action_frame, text="Mã SV:").grid(row=0, column=0, padx=10, pady=15, sticky="w")
        self.id_entry = ctk.CTkEntry(action_frame, placeholder_text="Mã SV")
        self.id_entry.grid(row=0, column=1, padx=10, pady=15, sticky="ew")

        ctk.CTkLabel(action_frame, text="Họ Tên:").grid(row=0, column=2, padx=10, pady=15, sticky="w")
        self.name_entry = ctk.CTkEntry(action_frame, placeholder_text="Họ Tên")
        self.name_entry.grid(row=0, column=3, padx=10, pady=15, sticky="ew")

        ctk.CTkLabel(action_frame, text="Email:").grid(row=0, column=4, padx=10, pady=15, sticky="w")
        self.email_entry = ctk.CTkEntry(action_frame, placeholder_text="Email")
        self.email_entry.grid(row=0, column=5, padx=10, pady=15, sticky="ew")
        
        ctk.CTkLabel(action_frame, text="Số ĐT:").grid(row=0, column=6, padx=10, pady=15, sticky="w")
        self.phone_entry = ctk.CTkEntry(action_frame, placeholder_text="Số điện thoại")
        self.phone_entry.grid(row=0, column=7, padx=10, pady=15, sticky="ew")

        btn_frame = ctk.CTkFrame(action_frame, fg_color="transparent")
        btn_frame.grid(row=0, column=8, padx=10, pady=15, sticky="e")

        self.add_btn = ctk.CTkButton(btn_frame, text="Thêm SV", command=self.handle_add, width=120)
        self.add_btn.pack(side="left")

        # Search Bar & List Actions
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 10), padx=5)

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="🔍 Tìm kiếm học sinh theo mã, tên...", width=400)
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.handle_search_realtime)
        
        self.search_btn = ctk.CTkButton(search_frame, text="Tìm kiếm", command=self.handle_search, width=100)
        self.search_btn.pack(side="left", padx=(0, 10))

        self.refresh_btn = ctk.CTkButton(search_frame, text="Làm mới", command=self.refresh_list, width=100)
        self.refresh_btn.pack(side="left")

        # Row level action placed on the right side of search bar for symmetrical ERP UI
        self.del_btn = ctk.CTkButton(
            search_frame, text="Xóa SV Đã Chọn", 
            command=self.handle_delete, 
            width=150, fg_color="#b83535", hover_color="#8c2323",
            font=ctk.CTkFont(weight="bold")
        )
        self.del_btn.pack(side="right")

        # Data Table Panel (Bottom)
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
        
        self.refresh_list()

    def handle_add(self):
        sid = self.id_entry.get()
        name = self.name_entry.get()
        email = self.email_entry.get()
        phone = self.phone_entry.get()
        
        if sid and name:
            success, msg = self.controller.add_student(sid, name, email, phone)
            if success:
                self.refresh_list()
                if self.on_refresh:
                    self.on_refresh()
                self.id_entry.delete(0, 'end')
                self.name_entry.delete(0, 'end')
                self.email_entry.delete(0, 'end')
                self.phone_entry.delete(0, 'end')
                messagebox.showinfo("Thành công", msg)
            else:
                messagebox.showerror("Lỗi", msg)
        else:
            messagebox.showwarning(
                "Lỗi nhập liệu", "Vui lòng điền các trường bắt buộc (Mã SV, Họ Tên)"
            )

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
