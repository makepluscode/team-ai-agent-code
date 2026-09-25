from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class ChatRequest(BaseModel):
    message: str = Field(..., description="사용자 질문 또는 지시")

class ChatResponse(BaseModel):
    id: str
    user_message: str
    reply: str
    route: Literal["local", "api"] = Field(..., description="처리 경로: 로컬 LLM 또는 상용 API")
    route_label: str
    timestamp: str
    redacted: bool = False
    details: Optional[str] = None

class MeetingMinutes(BaseModel):
    id: str
    title: str
    date: str
    attendees: list[str]
    agenda: str
    decisions: list[str]
    action_items: list[dict[str, str]]

class KPIData(BaseModel):
    pending_inquiries: int = 3
    today_meetings: int = 2
    wiki_articles: int = 28
    protection_rate: str = "100%"
    blocked_leaks: int = 14
