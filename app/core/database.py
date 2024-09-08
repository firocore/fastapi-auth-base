from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


from app.core import settings


# Параметры пула соединений
POOL_SIZE = 5
MAX_OVERFLOW = 10

# Создаем асинхронный engine с использованием asyncpg
engine = create_async_engine(
    settings.database_url, 
    future=True,
    pool_size=POOL_SIZE,    # Размер пула соединений
    max_overflow=MAX_OVERFLOW,  # Максимальное количество "дополнительных" соединений
    )

_async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with _async_session() as session:
        yield session


class Base(DeclarativeBase):
    ...
