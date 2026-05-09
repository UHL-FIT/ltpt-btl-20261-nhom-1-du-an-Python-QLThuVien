import customtkinter as ctk
from database.db_manager import init_db
from views.main_view import MainView

def main():
    # Initialize Database
    init_db()
    
    # Configure CustomTkinter
    ctk.set_appearance_mode("Dark")  # "System", "Dark", "Light"
    ctk.set_default_color_theme("blue")
    
    # Create main application window
    app = ctk.CTk()
    app.title("Phân mềm quản lý thư viện LMS-PRO X")
    app.geometry("1700x900")
    
    # Initialize the Main View (Dashboard)
    MainView(app)
    
    app.mainloop()

if __name__ == "__main__":
    main()
