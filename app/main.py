from typing import Dict
from fastapi import  Depends, FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
import uvicorn
from database.db import Endpoints, SessionDep
from database.schemas import *
from fastapi.middleware.cors import CORSMiddleware
from auth.auth import security
from fastapi import WebSocket
from fastapi import WebSocketDisconnect
from WebSockets.websocket_manager import manager

app = FastAPI()

app.mount("/static", StaticFiles(directory="templates"), name="static")

active_connection: Dict[int, WebSocket] = {}

origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "https://onlinezapic.cloudpub.ru",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

endpoints = Endpoints()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received message from user {user_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        print(f"User {user_id} disconnected")

@app.get("/account")
async def get_id(request: Request, session: SessionDep):
    return await endpoints.get_user_by_id(request, session)

@app.get("/my_reservations")
async def get_id(request: Request, session: SessionDep):
    return await endpoints.get_reservations_by_id(request, session)

@app.post("/setup-database")
async def setup_database():
    return await endpoints.setup_database()

@app.get("/logout")
def delete_cookie(response: Response):
    response.delete_cookie(key="my_access_token")
    return {"message": "Cookie has been deleted"}

@app.post("/register")
async def register_user(data: UserRegisterSchema, session: SessionDep, response: Response):
    return await endpoints.register_user(data, session, response)

@app.post("/login")
async def login_user(data: UserLoginSchema, session: SessionDep, response: Response):
    return await endpoints.login_user(data, session, response)


@app.get("/employee/{employee_id}", dependencies= [Depends(security.access_token_required)])
async def get_employee_by_id(employee_id: int, session: SessionDep):
    return await endpoints.get_employee_by_id(employee_id, session)
    
@app.get("/get_all_users/", dependencies= [Depends(security.access_token_required)])
async def get_users(session: SessionDep):
    return await endpoints.get_users(session)

@app.delete("/user/{user_id}")
async def delete_user(user_id: int, session: SessionDep):
    return await endpoints.delete_user(user_id, session)

#region CRUD clients
@app.post("/clients/")
async def add_client(data: ClientAddSchema, session: SessionDep):
    return await endpoints.add_client(data, session)

@app.get("/clients/")
async def get_clients(session: SessionDep):
    return await endpoints.get_clients(session)

@app.put("/clients/{client_id}")
async def update_client(client_id: int, data: ClientAddSchema, session: SessionDep):
    return await endpoints.update_client(client_id, data, session)

@app.delete("/clients/{client_id}")
async def delete_client(client_id: int, session: SessionDep):
    return await endpoints.delete_client(client_id, session)
#endregion

#region CRUD employees
@app.post("/employees/")
async def add_employee(data: EmployeeAddSchema, session: SessionDep):
    return await endpoints.add_employee(data, session)

@app.get("/employees/")
async def get_employees(session: SessionDep):
    return await endpoints.get_employees(session)

@app.put("/employees/{employee_id}")
async def update_employee(employee_id: int, data: EmployeeAddSchema, session: SessionDep):
    return await endpoints.update_employee(employee_id, data, session)

@app.delete("/employees/{employee_id}")
async def delete_employee(employee_id: int, session: SessionDep):
    return await endpoints.delete_employee(employee_id, session)
#endregion

#region CRUD notification
@app.post("/notifications/")
async def notification(data: NotificationAddSchema, session: SessionDep):
    return await endpoints.add_notification(data, session)

@app.get("/notifications/")
async def notifications(session: SessionDep):
    return await endpoints.get_notifications(session)
#endregion

#region CRUD reservation
@app.post("/reservations")
async def add_reservation(data: ReservationAddSchema, session: SessionDep):
    return await endpoints.add_reservation(data, session)

@app.get("/reservations")
async def get_reservations(session: SessionDep):
    return await endpoints.get_reservations(session)

@app.put("/reservations/{reservation_id}")
async def update_reservation(reservation_id: int, data: ReservationAddSchema, session: SessionDep):
    return await endpoints.update_reservation(reservation_id, data, session)

@app.delete("/reservations/{reservation_id}")
async def delete_reservation(reservation_id: int, session: SessionDep):
    return await endpoints.delete_reservation(reservation_id, session)
#endregion


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0")