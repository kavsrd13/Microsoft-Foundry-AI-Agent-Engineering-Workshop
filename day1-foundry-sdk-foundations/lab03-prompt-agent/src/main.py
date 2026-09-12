"""Prompt agents and versions. https://learn.microsoft.com/azure/foundry/agents/quickstarts/prompt-agent"""
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
import json
from pathlib import Path
from uuid import uuid4
from azure.ai.projects.models import PromptAgentDefinition


def main() -> None:
    load_dotenv()
    project = AIProjectClient(endpoint=os.environ["PROJECT_ENDPOINT"], credential=DefaultAzureCredential())
    state_file = Path("data/resource-state.json")
    if not state_file.exists():
        state_file.write_text(json.dumps({"agent": "acme-lab03-prompt-" + uuid4().hex[:8]}))
    state = json.loads(state_file.read_text())
    for instructions in ["Answer in Australian English.", "Answer in Australian English using one short sentence."]:
        agent = project.agents.create_version(
            agent_name=state["agent"],
            definition=PromptAgentDefinition(model=os.environ["MODEL_DEPLOYMENT"], instructions=instructions),
        )
        print("Created", agent.name, "version", agent.version)
    for version in project.agents.list_versions(agent_name=state["agent"]):
        print("Stored version:", version.version)
    client = project.get_openai_client(agent_name=state["agent"])
    response = client.responses.create(input="Explain why an agent might use a tool.", store=False)
    print(response.output_text)


if __name__ == "__main__":
    main()
