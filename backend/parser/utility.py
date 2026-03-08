import os

from dotenv import load_dotenv
import configparser
import base64
from urllib.parse import urlparse
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient

load_dotenv()

def client():
    api_key = os.getenv('AZURE_KEY')
    endpoint = os.getenv('AZURE_ENDPOINT')
    return DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(str(api_key)))

def is_file_or_url(path):
    if os.path.isfile(path):
        return 'file'
    elif urlparse(path).scheme in ('http', 'https'):
        return 'url'
    else:
        return 'unknown'

def load_file_as_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    
    base64_bytes = base64.b64encode(data)
    base64_string = base64_bytes.decode('utf-8')
    return base64_string