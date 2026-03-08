"""Parser service contracts and placeholder implementation."""

from uuid import uuid4

from fastapi import UploadFile

from app.models.parser_models import Form1098TParsedData, ParsedTaxData, W2ParsedData
from app.utils.sample_data import SAMPLE_SESSION_ID, get_sample_parsed_data


class ParserService:
    """Handles intake parsing flow for W-2 and 1098-T."""

    async def parse_documents(
        self,
        *,
        w2_file: UploadFile | None,
        form_1098t_file: UploadFile | None,
        mock_mode: bool,
    ) -> tuple[str, ParsedTaxData, str]:
        """
        Parse uploaded files or return deterministic mock values.

        TODO (Parser Team): Integrate real PDF parsing pipeline.
        TODO (Parser Team): Implement field extraction for only:
            - W-2: box1, box2
            - 1098-T: box1, box5
        TODO (Parser Team): Add parser-level validation and confidence/error metadata.
        """
        if mock_mode:
            sample = get_sample_parsed_data()
            parsed = ParsedTaxData(
                w2=W2ParsedData(**sample.get("w2", {})),
                **{"1098t": Form1098TParsedData(**sample.get("1098t", {}))},
            )
            return SAMPLE_SESSION_ID, parsed, "mock"

        if not w2_file and not form_1098t_file:
            raise ValueError("Provide at least one file or enable mock_mode.")

        # TODO (Parser Team): Replace placeholders with OCR/PDF extraction.
        # TODO (Parser Team): Validate that uploaded files are correct form types.
        # TODO (Parser Team): Return parse errors when required fields are missing.
        w2_data = None
        if w2_file:
            w2_data = W2ParsedData(box1=0.0, box2=0.0)

        t1098_data = None
        if form_1098t_file:
            t1098_data = Form1098TParsedData(box1=0.0, box5=0.0)

        parsed = ParsedTaxData(w2=w2_data, **{"1098t": t1098_data})
        return f"session_{uuid4().hex[:12]}", parsed, "parsed"
