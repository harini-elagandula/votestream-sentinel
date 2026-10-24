
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.candidate import Candidate
from backend.models.election import Election
from backend.models.vote import Vote

router = APIRouter(prefix="/api/v1/results", tags=["Results"])


@router.get("/{election_id}")
def get_results(election_id: int, db: Session = Depends(get_db)):
    election = db.get(Election, election_id)
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")

    rows = (
        db.query(
            Candidate.id,
            Candidate.name,
            func.count(Vote.id).label("votes"),
        )
        .outerjoin(
            Vote,
            (Vote.candidate_id == Candidate.id)
            & (Vote.election_id == election_id),
        )
        .filter(Candidate.election_id == election_id)
        .group_by(Candidate.id, Candidate.name)
        .order_by(Candidate.id)
        .all()
    )

    return {
        "election_id": election_id,
        "results": [
            {"candidate_id": row.id, "candidate": row.name, "votes": row.votes}
            for row in rows
        ],
    }
