"""Optional chatbot integration service."""

from app.config import settings


class ChatbotService:
    """Returns mock answers now; Gemini integration can be added later."""

    async def answer_question(self, *, session_id: str, question: str, context: dict) -> dict:
        """
        Answer tax draft questions for a session.

        TODO: Integrate Gemini SDK call when `gemini_enabled` is true.
        TODO: Future work may support DB edits via chatbot actions.
        """
        if settings.gemini_enabled and settings.gemini_api_key:
            # TODO: Replace with actual Gemini client call and prompt engineering.
            return {
                "session_id": session_id,
                "answer": (
                    "Gemini mode is configured but not implemented yet. "
                    "Returning placeholder answer."
                ),
                "source": "gemini_placeholder",
            }

        draft = context.get("draft_1040") or {}
        available_fields = ", ".join(sorted(draft.keys())) if draft else "none yet"
        return {
            "session_id": session_id,
            "answer": (
                "Mock assistant response: I can explain your draft once available. "
                f"Current draft fields: {available_fields}."
            ),
            "source": "mock",
            "question_echo": question,
        }
