from pathlib import Path
import ast
import os
import subprocess
import sys
from typing import List, Dict, Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from pymongo import MongoClient
from bson import ObjectId


router = APIRouter(prefix="/api/parser", tags=["parser"])

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "hackai_tax_assistant")
MONGODB_COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_BOXDATA", "box_data")

_mongo_client = MongoClient(MONGODB_URI)
_boxdata_collection = _mongo_client[MONGODB_DB_NAME][MONGODB_COLLECTION_NAME]


def _run_extract_script(file_paths: List[Path]) -> str:
    """
    Execute backend/parser/extract.py as a subprocess and return its stdout.

    This keeps the FastAPI layer thin and delegates all parsing logic to the
    existing extract.py script, as requested.
    """
    backend_root = Path(__file__).resolve().parents[2]
    parser_dir = backend_root / "parser"
    script_path = parser_dir / "extract.py"

    if not script_path.exists():
        raise HTTPException(status_code=500, detail="Parser script not found.")

    args = [sys.executable, str(script_path), *[str(p) for p in file_paths]]

    try:
        completed = subprocess.run(
            args,
            cwd=str(parser_dir),
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Parser script timed out.")
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr or exc.stdout or "Parser script failed."
        raise HTTPException(status_code=500, detail=detail.strip())

    return completed.stdout


def _to_float(value: Any) -> float:
    """Best-effort conversion of a parsed field value to float."""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).replace(",", "").strip().replace("$", "")
    try:
        return float(text)
    except ValueError:
        return 0.0


def _compute_calculations(box_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute high-level tax summary figures used by the frontend RESULTS_SECTIONS.

    box_data is expected to be a dictionary keyed by filename, where each value
    looks like: {"parsed_data": {"w2" or "1098t": {<field>: <value>, ...}}}
    """
    w2_fields: Dict[str, Any] = {}
    t1098_fields: Dict[str, Any] = {}

    for _filename, doc in box_data.items():
        parsed = doc.get("parsed_data", {})
        if "w2" in parsed:
            w2_fields = parsed["w2"]
        if "1098t" in parsed:
            t1098_fields = parsed["1098t"]

    # W-2 derived values
    wages = _to_float(w2_fields.get("WagesTipsAndOtherCompensation"))
    federal_withheld = _to_float(w2_fields.get("FederalIncomeTaxWithheld"))
    ss_withheld = _to_float(w2_fields.get("SocialSecurityTaxWithheld"))
    medicare_withheld = _to_float(w2_fields.get("MedicareTaxWithheld"))

    # 1098-T derived values
    tuition_paid = _to_float(t1098_fields.get("PaymentReceived"))
    scholarships = _to_float(t1098_fields.get("Scholarships"))

    # Simple illustrative rules for demo purposes.
    scholarship_income_taxable = max(0.0, scholarships - tuition_paid)
    non_taxable_scholarships = scholarships - scholarship_income_taxable

    total_income = wages + scholarship_income_taxable

    # Standard deduction for a single filer (demo value, hard-coded here).
    standard_deduction = 14600.0
    agi = total_income  # no above-the-line adjustments modeled yet
    taxable_income = max(0.0, agi - standard_deduction)

    # Very rough single-bracket approximation for demo.
    if taxable_income <= 11600:
        tax_rate = 0.10
    elif taxable_income <= 47150:
        tax_rate = 0.12
    else:
        tax_rate = 0.22

    estimated_tax_liability = taxable_income * tax_rate
    potential_refund = max(0.0, federal_withheld - estimated_tax_liability)

    return {
        "income": {
            "w2_wages": wages,
            "scholarship_income_taxable": scholarship_income_taxable,
            "total_income": total_income,
            "agi": agi,
        },
        "deductions_credits": {
            "standard_deduction": standard_deduction,
            "non_taxable_scholarships": non_taxable_scholarships,
            # Simple placeholder for AOTC-like education credit:
            "education_credits": min(2500.0, tuition_paid * 0.25),
        },
        "tax_and_refund": {
            "taxable_income": taxable_income,
            "tax_bracket_rate": tax_rate,
            "estimated_tax_liability": estimated_tax_liability,
            "federal_tax_withheld": federal_withheld,
            "fica_withheld": ss_withheld,
            "medicare_withheld": medicare_withheld,
            "potential_refund": potential_refund,
        },
    }


@router.post("/box-data")
async def get_box_data(files: List[UploadFile] = File(...)):
    """
    Run the existing backend/parser/extract.py script and return summary
    calculations suitable for populating the frontend RESULTS_SECTIONS.
    """
    backend_root = Path(__file__).resolve().parents[2]
    parser_dir = backend_root / "parser"

    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    saved_paths: List[Path] = []
    for upload in files:
        dest = parser_dir / upload.filename
        try:
            content = await upload.read()
            dest.write_bytes(content)
            saved_paths.append(dest)
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save uploaded file {upload.filename}: {exc}",
            )

    stdout = _run_extract_script(saved_paths)
    lines = [line for line in stdout.splitlines() if line.strip()]

    if not lines:
        raise HTTPException(status_code=500, detail="Parser produced no output.")

    last_line = lines[-1]

    try:
        box_data = ast.literal_eval(last_line)
    except Exception:
        # Fallback: return the raw stdout so the caller can inspect it.
        return {"raw_output": stdout}

    calculations = _compute_calculations(box_data)

    return {
        "calculations": calculations,
        "box_data": box_data,
    }


@router.post("/box-data/store")
async def store_box_data(payload: Dict[str, Any]):
    """
    Store the original box_data (and optional results_sections) in MongoDB.

    Expected payload shape:
    {
      "box_data": { ... },
      "results_sections": [ { "title": "...", "items": [ { "label", "value", "line", ... } ] } ]  # optional
    }
    """
    if "box_data" not in payload:
        raise HTTPException(status_code=400, detail="Missing 'box_data' in request body.")

    doc = {"box_data": payload["box_data"]}
    if "results_sections" in payload:
        doc["results_sections"] = payload["results_sections"]
    result = _boxdata_collection.insert_one(doc)

    return {"id": str(result.inserted_id)}


@router.put("/box-data/{doc_id}")
async def update_box_data(doc_id: str, payload: Dict[str, Any]):
    """
    Update a stored document with new results_sections (e.g. after user edits in the UI).

    Expected payload shape:
    {
      "results_sections": [ { "title": "...", "items": [ { "label", "value", "line", ... } ] }
    }
    """
    if "results_sections" not in payload:
        raise HTTPException(status_code=400, detail="Missing 'results_sections' in request body.")

    try:
        oid = ObjectId(doc_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid document id.")

    result = _boxdata_collection.update_one(
        {"_id": oid},
        {"$set": {"results_sections": payload["results_sections"]}},
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Document not found.")

    return {"status": "updated", "id": doc_id}


@router.delete("/box-data/{doc_id}")
async def delete_box_data(doc_id: str):
    """
    Delete a previously stored box_data document by its MongoDB ObjectId.
    """
    try:
        oid = ObjectId(doc_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid document id.")

    result = _boxdata_collection.delete_one({"_id": oid})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document not found.")

    return {"status": "deleted", "id": doc_id}

