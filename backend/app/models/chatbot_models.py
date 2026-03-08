"""Pydantic models for chatbot API."""

from pydantic import BaseModel, Field


class ChatbotAskRequest(BaseModel):
    """Request payload for chatbot questions."""

    message: str | None = Field(default=None, description="User question text")
    question: str | None = Field(default=None, description="Backward-compatible alias")

    def resolved_message(self) -> str:
        """Return normalized message field."""
        return (self.message or self.question or "").strip()


class ChatbotAskResponse(BaseModel):
    """Response payload for chatbot answers."""

    session_id: str
    answer: str
    source: str
