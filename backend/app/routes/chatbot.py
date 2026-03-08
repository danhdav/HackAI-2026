"""Optional chatbot route (mock-first)."""

from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from app.services.chatbot_service import ChatbotService
from app.services.mongodb_service import MongoTaxSessionService


class ChatbotAskRequest(BaseModel):
    question: str


router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])
chatbot_service = ChatbotService()
session_service = MongoTaxSessionService()


@router.post("/ask/{session_id}")
async def ask_chatbot(session_id: str, payload: ChatbotAskRequest) -> dict:
    """
    Ask a question about a stored session and draft values.

    Works in mock mode even when Gemini is disabled.
    """
    session = session_service.get_session(session_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    answer = await chatbot_service.answer_question(
        session_id=session_id,
        question=payload.question,
        context=session.model_dump(by_alias=True),
    )
    return answer
