"""Offline checks default; explicit live read checks. https://learn.microsoft.com/azure/search/search-document-level-access-overview"""
import argparse
import ast
import json
import os
from pathlib import Path
ROOT = Path(__file__).resolve().parent
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--live', action='store_true')
    args = parser.parse_args()
    try:
        for source in (ROOT / 'src').glob('*.py'):
            ast.parse(source.read_text(encoding='utf-8'))
        docs = json.loads((ROOT / 'data/chunks.json').read_text(encoding='utf-8'))
        assert docs and all({'id','content','source','page','allowed_groups'} <= d.keys() for d in docs)
        print('PASS OFFLINE: page metadata and permission strings present')
        if args.live:
            from dotenv import load_dotenv
            from azure.identity import DefaultAzureCredential
            load_dotenv(ROOT / '.env')
            from azure.search.documents.indexes import SearchIndexerClient
            from azure.search.documents import SearchClient
            name = json.loads((ROOT / 'data/resource-state.json').read_text(encoding='utf-8'))['name']
            result = SearchIndexerClient(os.environ['SEARCH_ENDPOINT'], DefaultAzureCredential()).get_indexer_status(name+'-indexer').last_result
            assert result and result.status == 'success' and not result.errors and result.failed_item_count == 0, str(result)
            assert SearchClient(os.environ['SEARCH_ENDPOINT'], name, DefaultAzureCredential()).get_document_count() > 0
            print('PASS LIVE: indexer succeeded and index contains documents')
        else:
            print('PASS OFFLINE: Python syntax valid. Azure execution NOT tested.')
    except Exception as error:
        print('FAIL', type(error).__name__, str(error))
        raise SystemExit(1)
if __name__ == '__main__':
    main()
