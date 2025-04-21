from datetime import datetime
from typing import Annotated
from fastapi import Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from database.config import settings
from database.models import *
from sqlalchemy import and_, select
from database.schemas import *
from auth.auth import security, config
from WebSockets.websocket_manager import manager


engine = create_async_engine(
    url=settings.DATABASE_URL_asyncpg
)

new_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with new_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]


class Endpoints:
    #создание таблиц
    async def setup_database(self):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        return {"ok" : True}

    async def get_token_cooki(self, request: Request):
        token = request.cookies.get("my_access_token")
        if not token:
            raise HTTPException(status_code=401, detail=f"Token cookie not found")
    
        return token
    
    async def decode_token(self, request: Request):
        token = await self.get_token_cooki(request)
        payload  = security._decode_token(token)
        user_id = payload.decode(token, "SECRET_KEY")
        return user_id.sub
    
    async def register_user(self, data: UserRegisterSchema, session: SessionDep, response: Response):
        # Проверяем, существует ли пользователь с таким email или логином
        existing_user = await session.execute(
            select(UserModel).where((UserModel.email == data.email) | (UserModel.login == data.login))
        )
        if existing_user.scalars().first():
            raise HTTPException(status_code = 409, detail = "error: User already exists")

        new_user = UserModel(
            fio=data.fio,
            email=data.email,
            login=data.login,
            password=data.password,
            role=data.role
        )
        session.add(new_user)
        result = await session.execute(select(UserModel).where(UserModel.login == data.login))
        user = result.scalars().first()
        token = security.create_access_token(uid=str(user.id))
        response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, value=token, httponly=True, secure=True, samesite="none", path="/")
        await session.commit()
        return {"ok": True}
    
    async def login_user(self, data: UserLoginSchema, session: SessionDep, response: Response):
        # Используем and_ для корректного сравнения логина и пароля
        query = select(UserModel).where(
            and_(
                UserModel.login == data.login,
                UserModel.password == data.password
            )
        )
        result = await session.execute(query)
        user = result.scalars().first()

        if user is None:
            raise HTTPException(status_code=401, detail="error: Incorrect login or password")

        token = security.create_access_token(uid=str(user.id))
        response.set_cookie(
        key=config.JWT_ACCESS_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
    )
        await session.commit()
        return {"access_token": token}

    
    async def get_user_by_id(self, request: Request, session: SessionDep):
        user_id = await self.decode_token(request)
        user_id = int(user_id)
        query = select(UserModel).where(UserModel.id == user_id)
        result = await session.execute(query)
        user = result.scalars().first()

        if user is None:
            raise HTTPException(status_code=404, detail= "error: Client not found")
        
        return {"id" : user.id,
                "fio" : user.fio,
                "email" : user.email,
                "login" : user.login,
                "role" : user.role}
    
    async def get_reservations_by_id(self, request: Request, session: SessionDep):
        user_id = await self.decode_token(request)
        user_id = int(user_id)
        query = select(Reservation).where(Reservation.user_id == user_id)
        result = await session.execute(query)
        reservation = result.scalars().all()

        if reservation is None:
            raise HTTPException(status_code=404, detail= "error: Client not found")
        
        return reservation
    
    async def get_users(self, session: SessionDep):
        query = select(UserModel)
        result = await session.execute(query)
        return result.scalars().all()
        
    async def delete_user(user_id: int, session: SessionDep):
        query = select(UserModel).where(UserModel.id == user_id)
        result = await session.execute(query)
        user = result.scalars().first()
    
        if user is None:
            raise HTTPException(status_code=404, detail= "error: Client not found")
    
        await session.delete(user)
        await session.commit()
        return {"ok": True}
    
    
    #region CRUD clients
    #создание клиента
    async def add_client(self, data: ClientAddSchema, session: SessionDep):
        new_client = ClientModel(
            fio = data.fio,
            email = data.email
        )
        session.add(new_client)
        await session.commit()
        return {"ok" : True}
    
    #получение списка клиентов
    async def get_clients(self, session: SessionDep):
        query = select(ClientModel)
        result = await session.execute(query)
        return result.scalars().all()
    
    #обновление клиента
    async def update_client(self, client_id: int, data: ClientAddSchema, session: SessionDep):
        query = select(ClientModel).where(ClientModel.id == client_id)
        result = await session.execute(query)
        client = result.scalars().first()
    
        if client is None:
            raise HTTPException(status_code=404, detail= "error: Client not found")
    
        client.fio = data.fio
        client.email = data.email
    
        await session.commit()
        return {"ok": True}
    
    #удаление клиента
    async def delete_client(self, client_id: int, session: SessionDep):
        query = select(ClientModel).where(ClientModel.id == client_id)
        result = await session.execute(query)
        client = result.scalars().first()
    
        if client is None:
            raise HTTPException(status_code=404, detail= "error: Client not found")
    
        await session.delete(client)
        await session.commit()
        return {"ok": True}
    #endregion

    #region CRUD employees
    #создание сотрудника
    async def add_employee(self, data: EmployeeAddSchema, session: SessionDep):
        new_employee = EmployeeModel(
            fio = data.fio,
            post = data.post,
            rating = data.rating,
            user_id = data.user_id
        )
        session.add(new_employee)
        await session.commit()
        return {"ok" : True}
    
    async def get_employee_by_id(self, employee_id: int, session: SessionDep):
        query = select(EmployeeModel).where(EmployeeModel.id == employee_id)
        result = await session.execute(query)
        return result.scalars().first()

    
    #получение списка сотрудников
    async def get_employees(self, session: SessionDep):
        query = select(EmployeeModel)
        result = await session.execute(query)
        return result.scalars().all()
    
    #обновление сотрудника
    async def update_employee(self, employee_id: int, data: EmployeeAddSchema, session: SessionDep):
        query = select(EmployeeModel).where(EmployeeModel.id == employee_id)
        result = await session.execute(query)
        employee = result.scalars().first()
    
        if employee is None:
            raise HTTPException(status_code=404, detail= "error: Employee not found")
    
        employee.fio = data.fio
        employee.post = data.post
        employee.rating = data.rating
        employee.user_id = data.user_id
    
        await session.commit()
        return {"ok": True}
    
    #удаление сотрудника
    async def delete_employee(self, employee_id: int, session: SessionDep):
        query = select(EmployeeModel).where(EmployeeModel.id == employee_id)
        result = await session.execute(query)
        employee = result.scalars().first()
    
        if employee is None:
            raise HTTPException(status_code=404, detail= "error: Employee not found")
    
        await session.delete(employee)
        await session.commit()
        return {"ok": True}
    #endregion

    #region CRUD notifications
    async def get_unread_notifications(self, user_id: int, session: SessionDep):
        #Возвращает список непрочитанных уведомлений для пользователя.
        query = select(NotificationModel).where(
            and_(
                NotificationModel.user_id == user_id,
                NotificationModel.is_read == False
            )
        )
        result = await session.execute(query)
        return result.scalars().all()
    
    #создание уведомления
    async def add_notification(self, data: NotificationAddSchema, session: SessionDep):
        new_notification = NotificationModel(
            text=data.text,
            date=datetime.now(),  # Текущая дата и время
            user_id=data.user_id,
            is_read=False,  # Уведомление не прочитано
        )
        session.add(new_notification)
        await session.commit()
        return {"ok" : True}

    #получения всех уведомлений
    async def get_notifications(self, session: SessionDep):
        query = select(NotificationModel)
        result = await session.execute(query)
        return result.scalars().all()


    #region CRUD reservations
    #создание бронирования
    async def add_reservation(self, data: ReservationAddSchema, session: SessionDep):
        query = select(Reservation).where(Reservation.date == data.date)
        result = await session.execute(query)
        res = result.scalars().first()

        if res:
            raise HTTPException(status_code=409, detail="error: На данное время уже есть запись")

        # Создаем запись
        new_reservation = Reservation(
            date=data.date,
            employee_id=data.employee_id,
            user_id=data.user_id,
            service=data.service,
        )
        session.add(new_reservation)
        await session.commit()

        # Находим сотрудника
        employee = await session.execute(
            select(EmployeeModel).where(EmployeeModel.id == data.employee_id)
        )
        employee = employee.scalars().first()

        # Находим пользователя, который создал запись
        client = await session.execute(
            select(UserModel).where(UserModel.id == data.user_id)
        )
        client = client.scalars().first()

        if employee and employee.user_id and client:
            # Формируем текст уведомления
            notification_text = (
                f"Новая запись:\n Дата: {data.date}\n Услуга: {data.service}\n Клиент: {client.fio}")

            # Создаем объект NotificationAddSchema
            notification_data = NotificationAddSchema(
                text=notification_text,
                user_id=employee.user_id
            )

            # Сохраняем уведомление в базу данных
            await self.add_notification(notification_data, session)

            # Отправляем уведомление через WebSocket, если сотрудник подключен
            await manager.send_notification(employee.user_id, notification_text)

        return {"ok": True}

    #получение списка бронирований
    async def get_reservations(self, session: SessionDep):
        query = select(Reservation)
        result = await session.execute(query)
        return result.scalars().all()


    #удаление бронирования
    async def delete_reservation(self, reservation_id: int, session: SessionDep):
        query = select(Reservation).where(Reservation.id == reservation_id)
        result = await session.execute(query)
        reservation = result.scalars().first()
        if reservation is None:
            raise HTTPException(status_code=404, detail="Reservation not found")
        await session.delete(reservation)
        await session.commit()
        return {"ok": True}
    #endregion