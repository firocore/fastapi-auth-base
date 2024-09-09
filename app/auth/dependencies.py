from typing import Annotated

from fastapi import Depends, Request, Response, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db_session
from app.auth import service as auth_service
from app.auth import schemas as auth_schemas
from app.users import service as users_service
from app.users import schemas as users_schemas


async def refresh_access_token(request: Request, response: Response, session: Annotated[AsyncSession, Depends(get_db_session)]) -> auth_schemas.Token:
    refresh_token = request.cookies.get("refresh_token", None)
    
    if refresh_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthrized!")
    
    payload = auth_service.decode_jwt_token(refresh_token)
    user_id = int(payload.get("sub"))

    access_token = auth_service.create_access_token(user_id)

    response.set_cookie("access_token", access_token)

    return auth_schemas.Token(access_token=access_token, refresh_token=refresh_token)


async def get_current_user(request: Request, session: Annotated[AsyncSession, Depends(get_db_session)]) -> users_schemas.User:
    token = request.cookies.get("access_token", None)
    
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthrized!")
    
    payload = auth_service.decode_jwt_token(token)
    user_id = int(payload.get("sub"))

    user = await users_service.get_user_by_id(user_id, session)

    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found!")

    return users_schemas.User(**user.__dict__)