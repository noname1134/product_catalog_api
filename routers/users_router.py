from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated

from schemas.users_schema import UserResponse, UserCreate, UserLogin, LoginResponse
from services.users_service import create_user as create_user_service, login_user as login_user_service
from exceptions.user_exceptions import UserAlreadyExistsError, InvalidCredentialsError
from security.auth_dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate):
    try:
        return create_user_service(user)
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/login", response_model=LoginResponse)
def login_user(user: UserLogin):
    try:
        return login_user_service(user.username, user.password)
    except InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="Invalid username or password", headers={"WWW-Authenticate": "Bearer"})


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: Annotated[dict, Depends(get_current_user)]):
    return current_user