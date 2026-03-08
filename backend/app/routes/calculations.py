"""Calculation and draft retrieval routes."""

from fastapi import APIRouter, HTTPException

from app.models.response_models import Draft1040Response
from app.services.calculation_service import CalculationService
from app.services.mongodb_service import MongoTaxSessionService

router = APIRouter(prefix="/api/calculations", tags=["calculations"])
calculation_service = CalculationService()
session_service = MongoTaxSessionService()


@router.post("/run/{session_id}", response_model=Draft1040Response)
async def run_calculations(session_id: str) -> Draft1040Response:
    """Compute, store, and return draft 1040 fields."""
    existing = session_service.get_session(session_id=session_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Session not found.")

    draft = calculation_service.compute_draft_1040(
        parsed_data=existing.parsed_data.model_dump(by_alias=True)
    )
    updated = session_service.save_draft_1040(
        session_id=session_id,
        draft_1040=draft.model_dump(),
    )
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to persist draft.")

    return Draft1040Response(session_id=session_id, draft_1040=draft)


@router.get("/draft/{session_id}", response_model=Draft1040Response)
async def get_draft_1040(session_id: str) -> Draft1040Response:
    """Return only draft 1040 values for frontend consumption."""
    existing = session_service.get_session(session_id=session_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Session not found.")
    if not existing.draft_1040:
        raise HTTPException(status_code=404, detail="Draft 1040 not available yet.")
    return Draft1040Response(session_id=session_id, draft_1040=existing.draft_1040)
