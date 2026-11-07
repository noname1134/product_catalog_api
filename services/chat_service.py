from repositories import chat_repository
from exceptions.chat_exceptions import ChatSessionNotFoundError


def get_user_chat_session(user_id: int, session_id: str) -> dict:
    chat_session = chat_repository.get_chat_session(session_id)

    if chat_session is None or chat_session["user_id"] != user_id:
        raise ChatSessionNotFoundError("Chat session not found")

    return chat_session


def create_chat_session(user_id: int) -> str:
    return chat_repository.create_chat_session(user_id)