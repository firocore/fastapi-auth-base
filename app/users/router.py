from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.users import schemas as users_schemas
from app.auth import dependencies as auth_depends



router = APIRouter(prefix="/users", tags={"users"})


@router.get('/me')
async def get_current_user(user: Annotated[users_schemas.User, Depends(auth_depends.get_current_user)]):
    return user