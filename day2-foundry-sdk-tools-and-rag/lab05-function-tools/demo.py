"""Smallest possible example: add one Python function tool to an agent and create a version."""

import os

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FunctionTool, PromptAgentDefinition
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

from state import state


def greet(name: str) -> dict:
    return {"message": f"Hello, {name}!"}


def main() -> None:
    load_dotenv()

    project_endpoint = os.getenv("PROJECT_ENDPOINT")
    model_deployment = os.getenv("MODEL_DEPLOYMENT")
    if not project_endpoint or not model_deployment:
        raise ValueError("Set PROJECT_ENDPOINT and MODEL_DEPLOYMENT in .env")

    project = AIProjectClient(project_endpoint, DefaultAzureCredential())
    saved = state()

    greet_tool = FunctionTool(
        name="greet",
        description="Return a short greeting for a name.",
        strict=True,
        parameters={
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
            "additionalProperties": False,
        },
    )

    version = project.agents.create_version(
        agent_name=saved["name"],
        definition=PromptAgentDefinition(
            model=model_deployment,
            instructions="Use the greet tool when the user asks for a greeting.",
            tools=[greet_tool],
        ),
    )

    print(f"Agent name: {saved['name']}")
    print(f"Agent version created: {version.version}")


if __name__ == "__main__":
    main()
