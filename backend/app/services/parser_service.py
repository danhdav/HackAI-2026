"""Parser service contracts and parser integration implementation."""

from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from fastapi import UploadFile

from app.models.parser_models import Form1098TParsedData, ParsedTaxData, W2ParsedData
from app.services.calculation_service import CalculationService
from app.utils.sample_data import SAMPLE_SESSION_ID, get_sample_parsed_data
from parser.extract import extract_many


class ParserService:
    """Handles intake parsing flow for W-2 and 1098-T."""

    def __init__(self) -> None:
        self.calculation_service = CalculationService()

    @staticmethod
    def _to_float(value: object) -> float:
        if value is None:
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        text = str(value).replace(",", "").replace("$", "").strip()
        try:
            return float(text)
        except ValueError:
            return 0.0

    def _normalize_parsed_data(self, box_data: dict) -> ParsedTaxData:
        """Map Daniel parser field names to normalized backend form shape."""
        w2_fields: dict = {}
        t1098_fields: dict = {}

        for _, doc in box_data.items():
            parsed = doc.get("parsed_data", {})
            if "w2" in parsed:
                w2_fields = parsed["w2"]
            if "1098t" in parsed:
                t1098_fields = parsed["1098t"]

        w2 = W2ParsedData(
            box1=self._to_float(w2_fields.get("WagesTipsAndOtherCompensation")),
            box2=self._to_float(w2_fields.get("FederalIncomeTaxWithheld")),
        )
        t1098 = Form1098TParsedData(
            box1=self._to_float(t1098_fields.get("PaymentReceived")),
            box5=self._to_float(t1098_fields.get("Scholarships")),
        )
        return ParsedTaxData(w2=w2, **{"1098t": t1098})

    def build_frontend_calculations(self, box_data: dict) -> dict:
        """
        Build Daniel-frontend-compatible calculation sections.

        This keeps the frontend integration compatible while session storage
        continues using normalized parsed fields + deterministic draft logic.
        """
        parsed = self._normalize_parsed_data(box_data).model_dump(by_alias=True)
        w2 = parsed.get("w2", {})
        t1098 = parsed.get("1098t", {})

        wages = self._to_float(w2.get("box1"))
        federal_withheld = self._to_float(w2.get("box2"))
        tuition_paid = self._to_float(t1098.get("box1"))
        scholarships = self._to_float(t1098.get("box5"))

        scholarship_income_taxable = max(0.0, scholarships - tuition_paid)
        non_taxable_scholarships = scholarships - scholarship_income_taxable

        total_income = wages + scholarship_income_taxable
        standard_deduction = 14600.0
        agi = total_income
        taxable_income = max(0.0, agi - standard_deduction)
        estimated_tax_liability = self.calculation_service.calculate_single_filer_tax(
            taxable_income
        )
        potential_refund = max(0.0, federal_withheld - estimated_tax_liability)
        tax_bracket_rate = 0.10 if taxable_income <= 11600 else (0.12 if taxable_income <= 47150 else 0.22)

        return {
            "income": {
                "w2_wages": round(wages, 2),
                "scholarship_income_taxable": round(scholarship_income_taxable, 2),
                "total_income": round(total_income, 2),
                "agi": round(agi, 2),
            },
            "deductions_credits": {
                "standard_deduction": round(standard_deduction, 2),
                "non_taxable_scholarships": round(non_taxable_scholarships, 2),
                "education_credits": round(min(2500.0, tuition_paid * 0.25), 2),
            },
            "tax_and_refund": {
                "taxable_income": round(taxable_income, 2),
                "tax_bracket_rate": round(tax_bracket_rate, 4),
                "estimated_tax_liability": round(estimated_tax_liability, 2),
                "federal_tax_withheld": round(federal_withheld, 2),
                "fica_withheld": 0.0,
                "medicare_withheld": 0.0,
                "potential_refund": round(potential_refund, 2),
            },
        }

    async def parse_files_for_frontend(
        self, *, files: list[UploadFile], mock_mode: bool
    ) -> tuple[str, ParsedTaxData, str, dict, dict]:
        """Return Daniel-compatible box_data + normalized parsed_data."""
        if mock_mode:
            sample = get_sample_parsed_data()
            parsed = ParsedTaxData(
                w2=W2ParsedData(**sample.get("w2", {})),
                **{"1098t": Form1098TParsedData(**sample.get("1098t", {}))},
            )
            box_data = {
                "W2.pdf": {
                    "parsed_data": {
                        "w2": {
                            "WagesTipsAndOtherCompensation": parsed.w2.box1 if parsed.w2 else 0.0,
                            "FederalIncomeTaxWithheld": parsed.w2.box2 if parsed.w2 else 0.0,
                        }
                    }
                },
                "1098-T.pdf": {
                    "parsed_data": {
                        "1098t": {
                            "PaymentReceived": parsed.form_1098t.box1 if parsed.form_1098t else 0.0,
                            "Scholarships": parsed.form_1098t.box5 if parsed.form_1098t else 0.0,
                        }
                    }
                },
            }
            calculations = self.build_frontend_calculations(box_data)
            return SAMPLE_SESSION_ID, parsed, "mock", box_data, calculations

        if not files:
            raise ValueError("No files provided for parsing.")

        with TemporaryDirectory(prefix="taxmaxx_parser_") as temp_dir:
            temp_paths: list[Path] = []
            for upload in files:
                if not upload.filename:
                    continue
                file_path = Path(temp_dir) / upload.filename
                content = await upload.read()
                file_path.write_bytes(content)
                temp_paths.append(file_path)

            if not temp_paths:
                raise ValueError("Uploaded files are empty or invalid.")

            box_data = extract_many(temp_paths)
            parsed = self._normalize_parsed_data(box_data)
            calculations = self.build_frontend_calculations(box_data)
            return f"session_{uuid4().hex[:12]}", parsed, "parsed", box_data, calculations

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
        file_list: list[UploadFile] = [
            upload for upload in [w2_file, form_1098t_file] if upload is not None
        ]
        session_id, parsed, source, _, _ = await self.parse_files_for_frontend(
            files=file_list,
            mock_mode=mock_mode,
        )
        return session_id, parsed, source
