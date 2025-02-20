from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from config import settings
from models import Base, ClientModel
from schemas import ClientAddSchema
from sqlalchemy import select

engine = create_async_engine(
    url=settings.DATABASE_URL_asyncpg,
    pool_size=10,  # Максимальное количество соединений в пуле
    max_overflow=20,  # Дополнительные соединения, если пул переполнен
    pool_timeout=30,  # Таймаут ожидания соединения из пула
    pool_recycle=3600
)

app = FastAPI()

new_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with new_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]

@app.post("/setup_database")
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    return {"ok" : True}

@app.post("/add_client")
async def add_client(data: ClientAddSchema, session: SessionDep):
    new_client = ClientModel(
        fio = data.fio,
        email = data.email
    )
    session.add(new_client)
    await session.commit()
    return {"ok" : True}

@app.post("/clients")
async def get_clients(session: SessionDep):
    query = select(ClientModel)
    result = await session.execute(query)
    return result.scalars().all()

@app.put("/update_client/{client_id}")
async def update_client(client_id: int, data: ClientAddSchema, session: SessionDep):
    query = select(ClientModel).where(ClientModel.id == client_id)
    result = await session.execute(query)
    client = result.scalars().first()

    if client is None:
        raise HTTPException(status_code=404, detail= "error: Client not found")

    client.fio = data.fio
    client.email = data.email

    await session.commit()
    return {"ok": True}

@app.delete("/delete_client/{client_id}")
async def delete_client(client_id: int, session: SessionDep):
    query = select(ClientModel).where(ClientModel.id == client_id)
    result = await session.execute(query)
    client = result.scalars().first()

    if client is None:
        raise HTTPException(status_code=404, detail= "error: Client not found")

    await session.delete(client)
    await session.commit()
    return {"ok": True}