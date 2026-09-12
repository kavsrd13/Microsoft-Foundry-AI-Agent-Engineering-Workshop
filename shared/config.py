"""Optional configuration convenience. https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview"""
import os
from dotenv import load_dotenv


def project_endpoint() -> str:
    load_dotenv()
    return os.environ["PROJECT_ENDPOINT"]
