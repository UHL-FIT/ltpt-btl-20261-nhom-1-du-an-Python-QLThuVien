# ==============================================================================
# Tệp: views/stats_view.py
# Mục đích: Xây dựng Giao diện (View) Thống kê & Phân tích dữ liệu (Dashboard).
# Chức năng:
# - Thiết lập giao diện Dashboard với các thẻ KPIs nhóm khoa học.
# - Thiết lập biểu đồ Matplotlib chất lượng cao (Donut chart, Area, Bar, Barh).
# - Hỗ trợ cho người dùng tự chọn 1 trong 14 biểu đồ để hiển thị.
# - Hỗ trợ Caching & cơ chế làm mới tự động (refresh) tối ưu hiệu năng.
# ==============================================================================
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.ticker as ticker
from utils.analysis import DataAnalyzer

# Sử dụng backend TkAgg ổn định cho môi trường Tkinter
matplotlib.use("TkAgg")

class StatsView(ctk.CTkFrame):
    # Lớp giao diện hiển thị bảng điều khiển thống kê thư viện (Dashboard).
    
    def __init__(self, parent, on_refresh=None):
        super().__init__(parent, fg_color="transparent")
        self.on_refresh = on_refresh
        
        # Trạng thái biểu đồ đang được chọn mặc định
        self.selected_chart_name = "Top 5 Sách Mượn Nhiều Nhất"
        
        # Khởi tạo vùng nội dung chính (Đổi từ ScrollableFrame sang Frame để hỗ trợ stretch/expand toàn màn hình)
        self.scroll_container = ctk.CTkFrame(self, fg_color="transparent")
        self.scroll_container.pack(fill="both", expand=True)
        
        # Vẽ nội dung thống kê và biểu đồ lần đầu tiên
        self.setup_ui_content()

    def refresh_stats(self):
        # Phương thức làm mới thống kê được gọi tự động từ MainView khi chuyển tab và có dữ liệu thay đổi
        # Xóa tất cả các widget con và vẽ lại từ đầu với dữ liệu mới nhất
        for widget in self.scroll_container.winfo_children():
            widget.destroy()
        self.setup_ui_content()

    def setup_ui_content(self):
        # 1. Truy xuất số liệu thống kê từ DataAnalyzer
        self.stats = DataAnalyzer.get_library_stats()

        # 2. Tiêu đề và nút bấm Làm mới thủ công
        header_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20), padx=5)
        
        header_lbl = ctk.CTkLabel(
            header_frame, text="Thống kê & Phân tích Thư viện",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#f8fafc"
        )
        header_lbl.pack(side="left")
        
        # Nút làm mới thủ công
        refresh_btn = ctk.CTkButton(
            header_frame, text="Làm mới dữ liệu 🔄", width=150,
            fg_color="#3b82f6", hover_color="#2563eb",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.refresh_stats
        )
        refresh_btn.pack(side="right")

        # 3. Lưới các Thẻ KPI nhóm khoa học (Kho sách - Độc giả - Hoạt động)
        kpi_grid = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        kpi_grid.pack(fill="x", pady=(0, 15))
        kpi_grid.grid_columnconfigure(0, weight=3) # Kho sách rộng hơn
        kpi_grid.grid_columnconfigure(1, weight=2) # Độc giả vừa phải
        kpi_grid.grid_columnconfigure(2, weight=4) # Mượn trả rộng nhất

        # Card 1: Kho Sách
        books_card = self.create_group_card(kpi_grid, "THÔNG TIN KHO SÁCH", "📚", 0, 0)
        self.add_kpi_item(books_card, "Tổng số sách", self.stats["total_books"], "#3b82f6", is_row=False)
        self.add_kpi_item(books_card, "Sẵn có", self.stats["available_books"], "#10b981", is_row=False)
        self.add_kpi_item(books_card, "Đang mượn", self.stats["borrowed_books"], "#f59e0b", is_row=False)

        # Card 2: Độc Giả
        students_card = self.create_group_card(kpi_grid, "ĐỘC GIẢ ĐĂNG KÝ", "🎓", 0, 1)
        self.add_kpi_item(students_card, "Tổng số sinh viên", self.stats["total_students"], "#8b5cf6", is_row=False)

        # Card 3: Mượn Trả
        borrow_card = self.create_group_card(kpi_grid, "HOẠT ĐỘNG MƯỢN TRẢ", "🔄", 0, 2)
        self.add_kpi_item(borrow_card, "Tổng lượt mượn", self.stats["total_borrows"], "#3b82f6", is_row=False)
        self.add_kpi_item(borrow_card, "Đã trả", self.stats["returned_count"], "#10b981", is_row=False)
        self.add_kpi_item(borrow_card, "Quá hạn", self.stats["overdue_count"], "#ef4444", is_row=False)
        self.add_kpi_item(borrow_card, "Tỷ lệ trễ hạn", f"{self.stats['overdue_rate']}%", "#f43f5e", is_row=False)

        # 4. Thanh chọn biểu đồ phân tích (Combobox)
        control_frame = ctk.CTkFrame(self.scroll_container, fg_color="#1e293b", corner_radius=12, border_color="#334155", border_width=1)
        control_frame.pack(fill="x", padx=5, pady=(5, 10))
        
        select_lbl = ctk.CTkLabel(
            control_frame, text="📊 Chọn biểu đồ phân tích cần xem:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#f8fafc"
        )
        select_lbl.pack(side="left", padx=20, pady=15)
        
        # Danh sách 14 biểu đồ phân tích
        self.chart_options = [
            "Top 5 Sách Mượn Nhiều Nhất",
            "Tỷ Lệ Thể Loại Sách Trong Kho",
            "Tình Trạng Sách Thư Viện (Có sẵn vs Đang mượn)",
            "Lượt Mượn Theo Tháng (6 Tháng Gần Nhất)",
            "Top 5 Độc Giả Tích Cực Nhất",
            "Tỷ Lệ Trạng Thái Phiếu Mượn",
            "Tỷ Lệ Trả Sách Đúng Hạn vs Trễ Hạn",
            "Tiền Phạt Phát Sinh Theo Tháng",
            "Tần Suất Mượn Theo Ngày Trong Tuần",
            "Lượt Mượn Sách Theo Thể Loại",
            "Thời Gian Mượn Trung Bình Theo Thể Loại",
            "Phân Bố Độ Dài Mượn Sách",
            "Số Lượng Sách Có Sẵn Theo Thể Loại",
            "Top 5 Sách Bị Quá Hạn Nhiều Nhất"
        ]
        
        # Đảm bảo lựa chọn hiện tại vẫn hợp lệ sau khi vẽ lại UI
        if self.selected_chart_name not in self.chart_options:
            self.selected_chart_name = self.chart_options[0]
            
        self.chart_combobox = ctk.CTkComboBox(
            control_frame, values=self.chart_options,
            width=380, height=35,
            font=ctk.CTkFont(size=13),
            dropdown_font=ctk.CTkFont(size=13),
            command=self.on_chart_changed
        )
        self.chart_combobox.set(self.selected_chart_name)
        self.chart_combobox.pack(side="right", padx=20, pady=15)

        # 5. Vùng vẽ biểu đồ lớn duy nhất
        self.chart_container = ctk.CTkFrame(
            self.scroll_container, fg_color="#1e293b",
            corner_radius=12, border_color="#334155", border_width=1
        )
        self.chart_container.pack(fill="both", expand=True, padx=5, pady=5)

        # Vẽ biểu đồ đang chọn
        self.draw_chart()

    def on_chart_changed(self, choice):
        self.selected_chart_name = choice
        self.draw_chart()

    def draw_chart(self):
        # Xóa widget cũ trong container biểu đồ
        for widget in self.chart_container.winfo_children():
            widget.destroy()
            
        choice = self.selected_chart_name
        
        if choice == "Top 5 Sách Mượn Nhiều Nhất":
            self.plot_popular_books(self.chart_container)
        elif choice == "Tỷ Lệ Thể Loại Sách Trong Kho":
            self.plot_genre_distribution(self.chart_container)
        elif choice == "Tình Trạng Sách Thư Viện (Có sẵn vs Đang mượn)":
            self.plot_book_status(self.chart_container)
        elif choice == "Lượt Mượn Theo Tháng (6 Tháng Gần Nhất)":
            self.plot_borrow_trend(self.chart_container)
        elif choice == "Top 5 Độc Giả Tích Cực Nhất":
            self.plot_top_students(self.chart_container)
        elif choice == "Tỷ Lệ Trạng Thái Phiếu Mượn":
            self.plot_slip_status(self.chart_container)
        elif choice == "Tỷ Lệ Trả Sách Đúng Hạn vs Trễ Hạn":
            self.plot_return_punctuality(self.chart_container)
        elif choice == "Tiền Phạt Phát Sinh Theo Tháng":
            self.plot_fine_trend(self.chart_container)
        elif choice == "Tần Suất Mượn Theo Ngày Trong Tuần":
            self.plot_borrow_by_weekday(self.chart_container)
        elif choice == "Lượt Mượn Sách Theo Thể Loại":
            self.plot_borrow_by_genre(self.chart_container)
        elif choice == "Thời Gian Mượn Trung Bình Theo Thể Loại":
            self.plot_avg_duration_by_genre(self.chart_container)
        elif choice == "Phân Bố Độ Dài Mượn Sách":
            self.plot_duration_distribution(self.chart_container)
        elif choice == "Số Lượng Sách Có Sẵn Theo Thể Loại":
            self.plot_available_by_genre(self.chart_container)
        elif choice == "Top 5 Sách Bị Quá Hạn Nhiều Nhất":
            self.plot_most_overdue_books(self.chart_container)

    def create_group_card(self, parent, title, icon, row, col):
        card = ctk.CTkFrame(parent, fg_color="#1e293b", corner_radius=12, border_color="#334155", border_width=1)
        card.grid(row=row, column=col, padx=8, pady=5, sticky="nsew")
        
        header_lbl = ctk.CTkLabel(
            card, text=f"{icon}  {title}", 
            font=ctk.CTkFont(size=12, weight="bold"), 
            text_color="#94a3b8"
        )
        header_lbl.pack(anchor="w", padx=15, pady=(15, 10))
        
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        return content_frame

    def add_kpi_item(self, parent, label, value, color, is_row=True):
        item_frame = ctk.CTkFrame(parent, fg_color="transparent")
        if is_row:
            item_frame.pack(fill="x", pady=4)
            lbl = ctk.CTkLabel(item_frame, text=label, font=ctk.CTkFont(size=13), text_color="#94a3b8")
            lbl.pack(side="left")
            val = ctk.CTkLabel(item_frame, text=str(value), font=ctk.CTkFont(size=16, weight="bold"), text_color=color)
            val.pack(side="right")
        else:
            item_frame.pack(side="left", fill="both", expand=True, padx=5)
            val = ctk.CTkLabel(item_frame, text=str(value), font=ctk.CTkFont(size=28, weight="bold"), text_color=color)
            val.pack(pady=(5, 2))
            lbl = ctk.CTkLabel(item_frame, text=label, font=ctk.CTkFont(size=12, weight="normal"), text_color="#94a3b8")
            lbl.pack()

    # ==================== CÁC PHƯƠNG THỨC VẼ BIỂU ĐỒ ====================

    def plot_popular_books(self, parent):
        popular_books = self.stats.get("popular_books", [])
        if not popular_books:
            self.show_no_data(parent, "Top 5 Sách Mượn Nhiều Nhất")
            return

        names = [b["name"][:25] + '...' if len(b["name"]) > 25 else b["name"] for b in popular_books]
        counts = [b["count"] for b in popular_books]
        names.reverse()
        counts.reverse()

        fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=100, facecolor='#1e293b')
        ax.set_facecolor('#1e293b')

        bars = ax.barh(names, counts, color='#3b82f6', height=0.5)
        ax.set_title('Top 5 Sách Mượn Nhiều Nhất', color='#f8fafc', fontsize=12, fontweight='bold', pad=15)
        ax.tick_params(colors='#94a3b8', labelsize=9)
        
        for spine in ax.spines.values():
            spine.set_visible(False)
            
        ax.bar_label(bars, padding=8, color='#f8fafc', fontsize=9.5, fontweight='bold')
        plt.tight_layout()
        self.embed_chart(fig, parent)

    def plot_genre_distribution(self, parent):
        genre_counts = self.stats.get("genre_counts", {})
        if not genre_counts:
            self.show_no_data(parent, "Tỷ Lệ Thể Loại Sách Trong Kho")
            return

        sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
        top_genres = sorted_genres[:6]
        other_sum = sum(x[1] for x in sorted_genres[6:])
        
        labels = [g[0] for g in top_genres]
        sizes = [g[1] for g in top_genres]
        if other_sum > 0:
            labels.append("Khác")
            sizes.append(other_sum)

        fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=100, facecolor='#1e293b')
        ax.set_facecolor('#1e293b')

        colors = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ec4899', '#f43f5e', '#64748b']
        
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, 
               textprops={'color':'#f8fafc', 'fontsize':9}, 
               colors=colors[:len(sizes)],
               wedgeprops=dict(width=0.4, edgecolor='#1e293b', linewidth=2),
               pctdistance=0.75)
        
        ax.set_title('Tỷ Lệ Thể Loại Sách Trong Kho', color='#f8fafc', fontsize=12, fontweight='bold', pad=15)
        plt.tight_layout()
        self.embed_chart(fig, parent)

    def plot_book_status(self, parent):
        available = self.stats.get("available_books", 0)
        borrowed = self.stats.get("borrowed_books", 0)
        damaged = self.stats.get("damaged_books", 0)
        if available == 0 and borrowed == 0 and damaged == 0:
            self.show_no_data(parent, "Tình Trạng Sách Thư Viện")
            return

        labels = ['Có sẵn', 'Đang mượn', 'Hư hỏng']
        sizes = [available, borrowed, damaged]
        filtered = [(l, s) for l, s in zip(labels, sizes) if s > 0]
        if not filtered:
            self.show_no_data(parent, "Tình Trạng Sách Thư Viện")
            return
        labels, sizes = zip(*filtered)

        colors = {'Có sẵn': '#10b981', 'Đang mượn': '#f59e0b', 'Hư hỏng': '#ef4444'}
        pie_colors = [colors[l] for l in labels]

        fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=100, facecolor='#1e293b')
        ax.set_facecolor('#1e293b')

        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, 
               textprops={'color':'#f8fafc', 'fontsize':9}, 
               colors=pie_colors,
               wedgeprops=dict(width=0.4, edgecolor='#1e293b', linewidth=2),
               pctdistance=0.75)
               
        ax.set_title('Tình Trạng Sách Thư Viện', color='#f8fafc', fontsize=12, fontweight='bold', pad=15)
        plt.tight_layout()
        self.embed_chart(fig, parent)

    def plot_borrow_trend(self, parent):
        borrows_by_month = self.stats.get("borrows_by_month", {})
        if not borrows_by_month:
            self.show_no_data(parent, "Lượt Mượn Theo Tháng (6 Tháng Gần Nhất)")
            return

        months = list(borrows_by_month.keys())
        counts = list(borrows_by_month.values())

        fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=100, facecolor='#1e293b')
        ax.set_facecolor('#1e293b')

        ax.plot(months, counts, marker='o', color='#10b981', linewidth=3, markersize=7)
        ax.fill_between(months, counts, color='#10b981', alpha=0.15)
        
        ax.set_title('Lượt Mượn Theo Tháng (6 Tháng Gần Nhất)', color='#f8fafc', fontsize=12, fontweight='bold', pad=15)
        ax.tick_params(colors='#94a3b8', labelsize=9)
        
        for spine in ax.spines.values():
            spine.set_visible(False)
            
        ax.grid(True, color='#334155', linestyle=':', alpha=0.5)
        plt.tight_layout()
        self.embed_chart(fig, parent)

    def plot_top_students(self, parent):
        top_students = self.stats.get("top_students", [])
        if not top_students:
            self.show_no_data(parent, "Top 5 Độc Giả Tích Cực Nhất")
            return

        names = [s["name"][:20] + '...' if len(s["name"]) > 20 else s["name"] for s in top_students]
        counts = [s["count"] for s in top_students]
        names.reverse()
        counts.reverse()

        fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=100, facecolor='#1e293b')
        ax.set_facecolor('#1e293b')

        bars = ax.barh(names, counts, color='#8b5cf6', height=0.5)
        ax.set_title('Top 5 Độc Giả Tích Cực Nhất (Mượn nhiều nhất)', color='#f8fafc', fontsize=12, fontweight='bold', pad=15)
        ax.tick_params(colors='#94a3b8', labelsize=9)
        
        for spine in ax.spines.values():
            spine.set_visible(False)
            
        ax.bar_label(bars, padding=8, color='#f8fafc', fontsize=9.5, fontweight='bold')
        plt.tight_layout()
        self.embed_chart(fig, parent)

    def plot_slip_status(self, parent):
        counts = self.stats.get("slip_status_counts", {})
        if not counts or sum(counts.values()) == 0:
            self.show_no_data(parent, "Tỷ Lệ Trạng Thái Phiếu Mượn")
            return

        labels = ['Đang mượn', 'Đã trả', 'Quá hạn']
        sizes = [counts.get("Borrowed", 0), counts.get("Returned", 0), counts.get("Overdue", 0)]
        filtered = [(l, s) for l, s in zip(labels, sizes) if s > 0]
        if not filtered:
            self.show_no_data(parent, "Tỷ Lệ Trạng Thái Phiếu Mượn")
            return
        labels, sizes = zip(*filtered)

        colors = {'Đang mượn': '#f59e0b', 'Đã trả': '#10b981', 'Quá hạn': '#ef4444'}
        pie_colors = [colors[l] for l in labels]

        fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=100, facecolor='#1e293b')
        ax.set_facecolor('#1e293b')

        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, 
               textprops={'color':'#f8fafc', 'fontsize':9}, 
               colors=pie_colors,
               wedgeprops=dict(width=0.4, edgecolor='#1e293b', linewidth=2),
               pctdistance=0.75)
               
        ax.set_title('Tỷ Lệ Trạng Thái Phiếu Mượn', color='#f8fafc', fontsize=12, fontweight='bold', pad=15)
        plt.tight_layout()
        self.embed_chart(fig, parent)

    def plot_return_punctuality(self, parent):
        punctuality = self.stats.get("return_punctuality", {})
        on_time = punctuality.get("OnTime", 0)
        late = punctuality.get("Late", 0)
        if on_time == 0 and late == 0:
            self.show_no_data(parent, "Tỷ Lệ Trả Sách Đúng Hạn vs Trễ Hạn")
            return

        labels = ['Đúng hạn', 'Trễ hạn']
        sizes = [on_time, late]
        colors = ['#10b981', '#ef4444']

        fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=100, facecolor='#1e293b')
        ax.set_facecolor('#1e293b')

        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, 
               textprops={'color':'#f8fafc', 'fontsize':9}, 
               colors=colors,
               wedgeprops=dict(width=0.4, edgecolor='#1e293b', linewidth=2),
               pctdistance=0.75)
               
        ax.set_title('Tỷ Lệ Trả Sách Đúng Hạn vs Trễ Hạn (Trên tổng phiếu đã trả)', color='#f8fafc', fontsize=12, fontweight='bold', pad=15)
        plt.tight_layout()
        self.embed_chart(fig, parent)

    def plot_fine_trend(self, parent):
        fine_trend = self.stats.get("fine_trend", {})
        if not fine_trend:
            self.show_no_data(parent, "Tiền Phạt Phát Sinh Theo Tháng")
            return

        months = list(fine_trend.keys())
        amounts = list(fine_trend.values())

        fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=100, facecolor='#1e293b')
        ax.set_facecolor('#1e293b')

        ax.plot(months, amounts, marker='o', color='#ef4444', linewidth=3, markersize=7)
        ax.fill_between(months, amounts, color='#ef4444', alpha=0.15)
        
        ax.set_title('Tổng Tiền Phạt Phát Sinh Theo Tháng (VNĐ)', color='#f8fafc', fontsize=12, fontweight='bold', pad=15)
        ax.tick_params(colors='#94a3b8', labelsize=9)
        
        # Format các giá trị tiền tệ trên trục y
        ax.get_yaxis().set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        
        for spine in ax.spines.values():
            spine.set_visible(False)
            
        ax.grid(True, color='#334155', linestyle=':', alpha=0.5)
        plt.tight_layout()
        self.embed_chart(fig, parent)

    def plot_borrow_by_weekday(self, parent):
        data = self.stats.get("borrow_by_weekday", {})
        if not data or sum(data.values()) == 0:
            self.show_no_data(parent, "Tần Suất Mượn Theo Ngày Trong Tuần")
            return

        days = list(data.keys())
        counts = list(data.values())

        fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=100, facecolor='#1e293b')
        ax.set_facecolor('#1e293b')

        bars = ax.bar(days, counts, color='#0ea5e9', width=0.55)
        ax.set_title('Tần Suất Mượn Sách Theo Ngày Trong Tuần', color='#f8fafc', fontsize=12, fontweight='bold', pad=15)
        ax.tick_params(colors='#94a3b8', labelsize=9)
        
        for spine in ax.spines.values():
            spine.set_visible(False)
            
        ax.bar_label(bars, padding=3, color='#f8fafc', fontsize=9.5, fontweight='bold')
        ax.grid(axis='y', color='#334155', linestyle=':', alpha=0.5)
        plt.tight_layout()
        self.embed_chart(fig, parent)

    def plot_borrow_by_genre(self, parent):
        data = self.stats.get("borrow_by_genre", {})
        if not data:
            self.show_no_data(parent, "Lượt Mượn Sách Theo Thể Loại")
            return

        genres = list(data.keys())
        counts = list(data.values())
        
        genres_sorted = [x for _, x in sorted(zip(counts, genres))]
        counts_sorted = sorted(counts)

        fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=100, facecolor='#1e293b')
        ax.set_facecolor('#1e293b')

        bars = ax.barh(genres_sorted, counts_sorted, color='#10b981', height=0.5)
        ax.set_title('Tổng Lượt Mượn Sách Phân Loại Theo Thể Loại', color='#f8fafc', fontsize=12, fontweight='bold', pad=15)
        ax.tick_params(colors='#94a3b8', labelsize=9)
        
        for spine in ax.spines.values():
            spine.set_visible(False)
            
        ax.bar_label(bars, padding=8, color='#f8fafc', fontsize=9.5, fontweight='bold')
        plt.tight_layout()
        self.embed_chart(fig, parent)

    def plot_avg_duration_by_genre(self, parent):
        data = self.stats.get("avg_duration_by_genre", {})
        if not data:
            self.show_no_data(parent, "Thời Gian Mượn Trung Bình Theo Thể Loại")
            return

        genres = list(data.keys())
        days = list(data.values())

        fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=100, facecolor='#1e293b')
        ax.set_facecolor('#1e293b')

        bars = ax.bar(genres, days, color='#f59e0b', width=0.55)
        ax.set_title('Thời Gian Mượn Sách Trung Bình Theo Thể Loại (Số Ngày)', color='#f8fafc', fontsize=12, fontweight='bold', pad=15)
        ax.tick_params(colors='#94a3b8', labelsize=9)
        
        for spine in ax.spines.values():
            spine.set_visible(False)
            
        ax.bar_label(bars, padding=3, color='#f8fafc', fontsize=9.5, fontweight='bold')
        ax.grid(axis='y', color='#334155', linestyle=':', alpha=0.5)
        plt.tight_layout()
        self.embed_chart(fig, parent)

    def plot_duration_distribution(self, parent):
        data = self.stats.get("duration_distribution", {})
        if not data or sum(data.values()) == 0:
            self.show_no_data(parent, "Phân Bố Độ Dài Mượn Sách")
            return

        intervals = list(data.keys())
        counts = list(data.values())

        fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=100, facecolor='#1e293b')
        ax.set_facecolor('#1e293b')

        bars = ax.bar(intervals, counts, color='#e11d48', width=0.55)
        ax.set_title('Phân Bố Thời Gian Mượn Sách Thực Tế (Số ngày)', color='#f8fafc', fontsize=12, fontweight='bold', pad=15)
        ax.tick_params(colors='#94a3b8', labelsize=9)
        
        for spine in ax.spines.values():
            spine.set_visible(False)
            
        ax.bar_label(bars, padding=3, color='#f8fafc', fontsize=9.5, fontweight='bold')
        ax.grid(axis='y', color='#334155', linestyle=':', alpha=0.5)
        plt.tight_layout()
        self.embed_chart(fig, parent)

    def plot_available_by_genre(self, parent):
        data = self.stats.get("available_by_genre", {})
        if not data:
            self.show_no_data(parent, "Số Lượng Sách Có Sẵn Theo Thể Loại")
            return

        genres = list(data.keys())
        counts = list(data.values())

        fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=100, facecolor='#1e293b')
        ax.set_facecolor('#1e293b')

        bars = ax.bar(genres, counts, color='#059669', width=0.55)
        ax.set_title('Số Sách Có Sẵn Trong Kho Theo Thể Loại', color='#f8fafc', fontsize=12, fontweight='bold', pad=15)
        ax.tick_params(colors='#94a3b8', labelsize=9)
        
        for spine in ax.spines.values():
            spine.set_visible(False)
            
        ax.bar_label(bars, padding=3, color='#f8fafc', fontsize=9.5, fontweight='bold')
        ax.grid(axis='y', color='#334155', linestyle=':', alpha=0.5)
        plt.tight_layout()
        self.embed_chart(fig, parent)

    def plot_most_overdue_books(self, parent):
        data = self.stats.get("most_overdue_books", [])
        if not data:
            self.show_no_data(parent, "Top 5 Sách Bị Quá Hạn Nhiều Nhất")
            return

        names = [b["name"][:25] + '...' if len(b["name"]) > 25 else b["name"] for b in data]
        counts = [b["count"] for b in data]
        names.reverse()
        counts.reverse()

        fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=100, facecolor='#1e293b')
        ax.set_facecolor('#1e293b')

        bars = ax.barh(names, counts, color='#ef4444', height=0.5)
        ax.set_title('Top 5 Sách Bị Trễ Hạn/Quá Hạn Nhiều Nhất', color='#f8fafc', fontsize=12, fontweight='bold', pad=15)
        ax.tick_params(colors='#94a3b8', labelsize=9)
        
        for spine in ax.spines.values():
            spine.set_visible(False)
            
        ax.bar_label(bars, padding=8, color='#f8fafc', fontsize=9.5, fontweight='bold')
        plt.tight_layout()
        self.embed_chart(fig, parent)

    # ==================== PHƯƠNG THỨC BỔ TRỢ ====================

    def show_no_data(self, parent, title):
        lbl_title = ctk.CTkLabel(
            parent, text=title, 
            font=ctk.CTkFont(size=12, weight="bold"), 
            text_color="#94a3b8"
        )
        lbl_title.pack(pady=15)
        
        lbl_err = ctk.CTkLabel(parent, text="Chưa có đủ dữ liệu để phân tích.", text_color="#64748b", font=ctk.CTkFont(size=13))
        lbl_err.pack(expand=True)

    def embed_chart(self, fig, parent):
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        plt.close(fig)
