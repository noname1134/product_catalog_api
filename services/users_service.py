from repositories.users_repository import create_user as create_user_repository, get_user_by_id as get_user_by_id_repository, get_user_by_username as get_user_by_username_repository
from schemas.users_schema import UserCreate
from security.passwords import hash_password, verify_password
from exceptions.user_exceptions import InvalidCredentialsError
from repositories.sessions_repository import create_session as create_session_repository


def create_user(user: UserCreate):
    password_hash = hash_password(user.password)
    user_id = create_user_repository(user, password_hash)
    return get_user_by_id_repository(user_id)


def authenticate_user(username: str, password: str):
    user = get_user_by_username_repository(username)
    if user is None:
        raise InvalidCredentialsError("Invalid username or password")
    if not verify_password(password, user["password_hash"]):
        raise InvalidCredentialsError("Invalid username or password")

    return get_user_by_id_repository(user["user_id"])


def login_user(username: str, password: str):
    user = authenticate_user(username, password)
    token = create_session_repository(user["user_id"])
    return {
        "access_token": token,
        "token_type": "bearer"
    }