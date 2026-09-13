from dotenv import load_dotenv
load_dotenv()

"""Create a dedicated index; vectors are numerical arrays, metadata enables filters."""
import os
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchableField, SearchField, VectorSearch,
    HnswAlgorithmConfiguration, VectorSearchProfile, SemanticSearch,
    SemanticConfiguration, SemanticPrioritizedFields, SemanticField)
from clients import credential, name

client = SearchIndexClient(os.environ['SEARCH_ENDPOINT'], credential)
index = SearchIndex(name=name, fields=[
    SimpleField(name='id', type='Edm.String', key=True),
    SimpleField(name='source', type='Edm.String', filterable=True),
    SimpleField(name='page', type='Edm.Int32'),
    SearchableField(name='content', type='Edm.String'),
    SimpleField(name='allowed_groups', type='Collection(Edm.String)', filterable=True),
    SearchField(name='vector', type='Collection(Edm.Single)', searchable=True,
        vector_search_dimensions=1536, vector_search_profile_name='vectors')],
    vector_search=VectorSearch(algorithms=[HnswAlgorithmConfiguration(name='hnsw')],
        profiles=[VectorSearchProfile(name='vectors', algorithm_configuration_name='hnsw')]),
    semantic_search=SemanticSearch(configurations=[SemanticConfiguration(name='semantic',
        prioritized_fields=SemanticPrioritizedFields(content_fields=[SemanticField(field_name='content')]))]))
client.create_or_update_index(index)
print(name, 'ready; next run sync.py')
