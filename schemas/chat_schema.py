from typing import Literal

from pydantic import BaseModel, Field, ConfigDict

class ChatMessageCreate(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    model_config = ConfigDict(str_strip_whitespace=True)


class ChatSessionCreated(BaseModel):
    session_id: str


class ChatSessionResponse(BaseModel):
    user_id: int
    prompts_used: int = Field(ge=0, le=5)


class ChatMessageResponse(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatReplyResponse(BaseModel):
    reply: str
    prompts_remaining: int = Field(ge=0, le=5)