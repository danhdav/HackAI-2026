"""Parser intake routes."""

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.config import settings
from app.models.parser_models import ParseDocumentsResponse
from app.services.parser_service import ParserService

router = APIRouter(prefix="/api/parser", tags=["parser"])
parser_service = ParserService()


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
