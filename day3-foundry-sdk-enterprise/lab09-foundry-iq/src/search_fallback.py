"""GA Search fallback: https://learn.microsoft.com/azure/search/search-get-started-text"""
import os
from pathlib import Path
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from dotenv import load_dotenv


def main() -> None:
    load_dotenv(Path(__file__).resolve().parents[1] / '.env')
    with DefaultAzureCredential() as credential, SearchClient(
        os.environ['SEARCH_ENDPOINT'], os.environ['SEARCH_INDEX_NAME'], credential
    ) as client:
        results = client.search('leave travel', top=3,
            filter="allowed_groups/any(g: search.in(g, 'citizen-service'))")
        for result in results:
            print(result['source'], result['content'])


if __name__ == '__main__':
    main()
