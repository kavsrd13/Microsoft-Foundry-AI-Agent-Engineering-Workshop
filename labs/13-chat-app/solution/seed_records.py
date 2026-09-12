"""Lab 13, setup - create a small index where different users see different things.

Run this once:  python seed_records.py
"""

import os
from uuid import UUID

from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchableField, SearchIndex, SimpleField,
)
from dotenv import load_dotenv

load_dotenv()

INDEX_NAME = os.environ["SEARCH_INDEX"]

# Real object IDs of two test users in your tenant. Not app IDs.
USER_A = str(UUID(os.environ["TEST_USER_A_OBJECT_ID"]))
USER_B = str(UUID(os.environ["TEST_USER_B_OBJECT_ID"]))

if USER_A == USER_B:
    raise ValueError("Use two different test users, or the lab proves nothing")
if not INDEX_NAME.startswith("lab13-"):
    raise ValueError("SEARCH_INDEX must start with 'lab13-'")

fields = [
    SimpleField(name="id", type="Edm.String", key=True),
    SearchableField(name="content", type="Edm.String"),
    SimpleField(name="is_public", type="Edm.Boolean", filterable=True),
    SimpleField(name="allowed_user_ids", type="Collection(Edm.String)", filterable=True),
    SimpleField(name="allowed_group_ids", type="Collection(Edm.String)", filterable=True),
]

records = [
    {"id": "public-notice", "is_public": True,
     "content": "The service desk is open from 9 am to 5 pm on weekdays.",
     "allowed_user_ids": [], "allowed_group_ids": []},
    {"id": "case-for-user-a", "is_public": False,
     "content": "Synthetic case A: the property inspection is on Monday.",
     "allowed_user_ids": [USER_A], "allowed_group_ids": []},
    {"id": "case-for-user-b", "is_public": False,
     "content": "Synthetic case B: the property inspection is on Thursday.",
     "allowed_user_ids": [USER_B], "allowed_group_ids": []},
]

credential = DefaultAzureCredential()

SearchIndexClient(os.environ["SEARCH_ENDPOINT"], credential).create_or_update_index(
    SearchIndex(name=INDEX_NAME, fields=fields)
)

with SearchClient(os.environ["SEARCH_ENDPOINT"], INDEX_NAME, credential) as search:
    search.upload_documents(records)

print(f"Created {INDEX_NAME} with one public record and one for each test user.")
print("Now sign in as each user and ask about the inspection date.")
