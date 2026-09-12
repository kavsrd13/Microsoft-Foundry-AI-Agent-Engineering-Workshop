"""Optional Entra helpers. https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview"""
import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from dotenv import load_dotenv


def get_credential() -> DefaultAzureCredential:
    return DefaultAzureCredential()


def get_project_client() -> AIProjectClient:
    load_dotenv()
    return AIProjectClient(endpoint=os.environ["PROJECT_ENDPOINT"], credential=get_credential())
