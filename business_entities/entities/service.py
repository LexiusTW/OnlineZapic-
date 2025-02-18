import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class Service(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    duration: datetime.time
    price: float
    employee: str
