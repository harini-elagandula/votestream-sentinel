from sqlalchemy import func
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.candidate import Candidate
from backend.models.election import Election
from backend.models.vote import Vote
from backend.schemas.vote import VoteCreate
from backend.streaming.producer import publish_vote_event
from backend.websocket.manager import manager


router = APIRouter(
    prefix="/api/v1/votes",
    tags=["Votes"],
)


@router.post("", status_code=201)
async def cast_vote(
    data: VoteCreate,
    db: Session = Depends(get_db),
):
    # 1. Check whether the election exists and is open
    election = db.get(Election, data.election_id)

    if not election or election.status != "open":
        raise HTTPException(
            status_code=400,
            detail="Election not found or not open",
        )

    # 2. Check whether the candidate belongs to this election
    candidate = db.get(Candidate, data.candidate_id)

    if not candidate or candidate.election_id != data.election_id:
        raise HTTPException(
            status_code=400,
            detail="Candidate does not belong to this election",
        )

    # 3. Create the vote record
    vote = Vote(
        election_id=data.election_id,
        candidate_id=data.candidate_id,
        voter_id=data.voter_id,
    )

    db.add(vote)

    # 4. Save the vote in PostgreSQL
    try:
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="This voter has already voted in this election",
        )

    # 5. Prepare the Kafka event
    event = {
        "event": "vote_recorded",
        "election_id": data.election_id,
        "candidate_id": data.candidate_id,
        "voter_id": data.voter_id,
    }

    # 6. Publish the event to Kafka
    try:
        publish_vote_event(event)
    except Exception as error:
        print(f"Warning: Kafka event publishing failed: {error}")

        # Get updated vote totals from PostgreSQL
    rows = (
        db.query(
            Candidate.id,
            Candidate.name,
            func.count(Vote.id).label("votes"),
        )
        .outerjoin(
            Vote,
            (Vote.candidate_id == Candidate.id)
            & (Vote.election_id == data.election_id),
        )
        .filter(Candidate.election_id == data.election_id)
        .group_by(Candidate.id, Candidate.name)
        .order_by(Candidate.id)
        .all()
    )

    results = [
        {
            "candidate_id": row.id,
            "candidate": row.name,
            "votes": row.votes,
        }
        for row in rows
    ]

    await manager.broadcast({
    "type": "vote_update",
    "election_id": data.election_id,
    "results": results,
})

    # 8. Return the API response
    return {
        "message": "Vote recorded successfully",
        "election_id": data.election_id,
        "candidate_id": data.candidate_id,
    }
