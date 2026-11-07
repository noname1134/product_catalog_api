from fastapi import APIRouter, HTTPException

from exceptions.chat_exceptions import ChatSessionNotFoundError
from schemas.chat_schema import ChatSessionResponse, ChatSessionCreated, ChatMessageResponse
from security.auth_dependencies import CurrentUser
from services import chat_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/sessions", status_code=201, response_model=ChatSessionCreated)
def create_session(current_user: CurrentUser):
    session_id = chat_service.create_chat_session(current_user["user_id"])
    return {"session_id": session_id}


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
def get_session(session_id: str, current_user: CurrentUser):
    try:
        return chat_service.get_user_chat_session(current_user["user_id"], session_id)
    except ChatSessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageResponse])
def get_session_messages(session_id: str, current_user: CurrentUser):
    try:
        return chat_service.get_chat_messages(current_user["user_id"], session_id)
    except ChatSessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc