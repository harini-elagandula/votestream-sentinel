
from pydantic import BaseModel, Field


class ElectionCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)


class ElectionResponse(BaseModel):
    id: int
    title: str
    status: str

    model_config = {"from_attributes": True}
