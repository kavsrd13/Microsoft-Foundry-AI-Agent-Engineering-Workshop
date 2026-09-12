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
        assert list((ROOT / 'data/benefits').glob('*.pdf'))
        print('PASS OFFLINE: independent PDF inputs present')
        if args.live:
            from dotenv import load_dotenv
            from azure.identity import DefaultAzureCredential
            load_dotenv(ROOT / '.env')
            assert list((ROOT / 'data').glob('*.md'))
            chunks = json.loads((ROOT / 'data/chunks.json').read_text(encoding='utf-8'))
            assert chunks and all(c['page'] >= 1 and c['content'] for c in chunks)
            print('PASS OUTPUT CHECK: saved extraction outputs exist; this is not a fresh cloud call')
        else:
            print('PASS OFFLINE: Python syntax valid. Azure execution NOT tested.')
    except Exception as error:
        print('FAIL', type(error).__name__, str(error))
        raise SystemExit(1)
if __name__ == '__main__':
    main()
