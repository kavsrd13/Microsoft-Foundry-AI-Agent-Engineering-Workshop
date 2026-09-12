"""Read metadata only; never read or modify other users' conversation content."""
import os
from azure.cosmos import CosmosClient
from store import credential

database = CosmosClient(os.environ['COSMOS_ENDPOINT'], credential=credential).get_database_client('enterprise_memory')
for item in database.list_containers():
    print(item['id'], 'partition:', item['partitionKey'], 'TTL:', item.get('defaultTtl'))
