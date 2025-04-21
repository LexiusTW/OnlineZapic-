from datetime import datetime, time
from typing import Annotated
from sqlalchemy import DateTime, text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship



intpk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]

class Base(DeclarativeBase):
    pass

class UserModel(Base):
    __tablename__ = "Users"

    id: Mapped[intpk]
    fio: Mapped[str]
    email: Mapped[str]
    login: Mapped[str]
    password: Mapped[str]
    role: Mapped[str]

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
    rating: Mapped[float]
    user_id: Mapped[int] = mapped_column(ForeignKey("Users.id"))  # Связь с UserModel

class NotificationModel(Base):
    __tablename__ = "Notifications"

    id: Mapped[intpk]
    text: Mapped[str]  # Текст уведомления
    date: Mapped[datetime]  # Дата создания уведомления
    user_id: Mapped[int] = mapped_column(ForeignKey("Users.id"))  # Кому отправлено уведомление
    is_read: Mapped[bool] = mapped_column(default=False)  # Прочитано ли уведомление

class Reservation(Base):
    __tablename__ = "Reservations"

    id: Mapped[intpk]
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    employee_id: Mapped[int] = mapped_column(ForeignKey("Employees.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("Users.id"))
    service: Mapped[str]

class Service(Base):
    __tablename__ = "Services"
    
    id: Mapped[intpk]
    name: Mapped[str]
    duration: Mapped[time] = mapped_column(DateTime(timezone=True))
    price: Mapped[float]