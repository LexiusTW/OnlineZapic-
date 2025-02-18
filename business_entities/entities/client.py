from pydantic import BaseModel, EmailStr, Field
from uuid import UUID, uuid4

class Client(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    FIO: str
    email: EmailStr
