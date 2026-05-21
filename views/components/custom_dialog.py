# ==============================================================================
# Tệp: views/components/custom_dialog.py
# Mục đích: Định nghĩa các cửa sổ thông báo/xác nhận (Dialog) tùy biến.
# Chức năng:
# - Tạo giao diện hộp thoại đồng bộ với theme Slate Dark (#0f172a / #1e293b).
# - Hỗ trợ các kiểu thông báo: Info, Warning, Error và Xác nhận (Yes/No).
# ==============================================================================
import customtkinter as ctk

class CustomMessageDialog(ctk.CTkToplevel):
    def __init__(self, master, title, message, icon="info", show_cancel=False, **kwargs):
        super().__init__(master, **kwargs)
        self.title(title)
        self.geometry("450x220")
        self.resizable(False, False)
        self.configure(fg_color="#0f172a") # Slate Dark background
        
        # Modal setup
        self.transient(master)
        self.grab_set()
        self.attributes("-topmost", True)
        
        self.result = False
        
        # Center relative to master
        self.update_idletasks()
        try:
            master_x = master.winfo_rootx()
            master_y = master.winfo_rooty()
            master_w = master.winfo_width()
            master_h = master.winfo_height()
            x = master_x + (master_w - 450) // 2
            y = master_y + (master_h - 220) // 2
            self.geometry(f"+{x}+{y}")
        except Exception:
            # Fallback if window geometries cannot be fetched
            self.geometry("450x220+500+300")
            
        # Outer Border Frame
        border_frame = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=12, border_color="#3b82f6", border_width=1)
        border_frame.pack(fill="both", expand=True, padx=12, pady=12)
        
        # Icon/Title Color mapping
        title_color = "#3b82f6"  # Blue for Info
        icon_symbol = "💡"
        if icon == "error":
            title_color = "#ef4444"  # Red
            icon_symbol = "❌"
            border_frame.configure(border_color="#ef4444")
        elif icon == "warning":
            title_color = "#f59e0b"  # Orange
            icon_symbol = "⚠️"
            border_frame.configure(border_color="#f59e0b")
            
        # Title Header
        title_lbl = ctk.CTkLabel(
            border_frame, text=f"{icon_symbol}  {title}", 
            font=ctk.CTkFont(size=16, weight="bold"), 
            text_color=title_color
        )
        title_lbl.pack(pady=(15, 10))
        
        # Message Area
        msg_lbl = ctk.CTkLabel(
            border_frame, text=message, 
            font=ctk.CTkFont(size=13), 
            text_color="#f8fafc", 
            wraplength=390
        )
        msg_lbl.pack(pady=(5, 20), padx=20, fill="both", expand=True)
        
        # Action Buttons
        btn_frame = ctk.CTkFrame(border_frame, fg_color="transparent")
        btn_frame.pack(side="bottom", pady=15)
        
        if show_cancel:
            cancel_btn = ctk.CTkButton(
                btn_frame, text="Hủy", width=90, fg_color="#475569", hover_color="#334155",
                font=ctk.CTkFont(weight="bold"), command=self.on_cancel
            )
            cancel_btn.pack(side="left", padx=10)
            
            confirm_btn = ctk.CTkButton(
                btn_frame, text="Đồng ý", width=90, fg_color="#3b82f6", hover_color="#2563eb",
                font=ctk.CTkFont(weight="bold"), command=self.on_confirm
            )
            confirm_btn.pack(side="left", padx=10)
        else:
            ok_btn = ctk.CTkButton(
                btn_frame, text="Xác nhận", width=100, fg_color="#3b82f6", hover_color="#2563eb",
                font=ctk.CTkFont(weight="bold"), command=self.on_confirm
            )
            ok_btn.pack()
            
    def on_confirm(self):
        self.result = True
        self.grab_release()
        self.destroy()
        
    def on_cancel(self):
        self.result = False
        self.grab_release()
        self.destroy()

def show_custom_info(parent, title, message):
    root = parent.winfo_toplevel()
    dialog = CustomMessageDialog(root, title, message, icon="info")
    root.wait_window(dialog)
    return True

def show_custom_error(parent, title, message):
    root = parent.winfo_toplevel()
    dialog = CustomMessageDialog(root, title, message, icon="error")
    root.wait_window(dialog)
    return True

def show_custom_warning(parent, title, message):
    root = parent.winfo_toplevel()
    dialog = CustomMessageDialog(root, title, message, icon="warning")
    root.wait_window(dialog)
    return True

def show_custom_askyesno(parent, title, message):
    root = parent.winfo_toplevel()
    dialog = CustomMessageDialog(root, title, message, icon="warning", show_cancel=True)
    root.wait_window(dialog)
    return dialog.result
