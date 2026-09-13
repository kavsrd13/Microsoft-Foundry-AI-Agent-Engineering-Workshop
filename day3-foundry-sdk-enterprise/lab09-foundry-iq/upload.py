"""Load independent synthetic data: https://learn.microsoft.com/azure/search/search-get-started-text"""
import json
import os
from pathlib import Path
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from dotenv import load_dotenv


def main() -> None:
    root = Path(__file__).resolve().parent
    load_dotenv()
    chunks = json.loads((root / 'chunks.json').read_text(encoding='utf-8'))
    documents = [{'id': str(i), 'content': row['content'], 'source': row['source'],
                  'allowed_groups': ['citizen-service']} for i, row in enumerate(chunks)]
    with DefaultAzureCredential() as credential, SearchClient(
        os.environ['SEARCH_ENDPOINT'], os.environ['SEARCH_INDEX_NAME'], credential
    ) as client:
        results = client.merge_or_upload_documents(documents)
        for result in results:
            print(result.key, result.succeeded)


if __name__ == '__main__':
    main()
