"""Optional chatbot integration service."""

import json
from typing import Any

from app.config import settings


class ChatbotService:
    """Gemini-backed explanation assistant with deterministic fallback."""

    @staticmethod
    def _normalize_context(context: dict[str, Any]) -> dict[str, Any]:
        """Keep only fields relevant for grounded chatbot explanations."""
        parsed = context.get("parsed_data") or {}
        draft = context.get("draft_1040") or {}
        return {
            "parsed_data": {
                "w2": {
                    "box1": ((parsed.get("w2") or {}).get("box1")),
                    "box2": ((parsed.get("w2") or {}).get("box2")),
                },
                "1098t": {
                    "box1": ((parsed.get("1098t") or {}).get("box1")),
                    "box5": ((parsed.get("1098t") or {}).get("box5")),
                },
            },
            "draft_1040": {
                "line_1a": draft.get("line_1a"),
                "line_1z": draft.get("line_1z"),
                "line_9": draft.get("line_9"),
                "line_11a": draft.get("line_11a"),
                "line_11b": draft.get("line_11b"),
                "line_15": draft.get("line_15"),
                "line_16": draft.get("line_16"),
                "line_25a": draft.get("line_25a"),
                "line_25d": draft.get("line_25d"),
                "line_34": draft.get("line_34"),
            },
        }

    @staticmethod
    def _build_system_prompt() -> str:
        """Strict assistant behavior and project scope instructions."""
        return (
            "You are TaxMaxx Assistant, a tax-draft explanation assistant.\n"
            "You must only explain values present in the provided session context.\n"
            "Do not invent fields, forms, or calculations not in context.\n"
            "This project supports only a subset of 1040 lines: 1a, 1z, 9, 11a, 11b, 15, 16, 25a, 25d, 34.\n"
            "Core formulas:\n"
            "- line_1a = W-2 box1\n"
            "- line_1z = line_1a\n"
            "- line_9 = line_1z\n"
            "- line_11a = line_9\n"
            "- line_11b = line_11a\n"
            "- line_15 = max(line_11b - standard deduction, 0)\n"
            "- line_16 = tax from taxable income\n"
            "- line_25a = W-2 box2\n"
            "- line_25d = line_25a\n"
            "- line_34 = max(line_25d - line_16, 0)\n"
            "Privacy rule: personal identity fields (name, SSN, address, credentials) were intentionally not analyzed.\n"
            "If asked about those fields, say user must fill them manually on the 1040 PDF.\n"
            "If asked about unsupported sections, state they are not currently calculated and describe what extra data/rules are needed.\n"
            "Always remind user that the 1040 PDF tab is the primary form reference and app values are guidance for supported fields.\n"
            "Do not claim legal certainty or that taxes are fully filed.\n"
            "Keep responses clear, honest, beginner-friendly, and concise."
        )

    @staticmethod
    def _fallback_response(*, question: str, normalized_context: dict[str, Any]) -> str:
        """Deterministic fallback when Gemini is unavailable."""
        lower = question.lower()
        draft = normalized_context.get("draft_1040") or {}
        w2 = (normalized_context.get("parsed_data") or {}).get("w2") or {}

        if any(token in lower for token in ["ssn", "social security number", "name", "address", "credential"]):
            return (
                "We intentionally did not analyze personal identity fields for privacy/security reasons. "
                "Please fill those fields manually on the 1040 PDF while using the app values for supported calculations."
            )
        if "line 16" in lower or "line_16" in lower:
            return (
                f"Line 16 is your estimated tax from taxable income (line 15). "
                f"In this session, line 15 is {draft.get('line_15', 0)} and line 16 is {draft.get('line_16', 0)}. "
                "The app uses a simplified single-filer bracket function for this MVP."
            )
        if "line 34" in lower or "refund" in lower:
            return (
                f"Line 34 estimates refund as max(line 25d - line 16, 0). "
                f"Here, line 25d is {draft.get('line_25d', 0)} and line 16 is {draft.get('line_16', 0)}, "
                f"so line 34 is {draft.get('line_34', 0)}."
            )
        if "line 1a" in lower or "wages" in lower:
            return (
                f"Line 1a represents wages and comes from W-2 box 1. "
                f"For this session, W-2 box 1 is {w2.get('box1', 0)} and line 1a is {draft.get('line_1a', 0)}."
            )
        if "line 25a" in lower or "withholding" in lower:
            return (
                f"Line 25a comes from W-2 box 2 federal withholding. "
                f"For this session, W-2 box 2 is {w2.get('box2', 0)} and line 25a is {draft.get('line_25a', 0)}."
            )
        if any(token in lower for token in ["unsupported", "not filled", "other section", "schedule"]):
            return (
                "This version only calculates a limited subset of 1040 lines. "
                "Unsupported sections need additional documents, rules, and tax logic before they can be auto-explained."
            )

        return (
            "I can explain supported draft lines and where they came from using your stored session values. "
            "Use the 1040 PDF tab as your form reference, and use TaxMaxx values as guidance for the supported calculated fields."
        )

    async def answer_question(self, *, session_id: str, question: str, context: dict) -> dict:
        """
        Answer tax draft questions for a session.

        TODO: Future work may support user-approved DB value edits via chat actions.
        TODO: Expand explanation coverage as more 1040 lines are implemented.
        """
        normalized_context = self._normalize_context(context)

        if settings.gemini_enabled and settings.gemini_api_key:
            try:
                import google.generativeai as genai

                genai.configure(api_key=settings.gemini_api_key)
                model = genai.GenerativeModel(settings.gemini_model_name or "gemini-1.5-pro")

                prompt_text = (
                    f"{self._build_system_prompt()}\n\n"
                    f"User question: {question}\n\n"
                    "Session context JSON:\n"
                    f"{json.dumps(normalized_context, indent=2)}\n\n"
                    "Answer directly using the session values above."
                )
                response = model.generate_content(prompt_text)
                answer_text = (response.text or "").strip()
                if answer_text:
                    return {
                        "session_id": session_id,
                        "answer": answer_text,
                        "source": "gemini",
                    }
            except Exception as exc:
                # Keep this visible during hackathon integration debugging.
                print("Gemini fallback reason:", exc)

        return {
            "session_id": session_id,
            "answer": self._fallback_response(
                question=question, normalized_context=normalized_context
            ),
            "source": "mock",
        }
