"""Responses API, conversations and streaming. https://learn.microsoft.com/azure/foundry/agents/quickstarts/responses-api"""
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
import json
from pathlib import Path


def main() -> None:
    load_dotenv()
    project = AIProjectClient(endpoint=os.environ["PROJECT_ENDPOINT"], credential=DefaultAzureCredential())
    client = project.get_openai_client()
    state_file = Path("data/resource-state.json")
    state = json.loads(state_file.read_text()) if state_file.exists() else {"conversations": []}
    conversation = client.conversations.create()
    state["conversations"].append(conversation.id)
    state_file.write_text(json.dumps(state))
    for question in ["Our synthetic workshop is in Sydney. Remember this location.", "Which city is our workshop in?"]:
        response = client.responses.create(
            model=os.environ["MODEL_DEPLOYMENT"], instructions="Answer briefly in Australian English.",
            conversation=conversation.id, input=question,
        )
        state.setdefault("responses", []).append(response.id)
        state_file.write_text(json.dumps(state))
        print(response.output_text)


if __name__ == "__main__":
    main()
