import base64
from pathlib import Path
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from utility import client, is_file_or_url, load_file_as_base64
from parse_fields import parse_tax_fields

file_path = Path('w2-filled.pdf')

if not file_path.exists():
    raise FileNotFoundError(f'File {file_path} not found')

# determine if model should be 1098 or w2 based on the document type
if '1098t' in str(file_path):
    model_id = "prebuilt-tax.us.1098T"
    document_type = "1098t"
    print("Model set to 1098-T")
else:
    model_id = "prebuilt-tax.us.w2"
    document_type = "w2"
    print("Model set to w2")

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
# print("content:", result['content'])
# print("Documents", result['documents'])
# print(result['documents'][0].keys())
if result:
    print("Retrieval successful!")
document_fields = result.documents[0]['fields']
# print("Document fields:", document_fields.keys())

# https://github.com/Azure-Samples/document-intelligence-code-samples/blob/main/schema/2024-11-30-ga/us-tax/w2.md
# https://github.com/Azure-Samples/document-intelligence-code-samples/blob/main/schema/2024-11-30-ga/us-tax/1098/1098-t.md

if model_id:
    box_data = parse_tax_fields(document_fields, document_type)
else:
   print("Unsupported model")

print(box_data)