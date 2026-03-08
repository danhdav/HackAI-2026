"""Shared helpers for parser integrations."""

import base64
import os
from pathlib import Path
from urllib.parse import urlparse

from app.config import settings


def get_document_client():
    """Build Azure Document Intelligence client lazily."""
    # Lazy imports keep mock mode usable without Azure dependency installed.
    from azure.ai.documentintelligence import DocumentIntelligenceClient
    from azure.core.credentials import AzureKeyCredential

    api_key = settings.azure_key or os.getenv("AZURE_KEY", "")
    endpoint = settings.azure_endpoint or os.getenv("AZURE_ENDPOINT", "")
    if not api_key or not endpoint:
        raise ValueError("AZURE_KEY and AZURE_ENDPOINT must be configured for live parsing.")
    return DocumentIntelligenceClient(
        endpoint=endpoint, credential=AzureKeyCredential(str(api_key))
    )


def is_file_or_url(path: str) -> str:
    """Classify source path as file/url/unknown."""
    if Path(path).exists():
        return "file"
    if urlparse(path).scheme in ("http", "https"):
        return "url"
    return "unknown"


def load_file_as_base64(file_path: Path) -> str:
    """Read file bytes and encode as base64 utf-8 string."""
    with open(file_path, "rb") as file:
        data = file.read()
    return base64.b64encode(data).decode("utf-8")
