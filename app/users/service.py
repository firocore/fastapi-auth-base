from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.users import schemas as users_schemas
from app.users import models as users_models
from app.auth import service as auth_service


# Создание нового пользователя
async def create_user(form_data: users_schemas.UserCreate, session: AsyncSession):
    """
    Создает нового пользователя в базе данных.

    Args:
        form_data (users_schemas.UserCreate): Данные для создания пользователя (включая имя пользователя и пароль).
        session (AsyncSession): Асинхронная сессия базы данных.

    Returns:
        users_models.Users: Новый созданный пользователь.

    Raises:
        HTTPException: Если имя пользователя уже существует в базе данных.
    """
    # Проверяем, существует ли пользователь с таким именем
    if await get_user_by_username(form_data.username, session) is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists!")

    # Создаем нового пользователя с хешированным паролем
    new_user = users_models.Users(
        **form_data.model_dump(exclude={"password"}),  # Извлекаем данные формы, кроме пароля
        hashed_password=auth_service.get_password_hash(form_data.password)  # Хешируем пароль
    )
    
    session.add(new_user)  # Добавляем нового пользователя в сессию

    await session.flush()  # Применяем изменения в базе данных

    return new_user


# Получение пользователя по имени пользователя
async def get_user_by_username(username: str, session: AsyncSession):
    """
    Получает пользователя из базы данных по имени пользователя.

    Args:
        username (str): Имя пользователя для поиска.
        session (AsyncSession): Асинхронная сессия базы данных.

    Returns:
        users_models.Users or None: Найденный пользователь или None, если пользователь не найден.
    """
    # Формируем SQL-запрос для поиска пользователя по имени
    statement = select(users_models.Users).where(users_models.Users.username == username)
    result = await session.execute(statement)  # Выполняем запрос
    return result.scalars().first()  # Возвращаем первого найденного пользователя или None


# Получение пользователя по ID
async def get_user_by_id(user_id: int, session: AsyncSession):
    """
    Получает пользователя из базы данных по ID.

    Args:
        user_id (int): Идентификатор пользователя для поиска.
        session (AsyncSession): Асинхронная сессия базы данных.

    Returns:
        users_models.Users or None: Найденный пользователь или None, если пользователь не найден.
    """
    # Формируем SQL-запрос для поиска пользователя по ID
    statement = select(users_models.Users).where(users_models.Users.id == user_id)
    result = await session.execute(statement)  # Выполняем запрос
    return result.scalars().first()  # Возвращаем первого найденного пользователя или None

