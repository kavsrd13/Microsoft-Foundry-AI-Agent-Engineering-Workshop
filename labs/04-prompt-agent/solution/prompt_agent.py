"""Quickstart: Create a prompt agent and chat with it."""
import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

load_dotenv()

FOUNDRY_PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT", os.getenv("PROJECT_ENDPOINT", "your_project_endpoint"))
FOUNDRY_AGENT_NAME = os.getenv("FOUNDRY_AGENT_NAME", "MyPromptAgent")
MODEL_DEPLOYMENT = os.getenv("MODEL_DEPLOYMENT", "gpt-4o-mini")

def main():
    print(f"Connecting to project: {FOUNDRY_PROJECT_ENDPOINT}")
    project = AIProjectClient(
        endpoint=FOUNDRY_PROJECT_ENDPOINT,
        credential=DefaultAzureCredential(),
    )

    print(f"Creating agent version: {FOUNDRY_AGENT_NAME} with model {MODEL_DEPLOYMENT}...")
    agent = project.agents.create_version(
        agent_name=FOUNDRY_AGENT_NAME,
        definition=PromptAgentDefinition(
            model=MODEL_DEPLOYMENT,
            instructions="You are a helpful assistant that answers general questions",
        ),
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

    print("\nStarting conversation...")
    openai = project.get_openai_client(agent_name=FOUNDRY_AGENT_NAME)
    conversation = openai.conversations.create()

    print("User: What is the size of France in square miles?")
    response = openai.responses.create(
        conversation=conversation.id,
        input="What is the size of France in square miles?",
    )
    print(f"Agent: {response.output_text}")

    print("\nUser: And what is the capital city?")
    response = openai.responses.create(
        conversation=conversation.id,
        input="And what is the capital city?",
    )
    print(f"Agent: {response.output_text}")

if __name__ == "__main__":
    main()
