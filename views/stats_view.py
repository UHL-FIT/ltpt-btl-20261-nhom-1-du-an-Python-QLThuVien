import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from utils.analysis import DataAnalyzer

class StatsView(ctk.CTkFrame):
    def __init__(self, parent, on_refresh=None):
        super().__init__(parent, fg_color="transparent")
        self.on_refresh = on_refresh
        self.setup_ui()

    def setup_ui(self):
        # Header with Scrollable Area for statistics (to fit everything nicely)
        scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_container.pack(fill="both", expand=True)

        header = ctk.CTkLabel(
            scroll_container, text="Thống kê & Phân tích Thư viện",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        header.pack(anchor="w", pady=(0, 20))

        # Get Stats
        stats = DataAnalyzer.get_library_stats()

        # Analytics Cards Grid (8 Indicators, 2 rows of 4 cards)
        grid_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
        grid_frame.pack(fill="x", pady=(0, 20))
        grid_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Row 1
        self.create_stat_card(grid_frame, "Tổng số sách", stats["total_books"], "#1f538d", 0, 0)
        self.create_stat_card(grid_frame, "Tổng số sinh viên", stats["total_students"], "#9c27b0", 0, 1)
        self.create_stat_card(grid_frame, "Tổng lượt mượn", stats["total_borrows"], "#4caf50", 0, 2)
        self.create_stat_card(grid_frame, "Tỷ lệ quá hạn", f"{stats['overdue_rate']}%", "#f44336", 0, 3)
        
        # Row 2
        self.create_stat_card(grid_frame, "Sách đang mượn", stats["borrowed_books"], "#ff9800", 1, 0)
        self.create_stat_card(grid_frame, "Sách sẵn có", stats["available_books"], "#00bcd4", 1, 1)
        self.create_stat_card(grid_frame, "Phiếu quá hạn", stats["overdue_count"], "#e91e63", 1, 2)
        self.create_stat_card(grid_frame, "Phiếu đã trả", stats["returned_count"], "#3f51b5", 1, 3)

        # Charts Area (2x2 Grid)
        charts_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
        charts_frame.pack(fill="both", expand=True, padx=5, pady=5)
        charts_frame.grid_rowconfigure((0, 1), weight=1)
        charts_frame.grid_columnconfigure((0, 1), weight=1)

        # 4 Chart containers
        c1 = self.create_chart_container(charts_frame, 0, 0)
        c2 = self.create_chart_container(charts_frame, 0, 1)
        c3 = self.create_chart_container(charts_frame, 1, 0)
        c4 = self.create_chart_container(charts_frame, 1, 1)

        self.plot_popular_books(c1, stats["popular_books"])
        self.plot_genre_distribution(c2, stats["genre_counts"])
        self.plot_book_status(c3, stats["available_books"], stats["borrowed_books"])
        self.plot_borrow_trend(c4, stats["borrows_by_month"])

    def create_stat_card(self, parent, title, value, color, row, col):
        card = ctk.CTkFrame(parent, height=100, border_width=2, border_color=color)
        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        card.pack_propagate(False)
        
        title_lbl = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=13, weight="bold"))
        title_lbl.pack(pady=(15, 5))
        
        val_lbl = ctk.CTkLabel(card, text=str(value), font=ctk.CTkFont(size=28, weight="bold"), text_color=color)
        val_lbl.pack()

    def create_chart_container(self, parent, row, col):
        container = ctk.CTkFrame(parent, height=350)
        container.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        return container

    def plot_popular_books(self, parent, popular_books):
        if not popular_books:
            self.show_no_data(parent, "Top 5 Sách Mượn Nhiều Nhất")
            return

        names = [b["name"][:18] + '...' if len(b["name"]) > 18 else b["name"] for b in popular_books]
        counts = [b["count"] for b in popular_books]

        fig, ax = plt.subplots(figsize=(5, 3), dpi=90)
        fig.patch.set_facecolor('#2b2b2b')
        ax.set_facecolor('#2b2b2b')

        bars = ax.barh(names, counts, color='#1f538d')
        ax.set_title('Top 5 Sách Mượn Nhiều Nhất', color='white', fontsize=12, fontweight='bold')
        ax.tick_params(colors='white', labelsize=9)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.bar_label(bars, padding=3, color='white', fontsize=8)

        plt.tight_layout()
        self.embed_chart(fig, parent)

    def plot_genre_distribution(self, parent, genre_counts):
        if not genre_counts:
            self.show_no_data(parent, "Phân Bố Thể Loại Sách")
            return

        # Get top 5 genres, group others
        sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
        top_genres = sorted_genres[:5]
        other_sum = sum(x[1] for x in sorted_genres[5:])
        
        labels = [g[0] for g in top_genres]
        sizes = [g[1] for g in top_genres]
        if other_sum > 0:
            labels.append("Khác")
            sizes.append(other_sum)

        fig, ax = plt.subplots(figsize=(5, 3), dpi=90)
        fig.patch.set_facecolor('#2b2b2b')
        ax.set_facecolor('#2b2b2b')

        colors = ['#1f538d', '#9c27b0', '#4caf50', '#ff9800', '#00bcd4', '#e91e63']
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, 
               textprops={'color':'white', 'fontsize':8}, colors=colors[:len(sizes)])
        ax.set_title('Tỷ Lệ Thể Loại Sách', color='white', fontsize=12, fontweight='bold')

        plt.tight_layout()
        self.embed_chart(fig, parent)

    def plot_book_status(self, parent, available, borrowed):
        if available == 0 and borrowed == 0:
            self.show_no_data(parent, "Trạng Thái Thư Viện")
            return

        labels = ['Có sẵn', 'Đang mượn']
        sizes = [available, borrowed]
        colors = ['#00bcd4', '#ff9800']

        fig, ax = plt.subplots(figsize=(5, 3), dpi=90)
        fig.patch.set_facecolor('#2b2b2b')
        ax.set_facecolor('#2b2b2b')

        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, 
               textprops={'color':'white', 'fontsize':9}, colors=colors)
        ax.set_title('Tình Trạng Sách Thư Viện', color='white', fontsize=12, fontweight='bold')

        plt.tight_layout()
        self.embed_chart(fig, parent)

    def plot_borrow_trend(self, parent, borrows_by_month):
        if not borrows_by_month:
            self.show_no_data(parent, "Xu Hướng Mượn Sách")
            return

        months = list(borrows_by_month.keys())
        counts = list(borrows_by_month.values())

        fig, ax = plt.subplots(figsize=(5, 3), dpi=90)
        fig.patch.set_facecolor('#2b2b2b')
        ax.set_facecolor('#2b2b2b')

        ax.plot(months, counts, marker='o', color='#4caf50', linewidth=2, markersize=5)
        ax.set_title('Lượt Mượn Theo Tháng', color='white', fontsize=12, fontweight='bold')
        ax.tick_params(colors='white', labelsize=9)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.grid(True, color='#444444', linestyle='--', alpha=0.5)

        plt.tight_layout()
        self.embed_chart(fig, parent)

    def show_no_data(self, parent, title):
        lbl_title = ctk.CTkLabel(parent, text=title, font=ctk.CTkFont(size=12, weight="bold"))
        lbl_title.pack(pady=10)
        lbl_err = ctk.CTkLabel(parent, text="Chưa có đủ dữ liệu để phân tích.", text_color="gray")
        lbl_err.pack(expand=True)

    def embed_chart(self, fig, parent):
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        plt.close(fig)
