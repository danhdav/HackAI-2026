"""Optional chatbot route (mock-first)."""

from fastapi import APIRouter, HTTPException

from app.models.chatbot_models import ChatbotAskRequest, ChatbotAskResponse
from app.services.chatbot_service import ChatbotService
from app.services.mongodb_service import MongoTaxSessionService


router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])
chatbot_service = ChatbotService()
session_service = MongoTaxSessionService()


@router.post("/ask/{session_id}", response_model=ChatbotAskResponse)
async def ask_chatbot(session_id: str, payload: ChatbotAskRequest) -> ChatbotAskResponse:
    """
    Ask a question about a stored session and draft values.

    Works in mock mode even when Gemini is disabled.
    """
    session = session_service.get_session(session_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    question_text = payload.resolved_message()
    if not question_text:
        raise HTTPException(status_code=400, detail="Question/message is required.")

    answer = await chatbot_service.answer_question(
        session_id=session_id,
        question=question_text,
        context=session.model_dump(by_alias=True),
    )

    # Best-effort history persistence; don't fail UX if this write misses.
    session_service.append_chat_history(
        session_id=session_id,
        user_message=question_text,
        assistant_message=answer.get("answer", ""),
    )
    return ChatbotAskResponse.model_validate(answer)
