# ==============================================================================
# Tệp: views/student_view.py
# Mục đích: Cung cấp giao diện Quản lý Học sinh / Sinh viên (Độc giả).
# Chức năng:
# - Hiển thị danh sách sinh viên dưới dạng bảng.
# - Cung cấp biểu mẫu (Form) để người dùng có thể Thêm hoặc Chỉnh sửa thông tin sinh viên.
# ==============================================================================
import customtkinter as ctk
from controllers.student_controller import StudentController
from views.components.custom_dialog import show_custom_info, show_custom_error, show_custom_warning, show_custom_askyesno
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

        self.search_entry = ctk.CTkEntry(
            search_frame, 
            placeholder_text="🔍 Tìm kiếm học sinh theo mã, tên...", 
            width=400,
            border_color="#475569",
            fg_color="#1e293b"
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.handle_search_realtime)
        
        self.search_btn = ctk.CTkButton(
            search_frame, text="Tìm kiếm", command=self.handle_search, width=100,
            fg_color="#3b82f6", hover_color="#2563eb"
        )
        self.search_btn.pack(side="left", padx=(0, 10))

        self.refresh_btn = ctk.CTkButton(
            search_frame, text="Làm mới", command=self.refresh_list, width=100,
            fg_color="#475569", hover_color="#334155"
        )
        self.refresh_btn.pack(side="left", padx=(0, 10))

        # Nút xóa được thiết kế nằm ở phía bên phải để giao diện trông cân xứng và chuyên nghiệp hơn
        self.del_btn = ctk.CTkButton(
            search_frame, text="Xóa SV Đã Chọn", 
            command=self.handle_delete, 
            width=150, fg_color="#ef4444", hover_color="#dc2626",
            font=ctk.CTkFont(weight="bold")
        )
        self.del_btn.pack(side="right", padx=(10, 0))

        self.export_btn = ctk.CTkButton(
            search_frame, text="Xuất Excel", command=self.handle_export_excel, width=100,
            fg_color="#3b82f6", hover_color="#2563eb", font=ctk.CTkFont(weight="bold")
        )
        self.export_btn.pack(side="right", padx=(10, 0))

        self.import_btn = ctk.CTkButton(
            search_frame, text="Nhập từ Excel", command=self.handle_import_excel, width=110,
            fg_color="#f59e0b", hover_color="#d97706", font=ctk.CTkFont(weight="bold")
        )
        self.import_btn.pack(side="right", padx=(10, 0))

        self.add_new_btn = ctk.CTkButton(
            search_frame, text="Thêm Mới", command=lambda: self.open_student_form(), width=100, 
            fg_color="#10b981", hover_color="#059669", font=ctk.CTkFont(weight="bold")
        )
        self.add_new_btn.pack(side="right", padx=(10, 0))

        # Khung chứa bảng dữ liệu sinh viên hiển thị ở dưới cùng của giao diện
        self.table_frame = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=12)
        self.table_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        columns = ("student_id", "name", "email", "phone")
        self.table = DataTable(self.table_frame, columns=columns)
        self.table.pack(fill="both", expand=True, padx=10, pady=10)
        
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
        form_window.geometry("420x480")
        form_window.resizable(False, False)
        form_window.configure(fg_color="#0f172a")
        form_window.transient(self.winfo_toplevel())
        form_window.grab_set()

        # Center relative to parent
        form_window.update_idletasks()
        try:
            parent = self.winfo_toplevel()
            parent_x = parent.winfo_rootx()
            parent_y = parent.winfo_rooty()
            parent_w = parent.winfo_width()
            parent_h = parent.winfo_height()
            x = parent_x + (parent_w - 420) // 2
            y = parent_y + (parent_h - 480) // 2
            form_window.geometry(f"+{x}+{y}")
        except Exception:
            form_window.geometry("420x480+500+250")

        # Outer Border Frame matching theme
        border_frame = ctk.CTkFrame(form_window, fg_color="#1e293b", corner_radius=12, border_color="#3b82f6", border_width=1)
        border_frame.pack(fill="both", expand=True, padx=12, pady=12)

        # Title Label
        title_lbl = ctk.CTkLabel(
            border_frame, 
            text="THÔNG TIN SINH VIÊN" if not student_data else "CẬP NHẬT THÔNG TIN SINH VIÊN",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#3b82f6"
        )
        title_lbl.pack(pady=(15, 10))

        ctk.CTkLabel(border_frame, text="Mã SV:", font=ctk.CTkFont(size=12), text_color="#94a3b8").pack(pady=(5, 2), padx=25, anchor="w")
        id_entry = ctk.CTkEntry(border_frame, placeholder_text="Mã SV", fg_color="#0f172a", border_color="#475569")
        id_entry.pack(fill="x", padx=25, pady=(0, 8))

        ctk.CTkLabel(border_frame, text="Họ Tên:", font=ctk.CTkFont(size=12), text_color="#94a3b8").pack(pady=(5, 2), padx=25, anchor="w")
        name_entry = ctk.CTkEntry(border_frame, placeholder_text="Họ Tên", fg_color="#0f172a", border_color="#475569")
        name_entry.pack(fill="x", padx=25, pady=(0, 8))

        ctk.CTkLabel(border_frame, text="Email:", font=ctk.CTkFont(size=12), text_color="#94a3b8").pack(pady=(5, 2), padx=25, anchor="w")
        email_entry = ctk.CTkEntry(border_frame, placeholder_text="Email", fg_color="#0f172a", border_color="#475569")
        email_entry.pack(fill="x", padx=25, pady=(0, 8))

        ctk.CTkLabel(border_frame, text="Số ĐT:", font=ctk.CTkFont(size=12), text_color="#94a3b8").pack(pady=(5, 2), padx=25, anchor="w")
        phone_entry = ctk.CTkEntry(border_frame, placeholder_text="Số điện thoại", fg_color="#0f172a", border_color="#475569")
        phone_entry.pack(fill="x", padx=25, pady=(0, 15))

        if student_data:
            id_entry.insert(0, str(student_data[0]) if student_data[0] is not None and str(student_data[0]).strip().lower() != 'none' else "")
            name_entry.insert(0, str(student_data[1]) if student_data[1] is not None and str(student_data[1]).strip().lower() != 'none' else "")
            email_entry.insert(0, str(student_data[2]) if student_data[2] is not None and str(student_data[2]).strip().lower() != 'none' else "")
            phone_entry.insert(0, str(student_data[3]) if student_data[3] is not None and str(student_data[3]).strip().lower() != 'none' else "")

        def save_data():
            sid = id_entry.get().strip()
            name = name_entry.get().strip()
            email = email_entry.get().strip()
            phone = phone_entry.get().strip()

            if not (sid and name):
                show_custom_warning(form_window, "Lỗi nhập liệu", "Vui lòng điền các trường bắt buộc (Mã SV, Họ Tên)")
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
                show_custom_info(form_window, "Thành công", msg)
                form_window.destroy()
            else:
                show_custom_error(form_window, "Lỗi", msg)

        save_btn = ctk.CTkButton(
            border_frame, text="Lưu thông tin", command=save_data,
            fg_color="#3b82f6", hover_color="#2563eb", font=ctk.CTkFont(weight="bold")
        )
        save_btn.pack(pady=(5, 15))

    def handle_search_realtime(self, event):
        self.handle_search()

    def handle_search(self):
        query = self.search_entry.get()
        if not query.strip():
            self.refresh_list()
            return
            
        self.table.clear()
        students = self.controller.search_students(query)
        rows = [(student.student_id, student.name, student.email, student.phone) for student in students]
        self.table.insert_batch(rows)

    def refresh_list(self):
        self.table.clear()

        students = self.controller.get_all_students()
        rows = [(student.student_id, student.name, student.email, student.phone) for student in students]
        self.table.insert_batch(rows)

    def handle_delete(self):
        selected = self.table.get_selected()
        if not selected:
            show_custom_warning(self, "Chọn sinh viên", "Vui lòng chọn một sinh viên từ bảng để xóa.")
            return
 
        sid = selected[0]
        if show_custom_askyesno(self, "Xác nhận", f"Bạn có chắc muốn xóa sinh viên có mã {sid}?"):
            if self.controller.delete_student(sid):
                self.refresh_list()
                if self.on_refresh:
                    self.on_refresh()
                show_custom_info(self, "Thành công", "Xóa sinh viên thành công.")
            else:
                show_custom_error(self, "Lỗi", "Không thể xóa sinh viên này.")

    def handle_import_excel(self):
        from views.components.import_excel_dialog import ImportExcelDialog
        columns = ["Mã Sinh Viên", "Họ Tên", "Email", "Số Điện Thoại"]
        ImportExcelDialog(
            self, 
            title="Nhập dữ liệu Học sinh từ Excel", 
            template_columns=columns, 
            default_template_name="Template_Students.xlsx",
            on_import_click=self._process_import_excel
        )

    def _process_import_excel(self):
        import threading
        from tkinter import filedialog
        import pandas as pd
        
        filepath = filedialog.askopenfilename(
            title="Chọn tệp Excel",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if not filepath:
            return
            
        progress_win = ctk.CTkToplevel(self)
        progress_win.title("Nhập dữ liệu Excel")
        progress_win.geometry("400x150")
        progress_win.resizable(False, False)
        progress_win.configure(fg_color="#0f172a")
        progress_win.transient(self.winfo_toplevel())
        progress_win.grab_set()
        
        progress_win.update_idletasks()
        try:
            parent = self.winfo_toplevel()
            x = parent.winfo_rootx() + (parent.winfo_width() - 400) // 2
            y = parent.winfo_rooty() + (parent.winfo_height() - 150) // 2
            progress_win.geometry(f"+{x}+{y}")
        except:
            pass
            
        label = ctk.CTkLabel(progress_win, text="Đang chuẩn bị tệp tin...", text_color="#f8fafc", font=ctk.CTkFont(size=13))
        label.pack(pady=(20, 10))
        
        progress_bar = ctk.CTkProgressBar(progress_win, width=300)
        progress_bar.pack(pady=10)
        progress_bar.configure(mode="indeterminate")
        progress_bar.start()
        
        def do_import():
            try:
                label.configure(text="Đang phân tích dữ liệu Excel...")
                df = pd.read_excel(filepath)
                label.configure(text="Đang ghi vào cơ sở dữ liệu...")
                success, skipped, err = self.controller.import_students_from_df(df)
                
                self.after(0, lambda: import_finished(success, skipped, err))
            except Exception as e:
                self.after(0, lambda: import_finished(0, 0, str(e)))
                
        def import_finished(success, skipped, err):
            progress_bar.stop()
            progress_win.destroy()
            if err:
                show_custom_error(self, "Lỗi nhập Excel", err)
            else:
                self.refresh_list()
                if self.on_refresh:
                    self.on_refresh()
                show_custom_info(
                    self, 
                    "Nhập dữ liệu thành công", 
                    f"Đã nhập thành công {success} học sinh mới.\nBỏ qua {skipped} dòng (trùng mã hoặc dữ liệu không hợp lệ)."
                )
                
        threading.Thread(target=do_import, daemon=True).start()

    def handle_export_excel(self):
        import datetime
        from tkinter import filedialog
        import pandas as pd
        
        items = self.table.tree.get_children("")
        if not items:
            show_custom_warning(self, "Không có dữ liệu", "Không có dữ liệu hiển thị trên bảng để xuất.")
            return
            
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"Students_Filtered_{timestamp}.xlsx"
        
        filepath = filedialog.asksaveasfilename(
            title="Lưu báo cáo Excel",
            initialfile=default_filename,
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if not filepath:
            return
            
        data = []
        for item in items:
            values = self.table.tree.item(item)['values']
            if not values or isinstance(values, str) or len(values) < 4:
                continue
            data.append({
                'Mã Sinh Viên': values[0],
                'Họ và Tên': values[1],
                'Email': values[2] if values[2] != 'None' else '',
                'Số Điện Thoại': values[3] if values[3] != 'None' else ''
            })
            
        try:
            df = pd.DataFrame(data)
            df.to_excel(filepath, index=False)
            show_custom_info(self, "Thành công", f"Đã xuất dữ liệu ra tệp:\n{filepath}")
        except Exception as e:
            show_custom_error(self, "Lỗi xuất file", str(e))
