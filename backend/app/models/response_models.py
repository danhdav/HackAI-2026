"""Shared API response models."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response payload."""

    status: str
    service: str


class Draft1040Values(BaseModel):
    """Frontend-friendly shape for draft 1040 fields."""

    line_1a: float
    line_1z: float
    line_9: float
    line_11a: float
    line_11b: float
    line_15: float
    line_16: float
    line_25a: float
    line_25d: float
    line_34: float


class Draft1040Response(BaseModel):
    """Payload for draft-only retrieval endpoint."""

    session_id: str
    draft_1040: Draft1040Values
