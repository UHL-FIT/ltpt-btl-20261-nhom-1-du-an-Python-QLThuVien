from typing import Literal
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from database.db_manager import Base


class Book(Base):
    __tablename__ = 'books'
    
    isbn: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    genre: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[Literal["Available", "Borrowed", "Damaged"]] = mapped_column(String, default="Available")

    def __repr__(self):
        return f"<Book(name='{self.name}', isbn='{self.isbn}', status='{self.status}')>"
