import datetime

from sqlalchemy import ARRAY, String
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String, nullable=False)
    created_date: Mapped[datetime.datetime]
    rubrics: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
