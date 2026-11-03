import secrets
from redis_client import get_redis_client


def create_session(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    client = get_redis_client()
    session_key = f"session:{token}"
    client.set(session_key, user_id, ex=3600)
    return token


def get_session_user_id(token: str) -> int | None:
    client = get_redis_client()
    user_id = client.get(f"session:{token}")
    if user_id is None:
        return None
    return int(user_id)


def delete_session(token: str) -> None:
    client = get_redis_client()
    client.delete(f"session:{token}")