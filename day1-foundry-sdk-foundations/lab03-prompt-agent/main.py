"""Prompt agents and versions. https://learn.microsoft.com/azure/foundry/agents/quickstarts/prompt-agent"""
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from azure.ai.projects.models import PromptAgentDefinition


def main() -> None:
    load_dotenv()
    project = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
        allow_preview=True,
    )

    agent_name = "prompt-agent1"
    instructions = "You are a concise workshop assistant. Explain clearly and briefly."

    agent = project.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=os.environ["MODEL_DEPLOYMENT"],
            instructions=instructions,
        ),
    )
    print("Created", agent.name, "version", agent.version)

    for version in project.agents.list_versions(agent_name=agent_name):
        print("Stored version:", version.version)

    client = project.get_openai_client(agent_name=agent_name)
    response = client.responses.create(input="Explain why an agent might use a tool.", store=False)
    print(response.output_text)


if __name__ == "__main__":
    main()
