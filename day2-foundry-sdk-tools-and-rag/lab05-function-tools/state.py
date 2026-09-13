from dotenv import load_dotenv
load_dotenv()

"""Persist only this lab's resource names. https://learn.microsoft.com/azure/search/search-howto-create-search-index"""
import json
from pathlib import Path
from uuid import uuid4
ROOT = Path(__file__).resolve().parent
STATE = ROOT / 'resource-state.json'
def state() -> dict:
    if not STATE.exists():
        STATE.write_text(json.dumps({'name': 'acme-lab05-demo-' + uuid4().hex[:10]}))
    return json.loads(STATE.read_text(encoding='utf-8'))
def main() -> None:
    print(state())
if __name__ == '__main__':
    main()
