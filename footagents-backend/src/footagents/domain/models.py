from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FootballLegend(BaseModel):
    id: str
    name: str
    position: str
    era: str
    perspective: str
    style: str
    career_highlights: str


class ConversationState(BaseModel):
    messages: list
    character_context: str
    character_name: str
    character_perspective: str
    character_style: str
    summary: str = ""


class ChatRequest(BaseModel):
    message: str
    character_id: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    character_id: str
    conversation_id: str
    timestamp: datetime 