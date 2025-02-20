from pydantic import BaseModel


class ClientAddSchema(BaseModel):
    fio: str
    email: str

class ClientSchema(ClientAddSchema):
    id: int

