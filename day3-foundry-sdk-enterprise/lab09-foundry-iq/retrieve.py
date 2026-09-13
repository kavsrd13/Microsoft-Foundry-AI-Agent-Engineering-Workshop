"""Retrieve existing knowledge: https://learn.microsoft.com/azure/search/agentic-retrieval-how-to-retrieve"""
import argparse
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--preview', action='store_true', help='Enable preview planning and synthesis')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    load_dotenv()
    question = 'What leave and travel rules apply to an Acme employee?'
    version = '2026-08-01-preview' if args.preview else '2026-04-01'
    body = {'intents': [{'type': 'semantic', 'search': question}]}
    if args.preview:
        body = {'messages': [{'role': 'user', 'content': [{'type': 'text', 'text': question}]}]}
    credential = DefaultAzureCredential()
    token = credential.get_token('https://search.azure.com/.default').token
    url = f"{os.environ['SEARCH_ENDPOINT'].rstrip('/')}/knowledgebases/{os.environ['KNOWLEDGE_BASE_NAME']}/retrieve?api-version={version}"
    request = Request(url, data=json.dumps(body).encode(), headers={
        'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'})
    with urlopen(request, timeout=60) as response:
        result = json.load(response)
    print(json.dumps(result, indent=2))
    (root / 'live-retrieval.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    credential.close()


if __name__ == '__main__':
    main()
