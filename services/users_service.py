from repositories import users_repository, sessions_repository
from schemas.users_schema import UserCreate
from security.passwords import hash_password, verify_password
from exceptions.user_exceptions import InvalidCredentialsError


def create_user(user: UserCreate) -> dict:
    password_hash = hash_password(user.password)
    user_id = users_repository.create_user(user, password_hash)
    return users_repository.get_user_by_id(user_id)


def delete_account(user_id: int) -> bool:
    is_deleted = users_repository.delete_user_by_id(user_id)
    if is_deleted:
        sessions_repository.delete_user_sessions(user_id)
    return is_deleted


def authenticate_user(username: str, password: str) -> dict | None:
    user = users_repository.get_user_by_username(username)
    if user is None:
        raise InvalidCredentialsError("Invalid username or password")
    if not verify_password(password, user["password_hash"]):
        raise InvalidCredentialsError("Invalid username or password")
    ret_user = users_repository.get_user_by_id(user["user_id"])
    if ret_user is None:
        raise InvalidCredentialsError("User deleted")
    return ret_user


def login_user(username: str, password: str) -> dict:
    user = authenticate_user(username, password)
    token = sessions_repository.create_session(user["user_id"])
    return {
        "access_token": token,
        "token_type": "bearer"
    }

def get_authenticated_user(token: str) -> dict:
     user_id = sessions_repository.get_session_user_id(token)
     if user_id is None:
         raise InvalidCredentialsError("Invalid or expired session")
     user = users_repository.get_user_by_id(user_id)
     if user is None:
         raise InvalidCredentialsError("Invalid or expired session")
     return user


def logout_user(token: str) -> None:
    sessions_repository.delete_session(token)