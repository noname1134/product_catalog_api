import secrets
from redis_client import get_redis_client

SESSION_TTL_SECONDS = 3600


def create_session(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    client = get_redis_client()
    session_key = f"session:{token}"
    user_sessions_key = f"user_sessions:{user_id}"
    with client.pipeline(transaction=True) as pipe:
        pipe.set(session_key, user_id, ex=SESSION_TTL_SECONDS)
        pipe.sadd(user_sessions_key, token)
        pipe.expire(user_sessions_key, SESSION_TTL_SECONDS)
        pipe.execute()

    return token


def get_session_user_id(token: str) -> int | None:
    client = get_redis_client()
    user_id = client.get(f"session:{token}")
    if user_id is None:
        return None
    return int(user_id)


def delete_session(token: str) -> None:
    client = get_redis_client()
    session_key = f"session:{token}"
    user_id = client.get(session_key)

    if user_id is None:
        return

    with client.pipeline(transaction=True) as pipe:
        pipe.delete(session_key)
        pipe.srem(f"user_sessions:{user_id}", token)
        pipe.execute()


def delete_user_sessions(user_id: int) -> None:
    client = get_redis_client()
    user_sessions_key = f"user_sessions:{user_id}"
    tokens = client.smembers(user_sessions_key)
    with client.pipeline(transaction=True) as pipe:
        for token in tokens:
            pipe.delete(f"session:{token}")
        pipe.delete(user_sessions_key)
        pipe.execute()