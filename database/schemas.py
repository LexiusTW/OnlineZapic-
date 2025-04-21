from datetime import datetime, time
from typing import Literal
from pydantic import BaseModel, EmailStr

class UserRegisterSchema(BaseModel):
    fio: str
    email: EmailStr
    login: str
    password: str
    role: Literal["Client", "Employee", "Admin"] = "Client"


class UserLoginSchema(BaseModel):
    login: str
    password: str


# Client
class ClientAddSchema(BaseModel):
    fio: str
    email: str

class ClientSchema(ClientAddSchema):
    id: int

# Employee
class EmployeeAddSchema(BaseModel):
    fio: str
    post: str
    rating: float
    user_id: int

class EmployeeSchema(EmployeeAddSchema):
    id: int

# Notification
class NotificationAddSchema(BaseModel):
    text: str
    user_id: int

class NotificationSchema(NotificationAddSchema):
    id: int

# Reservation
class ReservationAddSchema(BaseModel):
    date: datetime
    employee_id: int
    user_id: int
    service: str

class ReservationSchema(ReservationAddSchema):
    id: int

# Service
class ServiceAddSchema(BaseModel):
    name: str
    duration: time
    price: float

class ServiceSchema(ServiceAddSchema):
    id: int