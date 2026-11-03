from fastapi import APIRouter, HTTPException

from schemas.users_schema import UserResponse, UserCreate
from services.users_service import create_user as create_user_service
from exceptions.user_exceptions import UserAlreadyExistsError


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate):
    try:
        return create_user_service(user)
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
