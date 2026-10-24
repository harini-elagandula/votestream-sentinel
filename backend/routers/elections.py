
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.election import Election
from backend.models.candidate import Candidate
from backend.schemas.election import ElectionCreate, ElectionResponse
from backend.schemas.vote import CandidateCreate, CandidateResponse

router = APIRouter(
    prefix="/api/v1/elections",
    tags=["Elections"],
)


# 1. Create a new election
@router.post(
    "",
    response_model=ElectionResponse,
    status_code=201,
)
def create_election(
    data: ElectionCreate,
    db: Session = Depends(get_db),
):
    election = Election(
        title=data.title,
        status="open",
    )

    db.add(election)
    db.commit()
    db.refresh(election)

    return election


# 2. List all elections
@router.get(
    "",
    response_model=list[ElectionResponse],
)
def list_elections(
    db: Session = Depends(get_db),
):
    return (
        db.query(Election)
        .order_by(Election.id)
        .all()
    )


# 3. Add a candidate to an election
@router.post(
    "/{election_id}/candidates",
    response_model=CandidateResponse,
    status_code=201,
)
def add_candidate(
    election_id: int,
    data: CandidateCreate,
    db: Session = Depends(get_db),
):
    election = db.get(Election, election_id)

    if election is None:
        raise HTTPException(
            status_code=404,
            detail="Election not found",
        )

    candidate = Candidate(
        name=data.name,
        election_id=election_id,
    )

    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    return candidate


# 4. List candidates for a specific election
@router.get(
    "/{election_id}/candidates",
    response_model=list[CandidateResponse],
)
def list_candidates(
    election_id: int,
    db: Session = Depends(get_db),
):
    election = db.get(Election, election_id)

    if election is None:
        raise HTTPException(
            status_code=404,
            detail="Election not found",
        )

    return (
        db.query(Candidate)
        .filter(Candidate.election_id == election_id)
        .order_by(Candidate.id)
        .all()
    )
