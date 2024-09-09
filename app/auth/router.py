from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Form, Depends, Response, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db_session
from app.auth import schemas as auth_schemas
from app.auth import service as auth_service
from app.auth import dependencies as auth_depends
from app.users import schemas as users_schemas



router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/authorization")


@router.post('/authorization')
async def authorization(
    form_data: Annotated[users_schemas.UserCreate, Depends()],
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db_session)]
    ):
    return await auth_service.authorization(form_data, response, session)


@router.post('/registration', status_code=status.HTTP_200_OK, response_model=auth_schemas.Token)
async def registration(
    form_data: Annotated[users_schemas.UserCreate, Depends()],
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db_session)]
    ):
    return await auth_service.registration(form_data, response, session)


@router.post('/refresh', status_code=status.HTTP_200_OK, response_model=auth_schemas.Token)
async def refresh(tokens: Annotated[auth_schemas.Token, Depends(auth_depends.refresh_access_token)]):
    return tokens