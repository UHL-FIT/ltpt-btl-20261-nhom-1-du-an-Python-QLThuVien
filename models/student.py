from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from database.db_manager import Base


class Student(Base):
    __tablename__ = 'students'
    
    student_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)

    def __repr__(self):
        return f"<Student(name='{self.name}', student_id='{self.student_id}')>"
