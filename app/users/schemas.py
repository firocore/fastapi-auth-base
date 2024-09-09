from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(default="username", description="User Username")
    password: str = Field(default="password", description="User Username")


class User(BaseModel):
    id: int
    username: str