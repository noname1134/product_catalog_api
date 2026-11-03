from pydantic import BaseModel, Field, EmailStr
from typing import Literal


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    phone: str = Field(min_length=1, max_length=20)
    country: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1, max_length=100)


class UserResponse(BaseModel):
    user_id: int
    username: str = Field(min_length=1, max_length=255)
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    phone: str = Field(min_length=1, max_length=20)
    country: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1, max_length=100)


class UserLogin(BaseModel):
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=128)


class LoginResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"]