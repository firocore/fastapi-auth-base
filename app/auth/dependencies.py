from typing import Annotated

from fastapi import Depends, Request, Response, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db_session
from app.auth import service as auth_service
from app.auth import schemas as auth_schemas
from app.users import service as users_service
from app.users import schemas as users_schemas


# Обновление токена доступа
async def refresh_access_token(
    request: Request, 
    response: Response, 
    session: Annotated[AsyncSession, Depends(get_db_session)]
) -> auth_schemas.Token:
    """
    Обновляет токен доступа на основе предоставленного токена обновления.

    Args:
        request (Request): HTTP запрос, содержащий токен обновления в cookies.
        response (Response): HTTP ответ, в который будет установлен новый токен доступа в cookies.
        session (AsyncSession): Асинхронная сессия базы данных.

    Returns:
        auth_schemas.Token: Новый токен доступа и токен обновления (старый).

    Raises:
        HTTPException: Если токен обновления отсутствует или недействителен.
    """
    # Получаем токен обновления из cookies
    refresh_token = request.cookies.get("refresh_token", None)
    
    # Если токен не найден, выбрасываем ошибку авторизации
    if refresh_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized!")
    
    # Декодируем токен обновления
    payload = auth_service.decode_jwt_token(refresh_token)
    user_id = int(payload.get("sub"))

    # Создаем новый токен доступа
    access_token = auth_service.create_access_token(user_id)

    # Устанавливаем новый токен доступа в cookies
    response.set_cookie("access_token", access_token)

    return auth_schemas.Token(access_token=access_token, refresh_token=refresh_token)


# Получение текущего авторизованного пользователя
async def get_current_user(
    request: Request, 
    session: Annotated[AsyncSession, Depends(get_db_session)]
) -> users_schemas.User:
    """
    Получает текущего авторизованного пользователя на основе токена доступа.

    Args:
        request (Request): HTTP запрос, содержащий токен доступа в cookies.
        session (AsyncSession): Асинхронная сессия базы данных.

    Returns:
        users_schemas.User: Данные авторизованного пользователя.

    Raises:
        HTTPException: Если токен доступа отсутствует, недействителен или пользователь не найден.
    """
    # Получаем токен доступа из cookies
    token = request.cookies.get("access_token", None)
    
    # Если токен не найден, выбрасываем ошибку авторизации
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized!")
    
    # Декодируем токен доступа
    payload = auth_service.decode_jwt_token(token)
    user_id = int(payload.get("sub"))

    # Получаем пользователя по ID
    user = await users_service.get_user_by_id(user_id, session)

    # Если пользователь не найден, выбрасываем ошибку
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found!")

    return users_schemas.User(**user.__dict__)
