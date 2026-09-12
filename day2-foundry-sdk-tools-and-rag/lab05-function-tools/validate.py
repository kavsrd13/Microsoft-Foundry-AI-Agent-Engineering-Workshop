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
        orders = json.loads((ROOT / 'data/orders.json').read_text(encoding='utf-8'))
        assert len(orders) == 25
        print('PASS OFFLINE: 25 synthetic orders loaded')
        if args.live:
            from dotenv import load_dotenv
            from azure.identity import DefaultAzureCredential
            load_dotenv(ROOT / '.env')
            from azure.ai.projects import AIProjectClient
            saved = json.loads((ROOT / 'data/resource-state.json').read_text(encoding='utf-8'))
            agent = AIProjectClient(os.environ['PROJECT_ENDPOINT'], DefaultAzureCredential()).agents.get_version(saved['name'], saved['version'])
            assert agent.definition.tools
            print('PASS LIVE: saved agent version exists with tools; execute demo to prove the tool loop')
        else:
            print('PASS OFFLINE: Python syntax valid. Azure execution NOT tested.')
    except Exception as error:
        print('FAIL', type(error).__name__, str(error))
        raise SystemExit(1)
if __name__ == '__main__':
    main()
