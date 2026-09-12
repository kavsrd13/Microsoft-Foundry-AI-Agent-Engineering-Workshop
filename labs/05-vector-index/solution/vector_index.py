"""Lab 05 - Build a vector index and search it four ways.

Takes the chunks from Lab 04, turns each one into a vector, puts them in
Azure AI Search, then runs the same question through four different kinds
of search so you can see what each one is good at.

Run it with:  python vector_index.py
"""

import json
import os

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchableField,
    SearchField,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)
from azure.search.documents.models import VectorizedQuery
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

INDEX_NAME = os.environ["SEARCH_INDEX"]
VECTOR_SIZE = 1536          # must match the embedding model you use
QUESTION = "How many days of annual leave do full-time staff get?"


# --- Task 2 -----------------------------------------------------------------
def create_the_index(index_client):
    """Describe the shape of the index: what we store and how we search it."""
    print("\n=== Creating the index ===")

    fields = [
        SimpleField(name="id", type="Edm.String", key=True),
        SearchableField(name="content", type="Edm.String"),      # searchable text
        SimpleField(name="source", type="Edm.String", filterable=True),
        SimpleField(name="page", type="Edm.Int32"),
        SimpleField(name="allowed_groups", type="Collection(Edm.String)",
                    filterable=True),                             # used in Lab 06
        SearchField(
            name="content_vector",
            type="Collection(Edm.Single)",       # a list of 1536 numbers
            searchable=True,
            vector_search_dimensions=VECTOR_SIZE,
            vector_search_profile_name="my-vector-profile",
        ),
    ]

    index = SearchIndex(
        name=INDEX_NAME,
        fields=fields,
        # HNSW is the algorithm that makes vector search fast.
        vector_search=VectorSearch(
            algorithms=[HnswAlgorithmConfiguration(name="my-hnsw")],
            profiles=[VectorSearchProfile(
                name="my-vector-profile",
                algorithm_configuration_name="my-hnsw",
            )],
        ),
        # The semantic ranker re-sorts results by meaning, after retrieval.
        semantic_search=SemanticSearch(configurations=[
            SemanticConfiguration(
                name="my-semantic-config",
                prioritized_fields=SemanticPrioritizedFields(
                    content_fields=[SemanticField(field_name="content")]
                ),
            )
        ]),
    )

    index_client.create_or_update_index(index)
    print("index", INDEX_NAME, "is ready")


# --- Task 3 -----------------------------------------------------------------
def make_vector(embeddings_client, text):
    """Turn a piece of text into a list of numbers."""
    response = embeddings_client.embeddings.create(
        model=os.environ["EMBEDDING_DEPLOYMENT"],
        input=text,
        dimensions=VECTOR_SIZE,
    )
    return response.data[0].embedding


def upload_the_chunks(search_client, embeddings_client):
    """Embed every chunk and put it in the index."""
    print("\n=== Uploading chunks ===")

    with open("data/chunks.json", encoding="utf-8") as file:
        chunks = json.load(file)

    documents = []
    for chunk in chunks:
        documents.append({
            "id": chunk["id"],
            "content": chunk["content"],
            "source": chunk["source"],
            "page": chunk["page"],
            "allowed_groups": chunk["allowed_groups"],
            "content_vector": make_vector(embeddings_client, chunk["content"]),
        })
        print(f"  embedded {chunk['id']}")

    result = search_client.upload_documents(documents)

    succeeded = sum(1 for item in result if item.succeeded)
    print(f"\nuploaded {succeeded} of {len(documents)} documents")


# --- Task 4 -----------------------------------------------------------------
def search(search_client, embeddings_client, mode):
    """Run one question through one kind of search."""
    options = {
        "select": ["id", "content", "source", "page"],
        "top": 3,
    }

    if mode in ("keyword", "hybrid", "semantic"):
        # Matches on the actual words.
        options["search_text"] = QUESTION

    if mode in ("vector", "hybrid", "semantic"):
        # Matches on meaning, even when the words are different.
        options["vector_queries"] = [VectorizedQuery(
            vector=make_vector(embeddings_client, QUESTION),
            fields="content_vector",
            k_nearest_neighbors=10,
        )]

    if mode == "semantic":
        # Re-sorts whatever came back, using a language model.
        options["query_type"] = "semantic"
        options["semantic_configuration_name"] = "my-semantic-config"

    return list(search_client.search(**options))


def compare_search_modes(search_client, embeddings_client):
    """Ask the same question four ways and print what each one returns."""
    print("\n=== Comparing search modes ===")
    print("Question:", QUESTION)

    for mode in ["keyword", "vector", "hybrid", "semantic"]:
        print(f"\n--- {mode} ---")
        for position, hit in enumerate(search(search_client, embeddings_client, mode), 1):
            preview = hit["content"][:90].replace("\n", " ")
            print(f"  {position}. [{hit['source']} p{hit['page']}] {preview}...")

    print("\nKeyword needs the same words. Vector understands meaning.")
    print("Hybrid does both. Semantic re-sorts hybrid's results by meaning.")


# --- Task 5 -----------------------------------------------------------------
def delete_the_index(index_client):
    """Tidy up. Only deletes the index this lab created."""
    print("\n=== Cleaning up ===")
    if not INDEX_NAME.startswith("lab05-"):
        raise ValueError("SEARCH_INDEX must start with 'lab05-' so we cannot "
                         "delete a shared index by mistake")
    index_client.delete_index(INDEX_NAME)
    print("deleted index", INDEX_NAME)


# --- Main -------------------------------------------------------------------
if __name__ == "__main__":
    credential = DefaultAzureCredential()

    index_client = SearchIndexClient(os.environ["SEARCH_ENDPOINT"], credential)
    search_client = SearchClient(os.environ["SEARCH_ENDPOINT"], INDEX_NAME, credential)

    token_provider = get_bearer_token_provider(
        credential, "https://cognitiveservices.azure.com/.default"
    )
    embeddings_client = OpenAI(
        base_url=os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/") + "/openai/v1/",
        api_key=token_provider,
    )

    create_the_index(index_client)
    upload_the_chunks(search_client, embeddings_client)
    compare_search_modes(search_client, embeddings_client)

    # Uncomment when you have finished the lab:
    # delete_the_index(index_client)

    print("\nDone. Lab 06 turns these results into a cited answer.")
