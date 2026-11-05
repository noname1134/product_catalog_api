from fastapi import APIRouter, HTTPException, Depends, Response
from typing import Annotated
from fastapi.security import HTTPAuthorizationCredentials

from schemas.users_schema import UserResponse, UserCreate, UserLogin, LoginResponse
from services.users_service import create_user as create_user_service, login_user as login_user_service, logout_user as logout_user_service, delete_account as delete_account_service
from exceptions.user_exceptions import UserAlreadyExistsError, InvalidCredentialsError
from security.auth_dependencies import get_current_user, security_scheme

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate) -> Response:
    try:
        return create_user_service(user)
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.delete("/me", status_code=204)
def delete_user(current_user: Annotated[dict, Depends(get_current_user)]) -> Response:
    if delete_account_service(current_user["user_id"]):
        return Response(status_code=204)
    return Response(status_code=404)


@router.post("/login", response_model=LoginResponse)
def login_user(user: UserLogin):
    try:
        return login_user_service(user.username, user.password)
    except InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="Invalid username or password", headers={"WWW-Authenticate": "Bearer"})


@router.post("/logout", status_code=204)
def logout_user(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)]) -> Response:
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logout_user_service(credentials.credentials)
    return Response(status_code=204)


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: Annotated[dict, Depends(get_current_user)]):
    return current_user