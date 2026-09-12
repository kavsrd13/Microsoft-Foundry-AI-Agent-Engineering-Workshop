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
        citizen = {d['id'] for d in docs if 'citizen-service' in d['allowed_groups']}
        hr = {d['id'] for d in docs if 'hr-internal' in d['allowed_groups']}
        assert citizen and hr and hr - citizen
        print('PASS OFFLINE: synthetic permissions produce distinct identity sets; negative control has restricted data')
        if args.live:
            from dotenv import load_dotenv
            from azure.identity import DefaultAzureCredential
            load_dotenv(ROOT / '.env')
            from azure.search.documents import SearchClient
            name = json.loads((ROOT / 'data/resource-state.json').read_text(encoding='utf-8'))['name']
            client = SearchClient(os.environ['SEARCH_ENDPOINT'], name, DefaultAzureCredential())
            results = list(client.search('*', filter="allowed_groups/any(g: search.in(g, 'citizen-service'))", top=1000))
            assert results and all('citizen-service' in d['allowed_groups'] for d in results)
            hr_results = list(client.search('*', filter="allowed_groups/any(g: search.in(g, 'hr-internal'))", top=1000))
            assert hr_results and all('hr-internal' in d['allowed_groups'] for d in hr_results)
            assert {d['id'] for d in hr_results} - {d['id'] for d in results}
            all_docs = list(client.search('*', top=1000))
            assert any('citizen-service' not in d['allowed_groups'] for d in all_docs)
            print('PASS LIVE: citizen filter holds; omitted filter reveals restricted synthetic documents')
        else:
            print('PASS OFFLINE: Python syntax valid. Azure execution NOT tested.')
    except Exception as error:
        print('FAIL', type(error).__name__, str(error))
        raise SystemExit(1)
if __name__ == '__main__':
    main()
