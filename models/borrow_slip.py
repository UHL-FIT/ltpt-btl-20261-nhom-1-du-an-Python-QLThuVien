from typing import Literal
from sqlalchemy import String, Integer, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from database.db_manager import Base
import datetime


class BorrowSlip(Base):
    __tablename__ = 'borrow_slips'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(String, nullable=False)
    book_isbn: Mapped[str] = mapped_column(String, ForeignKey('books.isbn'), nullable=False)
    borrow_date: Mapped[datetime.date] = mapped_column(Date, default=datetime.date.today)
    expected_return_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    actual_return_date: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    status: Mapped[Literal["Borrowed", "Returned", "Overdue"]] = mapped_column(String, default="Borrowed")

    def __repr__(self):
        return f"<BorrowSlip(student_id='{self.student_id}', book='{self.book_isbn}', status='{self.status}')>"
