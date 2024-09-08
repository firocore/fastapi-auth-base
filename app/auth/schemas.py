from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    refresh_token: str


class UserAuth(BaseModel):
    username: str = Field(default="username")
    password: str = Field(default="password")