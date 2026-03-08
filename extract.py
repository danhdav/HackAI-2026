"""
example 1: W2 form data extraction
"""
import base64
from pathlib import Path
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from utility import client, is_file_or_url, load_file_as_base64
from parse_w2 import parse_w2_fields

file_path = Path('w2-filled.pdf')

if not file_path.exists():
    raise FileNotFoundError(f'File {file_path} not found')

# determine if model should be 1098 or w2 based on the document type
if '1098' in str(file_path):
    model_id = "prebuilt-tax.us.1098"
else:
    model_id = "prebuilt-tax.us.w2"

document_ai_client = client()

# doc_source = '<doc url>'
doc_source = file_path

if is_file_or_url(str(doc_source)) == 'url':
    print('Doc is a url')
    poller = document_ai_client.begin_analyze_document(
        model_id, AnalyzeDocumentRequest(url_source=doc_source)
    )
elif is_file_or_url(str(doc_source)) == 'file':
    print('Doc is a file')
    poller = document_ai_client.begin_analyze_document(
        model_id, {"base64Source": load_file_as_base64(doc_source)}
    )

result = poller.result()

# dict_keys(['apiVersion', 'modelId', 'stringIndexType', 'content', 'pages', 'styles', 'documents', 'contentFormat'])
# print(result.keys())
# print(result['content'])
if result:
    print("Retrieval successful!")
document_fields = result.documents[0]['fields']

# https://github.com/Azure-Samples/document-intelligence-code-samples/blob/main/schema/2024-11-30-ga/us-tax/w2.md

if model_id == "prebuilt-tax.us.w2":
    parse_w2_fields(document_fields)
# else:
    # print_1098_fields(document_fields)