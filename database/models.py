import datetime
import enum
from typing import Annotated
from pydantic import EmailStr
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

intpk = Annotated[int, mapped_column(primary_key=True)]

class Base(DeclarativeBase):
    pass

class ClientModel(Base):
    __tablename__ = "Clients"

    id: Mapped[intpk]
    fio: Mapped[str]
    email: Mapped[str]

class EmployeeModel(Base):
    __tablename__ = "Employees"

    id: Mapped[intpk]
    fio: Mapped[str]
    post: Mapped[str]
    timetable: Mapped[str]
    services: Mapped[str]
    rating: Mapped[float]

class NotificationModel(Base):
    __tablename__ = "Notifications"

    id: Mapped[intpk] = mapped_column(primary_key=True)
    text: Mapped[str]
    date: Mapped[datetime.datetime]

class EnumStatus(enum.Enum):
    active = "активна",
    ended = "завершена", 
    cancelled = "отменена"

class Reservation(Base):
    __tablename__ = "Reservations"

    id: Mapped[intpk]
    date: Mapped[datetime.datetime]
    status: Mapped[EnumStatus]
    client: Mapped[str]
    employee: Mapped[str]
    service: Mapped[str]
    price: Mapped[float]

class Service(Base):
    __tablename__ = "Services"
    
    id: Mapped[intpk]
    name: Mapped[str]
    duration: Mapped[datetime.time]
    price: Mapped[float]