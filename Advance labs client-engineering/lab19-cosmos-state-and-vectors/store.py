"""Identity comes from an SDK-acquired token, never a request parameter."""
import base64
import json
import os
from pathlib import Path
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()
credential = DefaultAzureCredential()

def signed_in_partition():
    # Decode only the token acquired directly from Entra by the credential.
    # This is NOT a token validator for incoming web requests.
    token = credential.get_token('https://cosmos.azure.com/.default').token
    payload = token.split('.')[1]
    claims = json.loads(base64.urlsafe_b64decode(payload + '=' * (-len(payload) % 4)))
    return claims['tid'] + ':' + claims['oid']

def container(name):
    client = CosmosClient(os.environ['COSMOS_ENDPOINT'], credential=credential)
    return client.get_database_client('workshop-memory').get_container_client(name)
