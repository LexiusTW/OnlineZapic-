from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class Employee(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    FIO: str
    post: str
    timetable: list
    services: str
    rating: float = Field(ge=0, le=10)