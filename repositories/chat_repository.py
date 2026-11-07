import secrets
from redis_client import get_redis_client

CHAT_SESSION_TTL_SECONDS = 3600


def create_chat_session(user_id: int) -> str:
    session_id = secrets.token_urlsafe(32)
    client = get_redis_client()
    session_key = f"chat_session:{session_id}"
    user_sessions_key = f"user_chat_sessions:{user_id}"
    with client.pipeline(transaction=True) as pipe:
        pipe.hset(session_key, mapping={"user_id": user_id, "prompts_used": 0})
        pipe.expire(session_key, CHAT_SESSION_TTL_SECONDS)
        pipe.sadd(user_sessions_key, session_id)
        pipe.expire(user_sessions_key, CHAT_SESSION_TTL_SECONDS)
        pipe.execute()

    return session_id


def get_chat_session(session_id: str) -> dict | None:
    client = get_redis_client()
    data = client.hgetall(f"chat_session:{session_id}")

    if not data:
        return None

    return {
        "user_id": int(data["user_id"]),
        "prompts_used": int(data["prompts_used"]),
    }