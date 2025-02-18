import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class Notifications(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    text: str
    date: datetime