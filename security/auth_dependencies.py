from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from exceptions.user_exceptions import InvalidCredentialsError
from services.users_service import get_authenticated_user

security_scheme = HTTPBearer(auto_error=False)


def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)]) -> dict:
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return get_authenticated_user(credentials.credentials)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


CurrentUser = Annotated[dict, Depends(get_current_user)]