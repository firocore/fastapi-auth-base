from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Form, Depends, Response, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db_session
from app.auth import schemas as auth_schemas
from app.auth import service as auth_service
from app.auth import dependencies as auth_depends
from app.users import schemas as users_schemas



# Создаем роутер с префиксом "/auth" для всех маршрутов, связанных с авторизацией и регистрацией
router = APIRouter(prefix="/auth", tags=["auth"])

# OAuth2 схема для обработки токенов доступа
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/authorization")


# Маршрут для авторизации пользователя
@router.post('/authorization')
async def authorization(
    form_data: Annotated[users_schemas.UserCreate, Depends()],
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db_session)]
    ):
    """
    Авторизует пользователя на основе предоставленных данных и возвращает токены.

    Args:
        form_data (users_schemas.UserCreate): Данные пользователя (имя и пароль).
        response (Response): Ответ для установки токенов в cookies.
        session (AsyncSession): Сессия базы данных.

    Returns:
        auth_schemas.Token: Токены доступа и обновления.
    """
    return await auth_service.authorization(form_data, response, session)


# Маршрут для регистрации нового пользователя
@router.post('/registration', status_code=status.HTTP_200_OK, response_model=auth_schemas.Token)
async def registration(
    form_data: Annotated[users_schemas.UserCreate, Depends()],
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db_session)]
    ):
    """
    Регистрирует нового пользователя и возвращает токены.

    Args:
        form_data (users_schemas.UserCreate): Данные для создания пользователя.
        response (Response): Ответ для установки токенов в cookies.
        session (AsyncSession): Сессия базы данных.

    Returns:
        auth_schemas.Token: Токены доступа и обновления.
    """
    return await auth_service.registration(form_data, response, session)


# Маршрут для обновления токена доступа
@router.post('/refresh', status_code=status.HTTP_200_OK, response_model=auth_schemas.Token)
async def refresh(tokens: Annotated[auth_schemas.Token, Depends(auth_depends.refresh_access_token)]):
    """
    Обновляет токен доступа на основе предоставленного токена обновления.

    Args:
        tokens (auth_schemas.Token): Токен обновления и новый токен доступа.

    Returns:
        auth_schemas.Token: Новый токен доступа и старый токен обновления.
    """
    return tokens
