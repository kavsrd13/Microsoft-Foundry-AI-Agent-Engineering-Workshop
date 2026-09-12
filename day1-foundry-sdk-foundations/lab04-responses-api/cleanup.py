"""Remove only recorded lab resources. https://learn.microsoft.com/azure/foundry/agents/quickstarts/responses-api"""
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
import json
from pathlib import Path
from azure.core.exceptions import ResourceNotFoundError


def main() -> None:
    state_file = Path("data/resource-state.json")
    if not state_file.exists():
        print("Nothing to clean up.")
        return
    state = json.loads(state_file.read_text())
    print("Resources:", state)
    if input("Type DELETE to remove these lab resources: ") != "DELETE":
        return
    load_dotenv()
    project = AIProjectClient(endpoint=os.environ["PROJECT_ENDPOINT"], credential=DefaultAzureCredential())
    from openai import NotFoundError
    client = project.get_openai_client()
    for response_id in state.get("responses", []):
        try:
            client.responses.delete(response_id)
        except NotFoundError:
            pass
    for conversation_id in state["conversations"]:
        try:
            client.conversations.delete(conversation_id)
        except NotFoundError:
            pass
    state_file.unlink()
    print("Cleanup complete.")


if __name__ == "__main__":
    main()
