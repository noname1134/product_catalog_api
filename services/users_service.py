from repositories.users_repository import create_user as create_user_repository, get_user_by_id as get_user_by_id_repository
from schemas.users_schema import UserCreate
from security.passwords import hash_password

def create_user(user: UserCreate):
    password_hash = hash_password(user.password)
    user_id = create_user_repository(user, password_hash)
    return get_user_by_id_repository(user_id)