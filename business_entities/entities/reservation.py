import datetime
from typing import Literal
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class Reservation(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    date: datetime
    status: Literal["активна", "завершена", "отменена"]
    client: str
    employee: str
    service: str
    price: float