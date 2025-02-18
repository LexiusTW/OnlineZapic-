import datetime
from pydantic import BaseModel


class CreateReservationDTO(BaseModel):
    date: datetime
    client: str
    employee: str
    service: str

class GetReservationDTO(BaseModel):
    date: datetime
    client: str
    employee: str
    service: str
    price: float