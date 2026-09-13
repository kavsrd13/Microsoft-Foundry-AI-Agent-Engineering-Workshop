"""Integrated vectorisation. https://learn.microsoft.com/azure/search/vector-search-integrated-vectorization"""
import json
import os
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndex, SearchField, SimpleField, SearchableField, SearchFieldDataType,
    VectorSearch, HnswAlgorithmConfiguration, VectorSearchProfile,
    AzureOpenAIVectorizer, AzureOpenAIVectorizerParameters, SemanticSearch,
    SemanticConfiguration, SemanticPrioritizedFields, SemanticField,
    SearchIndexerDataSourceConnection, SearchIndexerDataContainer, SplitSkill,
    AzureOpenAIEmbeddingSkill, InputFieldMappingEntry, OutputFieldMappingEntry,
    SearchIndexerIndexProjection, SearchIndexerIndexProjectionSelector,
    SearchIndexerIndexProjectionsParameters, SearchIndexerSkillset, SearchIndexer,
    IndexingParameters, IndexingParametersConfiguration)
from dotenv import load_dotenv
from state import ROOT, state

def main() -> None:
    load_dotenv()
    name = state()['name']
    credential = DefaultAzureCredential()
    blobs = BlobServiceClient(os.environ['STORAGE_ACCOUNT_URL'], credential)
    container = blobs.get_container_client(name)
    if not container.exists():
        container.create_container()
    # Each JSON blob is one source page. This retains actual PDF page numbers
    # when the indexer splits its text; SplitSkill 'pages' means text chunks.
    for chunk in json.loads((ROOT / 'chunks.json').read_text(encoding='utf-8')):
        container.upload_blob(chunk['id'] + '.json', json.dumps(chunk), overwrite=True)
    indexes = SearchIndexClient(os.environ['SEARCH_ENDPOINT'], credential)
    indexers = SearchIndexerClient(os.environ['SEARCH_ENDPOINT'], credential)
    embedding = dict(resource_url=os.environ['AZURE_OPENAI_ENDPOINT'],
        deployment_name=os.environ['EMBEDDING_DEPLOYMENT'], model_name='text-embedding-3-small')
    fields = [SimpleField(name='id', type='Edm.String', key=True),
        SimpleField(name='parent_id', type='Edm.String', filterable=True),
        SearchableField(name='content', type='Edm.String'),
        SimpleField(name='source', type='Edm.String'), SimpleField(name='page', type='Edm.Int32'),
        SimpleField(name='allowed_groups', type='Collection(Edm.String)', filterable=True),
        SearchField(name='content_vector', type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True, vector_search_dimensions=1536, vector_search_profile_name='vectors')]
    indexes.create_or_update_index(SearchIndex(name=name, fields=fields,
        vector_search=VectorSearch(algorithms=[HnswAlgorithmConfiguration(name='hnsw')],
            profiles=[VectorSearchProfile(name='vectors', algorithm_configuration_name='hnsw', vectorizer_name='openai')],
            vectorizers=[AzureOpenAIVectorizer(vectorizer_name='openai', parameters=AzureOpenAIVectorizerParameters(**embedding))]),
        semantic_search=SemanticSearch(configurations=[SemanticConfiguration(name='semantic',
            prioritized_fields=SemanticPrioritizedFields(content_fields=[SemanticField(field_name='content')]))])))
    indexers.create_or_update_data_source_connection(SearchIndexerDataSourceConnection(name=name+'-blob', type='azureblob',
        connection_string='ResourceId='+os.environ['STORAGE_RESOURCE_ID']+';', container=SearchIndexerDataContainer(name=name)))
    split = SplitSkill(context='/document', text_split_mode='pages', maximum_page_length=1000, page_overlap_length=100,
        inputs=[InputFieldMappingEntry(name='text', source='/document/content')],
        outputs=[OutputFieldMappingEntry(name='textItems', target_name='chunks')])
    embed = AzureOpenAIEmbeddingSkill(context='/document/chunks/*', dimensions=1536, **embedding,
        inputs=[InputFieldMappingEntry(name='text', source='/document/chunks/*')],
        outputs=[OutputFieldMappingEntry(name='embedding', target_name='vector')])
    projection = SearchIndexerIndexProjection(selectors=[SearchIndexerIndexProjectionSelector(
        target_index_name=name, parent_key_field_name='parent_id', source_context='/document/chunks/*', mappings=[
            InputFieldMappingEntry(name='content', source='/document/chunks/*'),
            InputFieldMappingEntry(name='content_vector', source='/document/chunks/*/vector'),
            InputFieldMappingEntry(name='source', source='/document/source'),
            InputFieldMappingEntry(name='page', source='/document/page'),
            InputFieldMappingEntry(name='allowed_groups', source='/document/allowed_groups')])],
        parameters=SearchIndexerIndexProjectionsParameters(projection_mode='skipIndexingParentDocuments'))
    indexers.create_or_update_skillset(SearchIndexerSkillset(name=name+'-skills', skills=[split, embed], index_projection=projection))
    indexers.create_or_update_indexer(SearchIndexer(name=name+'-indexer', data_source_name=name+'-blob',
        target_index_name=name, skillset_name=name+'-skills', parameters=IndexingParameters(
            configuration=IndexingParametersConfiguration(parsing_mode='json'))))
    print(name, 'configured. Indexer runs on creation; inspect execution status using python the demo command.')
    print('For later changed input, run: python query.py --run-indexer')

if __name__ == '__main__':
    main()
