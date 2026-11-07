import json

from repositories import chat_repository
from services.products_service import get_products
from exceptions.chat_exceptions import ChatSessionNotFoundError
from schemas.products_schema import ProductResponse
from integrations import shopping_assistant


def get_user_chat_session(user_id: int, session_id: str) -> dict:
    chat_session = chat_repository.get_chat_session(session_id)

    if chat_session is None or chat_session["user_id"] != user_id:
        raise ChatSessionNotFoundError("Chat session not found")

    return chat_session


def create_chat_session(user_id: int) -> str:
    return chat_repository.create_chat_session(user_id)


def get_chat_messages(user_id: int, session_id: str) -> list[dict]:
    get_user_chat_session(user_id, session_id)
    return chat_repository.get_chat_messages(session_id)


def send_chat_message(user_id: int, session_id: str, message: str) -> dict:
    prompts_used = chat_repository.reserve_chat_prompt(user_id, session_id)
    try:
        history = get_chat_messages(user_id, session_id)
        product_context = build_product_context()
        assistant_message = shopping_assistant.generate_reply(history, message, product_context)
        chat_repository.save_chat_turn(user_id, session_id, message, assistant_message)
        return {
            "reply": assistant_message,
            "prompts_remaining": chat_repository.CHAT_PROMPT_LIMIT - prompts_used
        }
    finally:
        chat_repository.release_chat_session(session_id)


def build_product_context() -> str:
    products = get_products([], None, None, None, None)
    catalog = []
    for product in products:
        catalog.append(ProductResponse.model_validate(product).model_dump(mode="json"))

    return json.dumps(catalog)