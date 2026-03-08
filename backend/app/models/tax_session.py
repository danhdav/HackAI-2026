"""Pydantic models for tax session storage and retrieval."""

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from app.models.parser_models import ParsedTaxData
from app.models.response_models import Draft1040Values


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TaxSessionStatus(BaseModel):
    """Status markers to track workflow progress."""

    parser_status: str = "pending"
    calculation_status: str = "pending"
    chatbot_status: str = "disabled"


class TaxSessionMetadata(BaseModel):
    """Loose metadata bucket for frontend/user context."""

    user_id: str | None = None
    tax_year: int | None = None
    notes: str | None = None
    extras: dict[str, Any] = Field(default_factory=dict)


class TaxSessionDocument(BaseModel):
    """Canonical session document shape in MongoDB."""

    session_id: str
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)
    parsed_data: ParsedTaxData
    calculation_inputs: dict[str, Any] = Field(default_factory=dict)
    draft_1040: Draft1040Values | None = None
    chatbot_history: list[dict[str, str]] = Field(default_factory=list)
    status: TaxSessionStatus = Field(default_factory=TaxSessionStatus)
    metadata: TaxSessionMetadata = Field(default_factory=TaxSessionMetadata)


class UpsertTaxSessionRequest(BaseModel):
    """Contract for creating/updating session data."""

    session_id: str
    parsed_data: ParsedTaxData
    metadata: TaxSessionMetadata | None = None


class UpsertTaxSessionResponse(BaseModel):
    """Returned after session create/update."""

    session_id: str
    message: str
    session: TaxSessionDocument
