"""Tax session create/update/retrieve routes."""

from fastapi import APIRouter, HTTPException

from app.models.tax_session import (
    TaxSessionDocument,
    UpsertTaxSessionRequest,
    UpsertTaxSessionResponse,
)
from app.services.mongodb_service import MongoTaxSessionService

router = APIRouter(prefix="/api/tax-session", tags=["tax-session"])
session_service = MongoTaxSessionService()


@router.post("/upsert", response_model=UpsertTaxSessionResponse)
async def upsert_tax_session(payload: UpsertTaxSessionRequest) -> UpsertTaxSessionResponse:
    """Create or update a tax session document."""
    session = session_service.upsert_session(
        session_id=payload.session_id,
        parsed_data=payload.parsed_data.model_dump(by_alias=True),
        metadata=session_service.normalize_metadata(
            payload.metadata.model_dump() if payload.metadata else None
        ),
    )
    return UpsertTaxSessionResponse(
        session_id=payload.session_id,
        message="Session upserted successfully.",
        session=session,
    )


@router.get("/{session_id}", response_model=TaxSessionDocument)
async def get_tax_session(session_id: str) -> TaxSessionDocument:
    """Fetch a full stored tax session document."""
    session = session_service.get_session(session_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return session
