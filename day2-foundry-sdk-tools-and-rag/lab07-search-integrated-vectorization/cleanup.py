"""Delete only recorded lab resources. https://learn.microsoft.com/azure/search/search-howto-create-search-index"""
import json
import os
from pathlib import Path
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
ROOT = Path(__file__).resolve().parent
def main() -> None:
    load_dotenv(ROOT / '.env')
    path = ROOT / 'data/resource-state.json'
    if not path.exists():
        print('Nothing recorded to delete.')
        return
    saved = json.loads(path.read_text(encoding='utf-8'))
    assert saved['name'].startswith('acme-lab07-demo-'), 'Unexpected resource name'
    if input('Delete only '+saved['name']+' resources? Type yes: ') != 'yes':
        return
    try:
        from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
        from azure.storage.blob import BlobServiceClient
        client = SearchIndexerClient(os.environ['SEARCH_ENDPOINT'], DefaultAzureCredential())
        for delete, suffix in [(client.delete_indexer, '-indexer'), (client.delete_skillset, '-skills'), (client.delete_data_source_connection, '-blob')]:
            try:
                delete(saved['name']+suffix)
            except ResourceNotFoundError:
                pass
        try:
            SearchIndexClient(os.environ['SEARCH_ENDPOINT'], DefaultAzureCredential()).delete_index(saved['name'])
        except ResourceNotFoundError:
            pass
        BlobServiceClient(os.environ['STORAGE_ACCOUNT_URL'], DefaultAzureCredential()).delete_container(saved['name'])
    except ResourceNotFoundError:
        pass
    path.unlink()
    print('Recorded lab resources removed; shared services and source data retained.')
if __name__ == '__main__':
    main()
