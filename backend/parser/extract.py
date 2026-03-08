"""Azure parser integration for W-2 and 1098-T PDFs."""

from pathlib import Path

from parser.parse_fields import parse_tax_fields
from parser.utility import get_document_client, is_file_or_url, load_file_as_base64


def extract_from_file(file_path: Path) -> dict:
    """Parse one document and return extracted field payload."""
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File {file_path} not found")

    lower_name = file_path.name.lower()
    if "1098t" in lower_name or "1098-t" in lower_name:
        model_id = "prebuilt-tax.us.1098T"
        document_type = "1098t"
    elif "w2" in lower_name:
        model_id = "prebuilt-tax.us.w2"
        document_type = "w2"
    else:
        raise ValueError(
            "Unsupported filename. Name the file with W2 or 1098-T for model selection."
        )

    doc_client = get_document_client()
    source = is_file_or_url(str(file_path))
    if source == "url":
        # Lazy import for Azure request model.
        from azure.ai.documentintelligence.models import AnalyzeDocumentRequest

        poller = doc_client.begin_analyze_document(
            model_id, AnalyzeDocumentRequest(url_source=str(file_path))
        )
    elif source == "file":
        poller = doc_client.begin_analyze_document(
            model_id, {"base64Source": load_file_as_base64(file_path)}
        )
    else:
        raise ValueError(f"Unsupported document source: {file_path}")

    result = poller.result()
    if not result or not result.documents:
        raise RuntimeError("No parse result returned from Azure Document Intelligence.")

    document_fields = result.documents[0]["fields"]
    return parse_tax_fields(document_fields, document_type)


def extract_many(file_paths: list[Path]) -> dict:
    """Parse multiple files and return dict keyed by filename."""
    results: dict = {}
    for path in file_paths:
        parsed = extract_from_file(path)
        results[path.name] = parsed
    return results
