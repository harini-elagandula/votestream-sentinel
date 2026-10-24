
from pydantic import BaseModel, Field


class CandidateCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class CandidateResponse(BaseModel):
    id: int
    name: str
    election_id: int

    model_config = {"from_attributes": True}


class VoteCreate(BaseModel):
    election_id: int = Field(gt=0)
    candidate_id: int = Field(gt=0)
    voter_id: str = Field(min_length=1, max_length=100)
