import datetime
from pydantic import BaseModel


class GetServiceDTO(BaseModel):
    name: str
    duration: datetime.time
    price: float

class CreateServiceDTO(BaseModel):
    name: str
    duration: datetime.time
    price: float
    employee: str