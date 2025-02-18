from pydantic import BaseModel, EmailStr


class RegisterUserDTO(BaseModel):
    FIO: str
    email: EmailStr
    login: str
    password: str

class LoginUserDTO(BaseModel):
    login: str
    password: str

class GetAccountUserDTO(BaseModel):
    FIO: str
    email: EmailStr
    login: str