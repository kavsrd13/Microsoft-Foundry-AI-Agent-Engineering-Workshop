"""Only shared client setup; all indexing/retrieval remains visible in each script."""
import os
from pathlib import Path
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents import SearchClient
from openai import OpenAI

ROOT = Path(__file__).resolve().parent
load_dotenv()
credential = DefaultAzureCredential()
name = os.environ['SEARCH_INDEX']
if not name.startswith('lab18-'):
    raise ValueError('Use a dedicated lab18- index')
search = SearchClient(os.environ['SEARCH_ENDPOINT'], name, credential)
model = OpenAI(base_url=os.environ['AZURE_OPENAI_ENDPOINT'].rstrip('/') + '/openai/v1/',
    api_key=get_bearer_token_provider(credential, 'https://cognitiveservices.azure.com/.default'))


def embedding(text):
    return model.embeddings.create(model=os.environ['EMBEDDING_DEPLOYMENT'],
        input=text, dimensions=1536).data[0].embedding
