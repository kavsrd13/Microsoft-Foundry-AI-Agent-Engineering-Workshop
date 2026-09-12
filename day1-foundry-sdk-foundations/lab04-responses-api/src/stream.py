"""Streaming text. https://learn.microsoft.com/azure/foundry/agents/quickstarts/responses-api"""
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

def main() -> None:
    load_dotenv()
    project = AIProjectClient(endpoint=os.environ["PROJECT_ENDPOINT"], credential=DefaultAzureCredential())
    client = project.get_openai_client()
    with client.responses.create(model=os.environ["MODEL_DEPLOYMENT"],
                                 input="Explain tool calling in two sentences.", stream=True, store=False) as events:
        for event in events:
            if event.type == "response.output_text.delta":
                print(event.delta, end="", flush=True)
    print()


if __name__ == "__main__":
    main()
