"""Remove only recorded lab resources. https://learn.microsoft.com/azure/foundry/agents/quickstarts/prompt-agent"""
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
    assert state["agent"].startswith("acme-lab03-prompt-")
    try:
        project.agents.delete(agent_name=state["agent"])
    except ResourceNotFoundError:
        pass
    state_file.unlink()
    print("Cleanup complete.")


if __name__ == "__main__":
    main()
