
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class Election(Base):
    __tablename__ = "elections"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="open", nullable=False
    )
