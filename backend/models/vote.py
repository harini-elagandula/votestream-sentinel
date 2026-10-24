
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class Vote(Base):
    __tablename__ = "votes"

    __table_args__ = (
        UniqueConstraint(
            "election_id",
            "voter_id",
            name="uq_vote_election_voter",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    election_id: Mapped[int] = mapped_column(
        ForeignKey("elections.id"), nullable=False
    )
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"), nullable=False
    )
    voter_id: Mapped[str] = mapped_column(String(100), nullable=False)
