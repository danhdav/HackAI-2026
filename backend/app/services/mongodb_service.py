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

    def __init__(self) -> None:
        if SAMPLE_SESSION_ID not in self._memory_store:
            self._memory_store[SAMPLE_SESSION_ID] = get_sample_session()

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

        doc_payload: dict[str, Any] = {
            "session_id": session_id,
            "created_at": created_at,
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
                {"$set": doc_payload, "$setOnInsert": {"created_at": created_at}},
                upsert=True,
            )
        else:
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

    def save_draft_1040(self, *, session_id: str, draft_1040: dict[str, Any]) -> TaxSessionDocument | None:
        """Persist newly calculated draft 1040 values."""
        existing = self.get_session_raw(session_id=session_id)
        if not existing:
            return None

        existing["draft_1040"] = draft_1040
        existing["updated_at"] = _utcnow()
        existing["status"] = {
            **existing.get("status", TaxSessionStatus().model_dump()),
            "calculation_status": "completed",
        }

        collection = get_sessions_collection()
        if collection is not None:
            collection.update_one(
                {"session_id": session_id},
                {"$set": existing},
                upsert=False,
            )
        else:
            self._memory_store[session_id] = existing

        return TaxSessionDocument.model_validate(existing)

    @staticmethod
    def normalize_metadata(metadata: dict[str, Any] | None) -> dict[str, Any]:
        """Normalize metadata into the expected model shape."""
        return TaxSessionMetadata.model_validate(metadata or {}).model_dump()
