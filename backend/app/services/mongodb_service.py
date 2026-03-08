"""MongoDB service for tax session persistence."""

from datetime import datetime, timezone
from typing import Any

from app.db.mongo import get_sessions_collection
from app.models.tax_session import (
    TaxSessionDocument,
    TaxSessionMetadata,
    TaxSessionStatus,
)
from app.utils.sample_data import SAMPLE_SESSION_ID, get_sample_session


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class MongoTaxSessionService:
    """
    Service abstraction around Mongo sessions collection.

    Falls back to in-memory storage if MongoDB is unavailable so API
    contracts remain testable during hackathon setup.
    """

    _memory_store: dict[str, dict[str, Any]] = {}
    _indexes_initialized: bool = False

    def __init__(self) -> None:
        if SAMPLE_SESSION_ID not in self._memory_store:
            self._memory_store[SAMPLE_SESSION_ID] = get_sample_session()
        self._ensure_indexes()

    @classmethod
    def _ensure_indexes(cls) -> None:
        """Create practical indexes when Mongo is available."""
        if cls._indexes_initialized:
            return
        collection = get_sessions_collection()
        if collection is None:
            return
        collection.create_index("session_id", unique=True)
        collection.create_index("updated_at")
        cls._indexes_initialized = True

    def upsert_session(
        self,
        *,
        session_id: str,
        parsed_data: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> TaxSessionDocument:
        """Create or update a session document."""
        collection = get_sessions_collection()
        now = _utcnow()

        existing = self.get_session_raw(session_id=session_id)
        created_at = now if not existing else existing.get("created_at", now)

        default_inputs = {"filing_status": "single", "deduction_type": "standard"}
        status_payload = existing.get("status", {}) if existing else {}

        metadata_payload = metadata or (existing.get("metadata", {}) if existing else {})

        set_payload: dict[str, Any] = {
            "session_id": session_id,
            "updated_at": now,
            "parsed_data": parsed_data,
            "calculation_inputs": existing.get("calculation_inputs", default_inputs)
            if existing
            else default_inputs,
            "draft_1040": existing.get("draft_1040") if existing else None,
            "chatbot_history": existing.get("chatbot_history", []) if existing else [],
            "status": {
                "parser_status": "completed",
                "calculation_status": status_payload.get("calculation_status", "pending"),
                "chatbot_status": status_payload.get("chatbot_status", "disabled"),
            },
            "metadata": metadata_payload,
        }

        if collection is not None:
            collection.update_one(
                {"session_id": session_id},
                {"$set": set_payload, "$setOnInsert": {"created_at": created_at}},
                upsert=True,
            )
            stored_doc = collection.find_one({"session_id": session_id}, {"_id": 0})
            if stored_doc:
                return TaxSessionDocument.model_validate(stored_doc)

            # Fallback if the document cannot be read back immediately.
            return TaxSessionDocument.model_validate(
                {"created_at": created_at, **set_payload}
            )
        else:
            doc_payload = {"created_at": created_at, **set_payload}
            self._memory_store[session_id] = doc_payload
            return TaxSessionDocument.model_validate(doc_payload)

    def get_session_raw(self, *, session_id: str) -> dict[str, Any] | None:
        """Return raw session document."""
        collection = get_sessions_collection()
        if collection is not None:
            doc = collection.find_one({"session_id": session_id}, {"_id": 0})
            return doc
        return self._memory_store.get(session_id)

    def get_session(self, *, session_id: str) -> TaxSessionDocument | None:
        """Return typed session document or None."""
        doc = self.get_session_raw(session_id=session_id)
        if not doc:
            return None
        return TaxSessionDocument.model_validate(doc)

    def save_draft_1040(
        self,
        *,
        session_id: str,
        draft_1040: dict[str, Any],
        calculation_inputs: dict[str, Any] | None = None,
    ) -> TaxSessionDocument | None:
        """Persist newly calculated draft 1040 values."""
        existing = self.get_session_raw(session_id=session_id)
        if not existing:
            return None

        now = _utcnow()
        status_payload = {
            **existing.get("status", TaxSessionStatus().model_dump()),
            "calculation_status": "completed",
        }
        set_payload: dict[str, Any] = {
            "draft_1040": draft_1040,
            "updated_at": now,
            "status": status_payload,
        }
        if calculation_inputs is not None:
            set_payload["calculation_inputs"] = calculation_inputs

        collection = get_sessions_collection()
        if collection is not None:
            collection.update_one(
                {"session_id": session_id},
                {"$set": set_payload},
                upsert=False,
            )
            stored_doc = collection.find_one({"session_id": session_id}, {"_id": 0})
            if stored_doc:
                return TaxSessionDocument.model_validate(stored_doc)
            return None
        else:
            existing["draft_1040"] = draft_1040
            existing["updated_at"] = now
            existing["status"] = status_payload
            if calculation_inputs is not None:
                existing["calculation_inputs"] = calculation_inputs
            self._memory_store[session_id] = existing

        return TaxSessionDocument.model_validate(existing)

    def append_chat_history(
        self,
        *,
        session_id: str,
        user_message: str,
        assistant_message: str,
    ) -> TaxSessionDocument | None:
        """Append chatbot user/assistant messages to session history."""
        now = _utcnow()
        user_event = {"role": "user", "message": user_message, "timestamp": now.isoformat()}
        assistant_event = {
            "role": "assistant",
            "message": assistant_message,
            "timestamp": now.isoformat(),
        }

        collection = get_sessions_collection()
        if collection is not None:
            result = collection.update_one(
                {"session_id": session_id},
                {
                    "$push": {"chatbot_history": {"$each": [user_event, assistant_event]}},
                    "$set": {"updated_at": now, "status.chatbot_status": "enabled"},
                },
                upsert=False,
            )
            if result.matched_count == 0:
                return None
            stored_doc = collection.find_one({"session_id": session_id}, {"_id": 0})
            if not stored_doc:
                return None
            return TaxSessionDocument.model_validate(stored_doc)

        existing = self._memory_store.get(session_id)
        if not existing:
            return None
        history = existing.get("chatbot_history", [])
        history.extend([user_event, assistant_event])
        existing["chatbot_history"] = history
        existing["updated_at"] = now
        existing["status"] = {
            **existing.get("status", TaxSessionStatus().model_dump()),
            "chatbot_status": "enabled",
        }
        self._memory_store[session_id] = existing
        return TaxSessionDocument.model_validate(existing)

    @staticmethod
    def normalize_metadata(metadata: dict[str, Any] | None) -> dict[str, Any]:
        """Normalize metadata into the expected model shape."""
        return TaxSessionMetadata.model_validate(metadata or {}).model_dump()
