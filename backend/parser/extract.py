"""Extract data from tax documents and return a dictionary of the parsed fields.

This module can be:
- imported and used via the ``extract_from_file`` function, or
- executed as a script with one or more file paths:

    python extract.py W2.pdf 1098-T.pdf

When run as a script, the final line of stdout is a string representation of
the resulting dictionary so that the FastAPI layer can capture and return it.
"""

import argparse
from pathlib import Path

from azure.ai.documentintelligence.models import AnalyzeDocumentRequest

from parse_fields import parse_tax_fields
from utility import client, is_file_or_url, load_file_as_base64


def extract_from_file(file_path: Path) -> dict:
    """Run Azure Document Intelligence on a single tax document and return box_data."""
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File {file_path} not found")

    # Determine if model should be 1098-T or W-2 based on the document name.
    lower_name = file_path.name.lower()
    if "1098t" in lower_name or "1098-t" in lower_name:
        model_id = "prebuilt-tax.us.1098T"
        document_type = "1098t"
        print("Model set to 1098-T")
    else:
        model_id = "prebuilt-tax.us.w2"
        document_type = "w2"
        print("Model set to W-2")

    document_ai_client = client()

    # doc_source = '<doc url>'
    doc_source = file_path

    if is_file_or_url(str(doc_source)) == "url":
        print("Doc is a url")
        poller = document_ai_client.begin_analyze_document(
            model_id, AnalyzeDocumentRequest(url_source=doc_source)
        )
    elif is_file_or_url(str(doc_source)) == "file":
        print("Doc is a file")
        poller = document_ai_client.begin_analyze_document(
            model_id, {"base64Source": load_file_as_base64(doc_source)}
        )
    else:
        raise ValueError(f"Unsupported document source: {doc_source}")

    result = poller.result()

    # dict_keys(['apiVersion', 'modelId', 'stringIndexType', 'content', 'pages', 'styles', 'documents', 'contentFormat'])
    # print(result.keys())
    # print("content:", result['content'])
    # print("Documents", result['documents'])
    # print(result['documents'][0].keys())
    if result:
        print("Retrieval successful!")
    else:
        raise RuntimeError("No result returned from Document Intelligence")

    document_fields = result.documents[0]["fields"]
    # print("Document fields:", document_fields.keys())

    # https://github.com/Azure-Samples/document-intelligence-code-samples/blob/main/schema/2024-11-30-ga/us-tax/w2.md
    # https://github.com/Azure-Samples/document-intelligence-code-samples/blob/main/schema/2024-11-30-ga/us-tax/1098/1098-t.md

    box_data = parse_tax_fields(document_fields, document_type)
    return box_data


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract tax box data from one or more document files."
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="Path(s) to tax document PDF files (e.g., W2.pdf 1098-T.pdf).",
    )
    args = parser.parse_args()

    results = {}
    for file_arg in args.files:
        path = Path(file_arg)
        data = extract_from_file(path)
        # Key results by filename for clarity when multiple docs are processed.
        results[path.name] = data

    # Print a representation of the results dict; FastAPI layer parses this.
    # For a single file this will just be {'W2.pdf': {...}}.
    print(results)


if __name__ == "__main__":
    main()
