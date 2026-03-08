"""
example 1: W2 form data extraction
"""
import base64
from pathlib import Path
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from utility import client, is_file_or_url, load_file_as_base64

# document_dir = Path('./documents')
# w2_dir = document_dir / 'w2'
# file_path = w2_dir / 'W2_Clean_DataSet_01' / 'W2_XL_input_clean_1000.jpg'
file_path = Path('W2_XL_input_clean_1003.pdf')

if not file_path.exists():
    raise FileNotFoundError(f'File {file_path} not found')

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
print(result.keys())
print(result['content'])
