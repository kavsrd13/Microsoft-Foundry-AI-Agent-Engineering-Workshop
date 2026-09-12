import json
import os
from pathlib import Path
from openai import OpenAI
from azure.identity import get_bearer_token_provider
from store import container, credential, signed_in_partition

model = OpenAI(base_url=os.environ['AZURE_OPENAI_BASE_URL'],
               api_key=get_bearer_token_provider(credential, 'https://cognitiveservices.azure.com/.default'))
def embed(text):
    return model.embeddings.create(model=os.environ['EMBEDDING_DEPLOYMENT_NAME'],
                                   input=text, dimensions=256).data[0].embedding

records = json.loads((Path(__file__).parents[1] / 'data/records.json').read_text())
documents = container('vectors')
user = signed_in_partition()
for record in records:
    documents.upsert_item({**record, 'userId':user, 'embedding':embed(record['text'])})
query = embed('How do I replace my recycling container?')
rows = documents.query_items(
    query='SELECT TOP 2 c.id, c.text, VectorDistance(c.embedding, @vector) AS distance FROM c ORDER BY VectorDistance(c.embedding, @vector)',
    parameters=[{'name':'@vector','value':query}], partition_key=user)
for row in rows:
    print(row)
