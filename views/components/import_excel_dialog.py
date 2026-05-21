import customtkinter as ctk
from tkinter import filedialog
import pandas as pd
from views.components.custom_dialog import show_custom_info, show_custom_error

class ImportExcelDialog(ctk.CTkToplevel):
    def __init__(self, master, title="Nhập dữ liệu Excel", template_columns=None, default_template_name="Template.xlsx", on_import_click=None):
        super().__init__(master)
        
        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)
        self.configure(fg_color="#0f172a")
        self.transient(master.winfo_toplevel())
        self.grab_set()
        
        self.template_columns = template_columns or []
        self.default_template_name = default_template_name
        self.on_import_click = on_import_click
        
        self.setup_ui()
        
        # Center window
        self.update_idletasks()
        try:
            parent = master.winfo_toplevel()
            x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
            y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
            self.geometry(f"+{x}+{y}")
        except:
            pass

    def setup_ui(self):
        lbl = ctk.CTkLabel(self, text="Chọn thao tác Nhập dữ liệu:", font=ctk.CTkFont(size=15, weight="bold"), text_color="#f8fafc")
        lbl.pack(pady=(20, 15))
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        btn_template = ctk.CTkButton(
            btn_frame, 
            text="Tải file mẫu trắng",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#10b981", hover_color="#059669",
            height=40,
            command=self.download_template
        )
        btn_template.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        btn_import = ctk.CTkButton(
            btn_frame, 
            text="Chọn file để nhập",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#3b82f6", hover_color="#2563eb",
            height=40,
            command=self.import_file
        )
        btn_import.pack(side="right", fill="x", expand=True, padx=(10, 0))

    def download_template(self):
        filepath = filedialog.asksaveasfilename(
            title="Lưu file mẫu trắng",
            defaultextension=".xlsx",
            initialfile=self.default_template_name,
            filetypes=[("Excel files", "*.xlsx")]
        )
        if filepath:
            try:
                df = pd.DataFrame(columns=self.template_columns)
                df.to_excel(filepath, index=False)
                show_custom_info(self, "Thành công", f"Đã lưu file mẫu tại:\n{filepath}")
            except Exception as e:
                show_custom_error(self, "Lỗi", f"Lỗi khi lưu file mẫu:\n{str(e)}")

    def import_file(self):
        self.destroy()
        if self.on_import_click:
            self.on_import_click()
