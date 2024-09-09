from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


from app.core import settings



# Конфигурация пула соединений с базой данных
POOL_SIZE = 5  # Размер пула соединений
MAX_OVERFLOW = 10  # Максимальное количество дополнительных соединений, которые могут быть созданы

# Создание асинхронного двигателя для подключения к базе данных
engine = create_async_engine(
    settings.database_url,  # URL для подключения к базе данных
    future=True,  # Использование будущих возможностей SQLAlchemy
    pool_size=POOL_SIZE,  # Размер пула соединений
    max_overflow=MAX_OVERFLOW,  # Максимальное количество дополнительных соединений
)

# Создание фабрики сессий для асинхронного подключения
_async_session = sessionmaker(
    engine, 
    class_=AsyncSession,  # Указываем, что будем использовать асинхронные сессии
    expire_on_commit=False  # Объекты не будут истекать при коммите
)

# Функция для получения асинхронной сессии базы данных
async def get_db_session() -> AsyncIterator[AsyncSession]:
    """
    Создает и предоставляет асинхронную сессию базы данных.

    Yields:
        AsyncSession: Асинхронная сессия базы данных.
    """
    async with _async_session() as session:  # Открываем сессию
        yield session  # Передаем сессию вызывающему коду

# Базовый класс для декларативных моделей SQLAlchemy
class Base(DeclarativeBase):
    """
    Базовый класс для декларативных моделей SQLAlchemy.
    Используется для создания моделей базы данных.
    """
    ...
