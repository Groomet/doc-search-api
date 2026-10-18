from datetime import datetime

from app.db.base import Base
from sqlalchemy import Text, DateTime, CheckConstraint, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY


class Document(Base):
    __tablename__ = "documents"

    __table_args__ = (
        CheckConstraint(
            "length(trim(text)) > 0",
            name="ck_documents_text_not_empty"
        ),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rubrics: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_date: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    