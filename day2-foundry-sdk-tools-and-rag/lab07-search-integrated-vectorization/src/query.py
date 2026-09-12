"""Hybrid semantic search. https://learn.microsoft.com/azure/search/vector-search-integrated-vectorization"""
import argparse
import os
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.models import VectorizableTextQuery
from dotenv import load_dotenv
from state import ROOT, state
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-indexer', action='store_true')
    args = parser.parse_args()
    load_dotenv(ROOT / '.env')
    name = state()['name']
    credential = DefaultAzureCredential()
    if args.run_indexer:
        SearchIndexerClient(os.environ['SEARCH_ENDPOINT'], credential).run_indexer(name+'-indexer')
        print('Indexer requested. Wait for validate.py --live to pass before querying.')
        return
    client = SearchClient(os.environ['SEARCH_ENDPOINT'], name, credential)
    question = 'What leave and travel entitlements apply?'
    results = client.search(search_text=question, vector_queries=[VectorizableTextQuery(
        text=question, fields='content_vector', k_nearest_neighbors=50)], query_type='semantic',
        semantic_configuration_name='semantic', select=['content', 'source', 'page', 'allowed_groups'], top=3)
    for result in results:
        print(result)
if __name__ == '__main__':
    main()
