"""Create a fresh, dedicated ACL index with three synthetic records."""
import os
from pathlib import Path
from uuid import UUID

from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex, SimpleField, SearchableField, SearchFieldDataType
from dotenv import load_dotenv

load_dotenv()
name = os.environ['SEARCH_INDEX_NAME']
if not name.startswith('lab21-'):
    raise ValueError('Use a new lab21- index; do not replace a shared index')
user_a = str(UUID(os.environ['TEST_USER_A_OBJECT_ID']))
user_b = str(UUID(os.environ['TEST_USER_B_OBJECT_ID']))
if user_a == user_b or user_a == str(UUID(int=0)) or user_b == str(UUID(int=0)):
    raise ValueError('Supply two different real test-user object IDs')
fields = [
    SimpleField(name='id', type=SearchFieldDataType.String, key=True),
    SearchableField(name='content', type=SearchFieldDataType.String),
    SimpleField(name='is_public', type=SearchFieldDataType.Boolean, filterable=True),
    SimpleField(name='allowed_user_ids', type=SearchFieldDataType.Collection(SearchFieldDataType.String), filterable=True),
    SimpleField(name='allowed_group_ids', type=SearchFieldDataType.Collection(SearchFieldDataType.String), filterable=True),
]
documents = [
    {'id': 'public', 'content': 'The public service desk opens at 9 am.', 'is_public': True, 'allowed_user_ids': [], 'allowed_group_ids': []},
    {'id': 'record-a', 'content': 'Synthetic case A: the inspection is on Monday.', 'is_public': False, 'allowed_user_ids': [user_a], 'allowed_group_ids': []},
    {'id': 'record-b', 'content': 'Synthetic case B: the inspection is on Thursday.', 'is_public': False, 'allowed_user_ids': [user_b], 'allowed_group_ids': []},
]
with DefaultAzureCredential() as credential:
    with SearchIndexClient(os.environ['SEARCH_ENDPOINT'], credential) as indexes:
        indexes.create_index(SearchIndex(name=name, fields=fields))
    with SearchClient(os.environ['SEARCH_ENDPOINT'], name, credential) as search:
        results = search.upload_documents(documents)
        if not all(result.succeeded for result in results):
            raise RuntimeError('Upload incomplete; inspect index before continuing')
print('Created', name, 'with public and two private synthetic records')
