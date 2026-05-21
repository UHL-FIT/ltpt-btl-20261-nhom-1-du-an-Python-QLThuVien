# ==============================================================================
# Tệp: utils/debug_logger.py
# Mục đích: Định nghĩa tiện ích gỡ lỗi (Debug Logger) thời gian thực.
# Chức năng:
# - Bắt toàn bộ các tương tác từ người dùng (click, binding) trên các element.
# - (MỚI) Dùng hệ thống Python Profiler để "Trace" (dò vết) in ra toàn bộ cây 
#   chuỗi các hàm/phương thức đã được gọi liên tiếp bên trong phần mềm.
# - Loại bỏ những hàm nội bộ ồn ào của tkinter, python core để log thật sạch.
# ==============================================================================

import os
import sys
import inspect
import linecache
import functools
import threading
import tkinter
import customtkinter as ctk

# Kích hoạt ANSI Color cho Windows Terminal nếu chạy trên Windows
if os.name == 'nt':
    os.system("")

# Bảng mã màu ANSI
COLOR_BORDER = "\033[90m"     # Grey
COLOR_HEADER = "\033[95m"     # Magenta
COLOR_WIDGET = "\033[94m"     # Blue
COLOR_TRIGGER = "\033[96m"    # Cyan
COLOR_CALLBACK = "\033[92m"   # Green
COLOR_GREEN = "\033[92m"      # Green
COLOR_LOCATION = "\033[93m"   # Yellow
COLOR_RESET = "\033[0m"       # Reset

NOISY_SEQUENCES = {
    "<Enter>", "<Leave>", "<Motion>", "<Configure>", "<FocusIn>", "<FocusOut>", 
    "<Map>", "<Unmap>", "<Visibility>", "<Expose>", "<Destroy>", 
    "<Activate>", "<Deactivate>"
}

# Sử dụng thread local storage để lưu độ sâu (depth) của traceback
trace_data = threading.local()

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

def is_app_code(filename):
    """Kiểm tra xem file có thuộc mã nguồn chính của ứng dụng không."""
    if not filename or filename.startswith("<"):
        return False
        
    try:
        abs_filename = os.path.abspath(filename)
    except Exception:
        abs_filename = filename
        
    # Chỉ ghi nhận các file nằm trong thư mục gốc của project (ứng dụng)
    if not abs_filename.startswith(PROJECT_ROOT):
        return False
        
    # Loại trừ môi trường ảo và chính logger này
    exclusions = ["\\venv\\", "/venv/", "\\env\\", "/env/", "debug_logger"]
    for ex in exclusions:
        if ex in abs_filename.lower():
            return False
            
    return True

def profile_calls(frame, event, arg):
    """Tracer theo dõi và in ra dạng cây các hàm/phương thức được gọi."""
    func_name = frame.f_code.co_name
    if func_name in ("<genexpr>", "<listcomp>", "<dictcomp>", "<setcomp>"):
        return
        
    if event == 'call':
        filename = frame.f_code.co_filename
        if not is_app_code(filename):
            return
        cls_name = ""
        # Thử suy luận tên class từ f_locals nếu hàm này là method
        if "self" in frame.f_locals:
            try:
                cls_name = frame.f_locals["self"].__class__.__name__ + "."
            except Exception:
                pass
                
        depth = getattr(trace_data, 'depth', 0)
        indent = "  " * depth
        
        lineno = frame.f_lineno
        try:
            rel_filename = os.path.relpath(filename) if os.path.isabs(filename) else filename
        except Exception:
            rel_filename = filename
            
        print(f"{COLOR_BORDER}│{COLOR_RESET}   {indent}{COLOR_TRIGGER}→ {cls_name}{func_name}(){COLOR_RESET} {COLOR_BORDER}({rel_filename}:{lineno}){COLOR_RESET}")
        
        trace_data.depth = depth + 1
        
    elif event == 'return':
        filename = frame.f_code.co_filename
        if not is_app_code(filename):
            return
            
        depth = getattr(trace_data, 'depth', 1)
        trace_data.depth = max(0, depth - 1)

def get_widget_info(widget):
    """Lấy thông tin chi tiết của Widget."""
    cls_name = widget.__class__.__name__
    info = f"{COLOR_WIDGET}[{cls_name}]{COLOR_RESET}"
    
    text = None
    try:
        if hasattr(widget, "cget"):
            text = widget.cget("text")
    except Exception:
        pass
        
    if not text:
        try:
            if hasattr(widget, "_text"):
                text = widget._text
        except Exception:
            pass
            
    if text:
        info += f" text='{COLOR_TRIGGER}{text}{COLOR_RESET}'"
        
    info += f" path={widget._w}"
    return info

def get_callback_info(func):
    """Trích xuất và định dạng thông tin hàm/phương thức callback."""
    if not func:
        return f"{COLOR_LOCATION}None{COLOR_RESET}"
        
    if isinstance(func, functools.partial):
        inner_info = get_callback_info(func.func)
        return f"Partial: {inner_info} args={func.args} kwargs={func.keywords}"
        
    desc = ""
    if hasattr(func, "__self__") and func.__self__ is not None:
        cls_name = func.__self__.__class__.__name__
        func_name = func.__name__
        desc = f"{COLOR_CALLBACK}Method: {cls_name}.{func_name}(){COLOR_RESET}"
    else:
        func_name = getattr(func, "__name__", str(func))
        if func_name == "<lambda>":
            desc = f"{COLOR_CALLBACK}Lambda function{COLOR_RESET}"
        else:
            desc = f"{COLOR_CALLBACK}Function: {func_name}(){COLOR_RESET}"
            
    try:
        func_code = func.__code__
        filename = func_code.co_filename
        lineno = func_code.co_firstlineno
        rel_filename = os.path.relpath(filename) if os.path.isabs(filename) else filename
        line_content = linecache.getline(filename, lineno).strip()
        
        desc += f"\n{COLOR_BORDER}│{COLOR_RESET}   {COLOR_LOCATION}Location:{COLOR_RESET} {rel_filename}:{lineno}"
        if line_content:
            desc += f"\n{COLOR_BORDER}│{COLOR_RESET}   {COLOR_LOCATION}Code:{COLOR_RESET}     {line_content}"
    except Exception:
        pass
        
    return desc

def log_interaction_header(event_type, widget, trigger_info, callback):
    """In phần tiêu đề log thông tin tương tác."""
    widget_desc = get_widget_info(widget)
    callback_desc = get_callback_info(callback)
    
    print(f"{COLOR_BORDER}┌─── [LMS-PRO X DEBUGGER] ──────────────────────────────────────────────────{COLOR_RESET}")
    print(f"{COLOR_BORDER}│{COLOR_RESET} {COLOR_HEADER}EVENT TYPE:{COLOR_RESET} {event_type}")
    print(f"{COLOR_BORDER}│{COLOR_RESET} {COLOR_HEADER}WIDGET:{COLOR_RESET}     {widget_desc}")
    print(f"{COLOR_BORDER}│{COLOR_RESET} {COLOR_HEADER}TRIGGER:{COLOR_RESET}    {trigger_info}")
    print(f"{COLOR_BORDER}│{COLOR_RESET} {COLOR_HEADER}CALLBACK:{COLOR_RESET}   {callback_desc}")

def run_with_tracer(func, *args, **kwargs):
    """Chạy hàm với Profile Tracer để in ra chuỗi Call Stack."""
    trace_data.depth = 0
    print(f"{COLOR_BORDER}│{COLOR_RESET} {COLOR_HEADER}EXECUTION TRACE (Chuỗi hàm được gọi):{COLOR_RESET}")
    
    old_profile = sys.getprofile()
    sys.setprofile(profile_calls)
    try:
        return func(*args, **kwargs)
    finally:
        sys.setprofile(old_profile)
        print(f"{COLOR_BORDER}└───────────────────────────────────────────────────────────────────────────{COLOR_RESET}\n")

def wrap_command(widget, command, trigger_type):
    if not command:
        return None
        
    @functools.wraps(command)
    def command_wrapper(*args, **kwargs):
        log_interaction_header("COMMAND EXECUTED", widget, f"Widget command ({trigger_type})", command)
        return run_with_tracer(command, *args, **kwargs)
        
    return command_wrapper

def make_logged_bind(widget, sequence, func):
    is_noisy = any(noisy in sequence for noisy in NOISY_SEQUENCES)
    
    def event_wrapper(event):
        if not is_noisy:
            log_interaction_header("EVENT TRIGGERED", widget, f"Bind sequence: {sequence}", func)
            return run_with_tracer(func, event)
        return func(event)
    return event_wrapper

def patch_widget_class(cls):
    original_init = cls.__init__
    original_configure = cls.configure if hasattr(cls, "configure") else None
    
    try:
        sig = inspect.signature(original_init)
        params = list(sig.parameters.keys())
    except Exception:
        params = []
        
    @functools.wraps(original_init)
    def patched_init(self, *args, **kwargs):
        new_args = list(args)
        new_kwargs = dict(kwargs)
        
        if "command" in new_kwargs and new_kwargs["command"]:
            new_kwargs["command"] = wrap_command(self, new_kwargs["command"], "init")
        elif "command" in params:
            try:
                cmd_index = params.index("command")
                args_index = cmd_index - 1
                if 0 <= args_index < len(new_args) and new_args[args_index]:
                    new_args[args_index] = wrap_command(self, new_args[args_index], "init")
            except Exception:
                pass
                
        original_init(self, *new_args, **new_kwargs)
        
    cls.__init__ = patched_init
    
    if original_configure:
        @functools.wraps(original_configure)
        def patched_configure(self, *args, **kwargs):
            new_kwargs = dict(kwargs)
            if "command" in new_kwargs and new_kwargs["command"]:
                new_kwargs["command"] = wrap_command(self, new_kwargs["command"], "configure")
            return original_configure(self, *args, **new_kwargs)
        cls.configure = patched_configure

def setup_debug_logger():
    print(f"\n{COLOR_GREEN}[INFO] Đang khởi động LMS-PRO X Debug Logger (Tracer Mode)...{COLOR_RESET}")
    
    original_bind = tkinter.Misc.bind
    
    @functools.wraps(original_bind)
    def patched_bind(self, sequence, func=None, add=None):
        if func and callable(func):
            wrapped_func = make_logged_bind(self, sequence, func)
            return original_bind(self, sequence, wrapped_func, add)
        return original_bind(self, sequence, func, add)
        
    tkinter.Misc.bind = patched_bind # type: ignore
    print(f"{COLOR_GREEN}[INFO] Patch thành công tkinter.Misc.bind{COLOR_RESET}")
    
    ctk_classes_to_patch = [
        ctk.CTkButton, ctk.CTkCheckBox, ctk.CTkRadioButton, ctk.CTkSwitch,
        ctk.CTkOptionMenu, ctk.CTkSegmentedButton, ctk.CTkSlider, ctk.CTkComboBox
    ]
    
    for cls in ctk_classes_to_patch:
        patch_widget_class(cls)
        print(f"{COLOR_GREEN}[INFO] Patch thành công class {cls.__name__}{COLOR_RESET}")
        
    print(f"{COLOR_GREEN}[INFO] Tracer hoạt động! Click bất kỳ phần tử nào để theo dõi chuỗi hàm.{COLOR_RESET}\n")
