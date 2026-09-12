"""Deletes only the explicitly named lab18 index; leaves shared Azure services."""
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))
from clients import ROOT, name, credential
from azure.search.documents.indexes import SearchIndexClient

SearchIndexClient(os.environ['SEARCH_ENDPOINT'], credential).delete_index(name)
(ROOT / 'data' / f'{name}-manifest.json').unlink(missing_ok=True)
print('Deleted index', name)
