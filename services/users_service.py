from repositories.users_repository import create_user as create_user_repository, get_user_by_id as get_user_by_id_repository, get_user_by_username as get_user_by_username_repository
from repositories.sessions_repository import create_session as create_session_repository, get_session_user_id as get_session_user_id_repository, delete_session as delete_session_repository
from schemas.users_schema import UserCreate
from security.passwords import hash_password, verify_password
from exceptions.user_exceptions import InvalidCredentialsError


def create_user(user: UserCreate) -> dict:
    password_hash = hash_password(user.password)
    user_id = create_user_repository(user, password_hash)
    return get_user_by_id_repository(user_id)


def authenticate_user(username: str, password: str) -> dict | None:
    user = get_user_by_username_repository(username)
    if user is None:
        raise InvalidCredentialsError("Invalid username or password")
    if not verify_password(password, user["password_hash"]):
        raise InvalidCredentialsError("Invalid username or password")
    ret_user = get_user_by_id_repository(user["user_id"])
    if ret_user is None:
        raise InvalidCredentialsError("User deleted")
    return ret_user


def login_user(username: str, password: str) -> dict:
    user = authenticate_user(username, password)
    token = create_session_repository(user["user_id"])
    return {
        "access_token": token,
        "token_type": "bearer"
    }

def get_authenticated_user(token: str) -> dict:
     user_id = get_session_user_id_repository(token)
     if user_id is None:
         raise InvalidCredentialsError("Invalid or expired session")
     user = get_user_by_id_repository(user_id)
     if user is None:
         raise InvalidCredentialsError("Invalid or expired session")
     return user


def logout_user(token: str) -> None:
    delete_session_repository(token)