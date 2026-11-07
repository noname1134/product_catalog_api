import secrets
import json

from redis_client import get_redis_client
from exceptions.chat_exceptions import ChatSessionNotFoundError, ChatPromptLimitError
from repositories.chat_scripts import RESERVE_CHAT_PROMPT_SCRIPT, SAVE_CHAT_TURN_SCRIPT

CHAT_SESSION_TTL_SECONDS = 3600
CHAT_PROMPT_LIMIT = 5


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


def reserve_chat_prompt(user_id: int, session_id: str) -> int:
    client = get_redis_client()
    result = client.eval(RESERVE_CHAT_PROMPT_SCRIPT, 1, f"chat_session:{session_id}", str(user_id), CHAT_PROMPT_LIMIT)
    if result == -1:
        raise ChatSessionNotFoundError("Chat session not found")
    if result == 0:
        raise ChatPromptLimitError("Chat session limit reached")
    return int(result)


def get_chat_messages(session_id: str) -> list[dict]:
    client = get_redis_client()
    key = f"chat_messages:{session_id}"
    entries = client.lrange(key, 0, -1)
    return [json.loads(entry) for entry in entries]


def save_chat_turn(user_id: int, session_id: str, user_message: str, assistant_message: str) -> None:
    client = get_redis_client()
    user_entry = json.dumps({"role": "user", "content": user_message})
    assistant_entry = json.dumps({"role": "assistant", "content": assistant_message})
    result = client.eval(SAVE_CHAT_TURN_SCRIPT, 2, f"chat_session:{session_id}", f"chat_messages:{session_id}", str(user_id), user_entry, assistant_entry)
    if result == -1:
        raise ChatSessionNotFoundError("Chat session not found")