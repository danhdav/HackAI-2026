"""Parser intake routes."""

from datetime import datetime, timezone
from uuid import uuid4

from bson import ObjectId
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.config import settings
from app.db.mongo import get_boxdata_collection
from app.models.parser_models import ParseDocumentsResponse
from app.services.calculation_service import CalculationService
from app.services.mongodb_service import MongoTaxSessionService
from app.services.parser_service import ParserService

router = APIRouter(prefix="/api/parser", tags=["parser"])
parser_service = ParserService()
session_service = MongoTaxSessionService()
calculation_service = CalculationService()
_boxdata_memory_store: dict[str, dict] = {}


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.post("/parse", response_model=ParseDocumentsResponse)
async def parse_tax_documents(
    mock_mode: bool = Form(settings.use_mock_parser_by_default),
    w2_file: UploadFile | None = File(default=None),
    form_1098t_file: UploadFile | None = File(default=None),
) -> ParseDocumentsResponse:
    """
    Parse W-2 / 1098-T files or return mock parsed data.

    Supports:
    - multipart upload with `w2_file` and/or `form_1098t_file`
    - `mock_mode=true` to bypass parser implementation

    TODO (Parser Team): Add stronger file validation and parser option flags.
    TODO (Parser Team): Add structured error mapping for parser failures.
    """
    try:
        session_id, parsed_data, source = await parser_service.parse_documents(
            w2_file=w2_file,
            form_1098t_file=form_1098t_file,
            mock_mode=mock_mode,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ParseDocumentsResponse(session_id=session_id, parsed_data=parsed_data, source=source)


@router.post("/box-data")
async def get_box_data(
    files: list[UploadFile] = File(...),
    mock_mode: bool = Form(False),
) -> dict:
    """
    Daniel-compatible endpoint used by frontend upload flow.

    It also integrates with the canonical session + draft pipeline.
    """
    try:
        session_id, parsed_data, source, box_data, calculations = (
            await parser_service.parse_files_for_frontend(files=files, mock_mode=mock_mode)
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Parser failed: {exc}") from exc

    # Integrate parser output into canonical TaxMaxx session flow.
    session_service.upsert_session(
        session_id=session_id,
        parsed_data=parsed_data.model_dump(by_alias=True),
        metadata=session_service.normalize_metadata(
            {
                "notes": "Auto-created from /api/parser/box-data flow",
                "extras": {"uploaded_filenames": [upload.filename for upload in files]},
            }
        ),
    )
    draft = calculation_service.compute_draft_1040(
        parsed_data=parsed_data.model_dump(by_alias=True)
    )
    calc_inputs = calculation_service.build_calculation_inputs(
        parsed_data=parsed_data.model_dump(by_alias=True)
    )
    session_service.save_draft_1040(
        session_id=session_id,
        draft_1040=draft.model_dump(),
        calculation_inputs=calc_inputs,
    )

    return {
        "session_id": session_id,
        "source": source,
        "calculations": calculations,
        "box_data": box_data,
        "draft_1040": draft.model_dump(),
    }


@router.post("/box-data/store")
async def store_box_data(payload: dict) -> dict:
    """Store parser raw output and optional frontend result sections."""
    if "box_data" not in payload:
        raise HTTPException(status_code=400, detail="Missing 'box_data' in request body.")

    document = {
        "box_data": payload["box_data"],
        "results_sections": payload.get("results_sections"),
        "created_at": _utcnow_iso(),
        "updated_at": _utcnow_iso(),
    }

    collection = get_boxdata_collection()
    if collection is not None:
        result = collection.insert_one(document)
        return {"id": str(result.inserted_id)}

    doc_id = uuid4().hex
    _boxdata_memory_store[doc_id] = document
    return {"id": doc_id}


@router.put("/box-data/{doc_id}")
async def update_box_data(doc_id: str, payload: dict) -> dict:
    """Update results sections for a stored parser document."""
    if "results_sections" not in payload:
        raise HTTPException(status_code=400, detail="Missing 'results_sections' in request body.")

    collection = get_boxdata_collection()
    if collection is not None:
        try:
            object_id = ObjectId(doc_id)
        except Exception as exc:
            raise HTTPException(status_code=400, detail="Invalid document id.") from exc

        result = collection.update_one(
            {"_id": object_id},
            {
                "$set": {
                    "results_sections": payload["results_sections"],
                    "updated_at": _utcnow_iso(),
                }
            },
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Document not found.")
        return {"status": "updated", "id": doc_id}

    if doc_id not in _boxdata_memory_store:
        raise HTTPException(status_code=404, detail="Document not found.")
    _boxdata_memory_store[doc_id]["results_sections"] = payload["results_sections"]
    _boxdata_memory_store[doc_id]["updated_at"] = _utcnow_iso()
    return {"status": "updated", "id": doc_id}


@router.delete("/box-data/{doc_id}")
async def delete_box_data(doc_id: str) -> dict:
    """Delete a stored parser document by id."""
    collection = get_boxdata_collection()
    if collection is not None:
        try:
            object_id = ObjectId(doc_id)
        except Exception as exc:
            raise HTTPException(status_code=400, detail="Invalid document id.") from exc

        result = collection.delete_one({"_id": object_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Document not found.")
        return {"status": "deleted", "id": doc_id}

    if doc_id not in _boxdata_memory_store:
        raise HTTPException(status_code=404, detail="Document not found.")
    _boxdata_memory_store.pop(doc_id, None)
    return {"status": "deleted", "id": doc_id}
