"""Create an agent that uses the Azure Function as a tool, ask it a question, tidy up.

Run it with:  python ask_the_agent.py
The Function must already be deployed and listening on the input queue.
"""

import os
import time

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AzureFunctionBinding,
    AzureFunctionDefinition,
    AzureFunctionDefinitionFunction,
    AzureFunctionStorageQueue,
    AzureFunctionTool,
    PromptAgentDefinition,
)
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

PROJECT_ENDPOINT = os.environ["PROJECT_ENDPOINT"]
STORAGE_QUEUE_ENDPOINT = os.environ["STORAGE_QUEUE_ENDPOINT"]
MODEL = os.environ["MODEL_DEPLOYMENT"]

AGENT_NAME = "azure-function-agent-get-weather"


# --- Task 2 -----------------------------------------------------------------
def describe_the_tool():
    """Tell the agent about the Function: what it does, and which queues to use."""
    return AzureFunctionTool(
        azure_function=AzureFunctionDefinition(
            # Where the agent drops its request.
            input_binding=AzureFunctionBinding(
                storage_queue=AzureFunctionStorageQueue(
                    queue_name="get-weather-input-queue",
                    queue_service_endpoint=STORAGE_QUEUE_ENDPOINT,
                )
            ),
            # Where the agent waits for the answer.
            output_binding=AzureFunctionBinding(
                storage_queue=AzureFunctionStorageQueue(
                    queue_name="get-weather-output-queue",
                    queue_service_endpoint=STORAGE_QUEUE_ENDPOINT,
                )
            ),
            # What the model sees: a name, a purpose and the arguments it may send.
            function=AzureFunctionDefinitionFunction(
                name="GetWeather",
                description="Get the current weather in a location.",
                parameters={
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city or town to look up.",
                        }
                    },
                    "required": ["location"],
                },
            ),
        )
    )


# --- Task 3 -----------------------------------------------------------------
def create_the_agent(project):
    """Save an agent version that has the Function tool attached."""
    agent = project.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=MODEL,
            instructions=(
                "You are a helpful support agent. When asked about the weather, "
                "always use the GetWeather tool rather than guessing."
            ),
            tools=[describe_the_tool()],
        ),
    )
    print(f"Created agent {agent.name}, version {agent.version}")
    return agent


# --- Task 4 -----------------------------------------------------------------
def ask(client, agent, question):
    """Ask a question. The service handles the queue round-trip for us."""
    print(f"\nYou: {question}")
    started = time.perf_counter()

    response = client.responses.create(
        input=question,
        extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
    )

    print(f"Agent: {response.output_text}")
    print(f"(took {time.perf_counter() - started:.1f}s including the queue round-trip)")
    return response


# --- Task 5 -----------------------------------------------------------------
def delete_the_agent(project, agent):
    project.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    print(f"\nDeleted {agent.name} version {agent.version}")


# --- Main -------------------------------------------------------------------
if __name__ == "__main__":
    project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=DefaultAzureCredential())
    client = project.get_openai_client()

    agent = create_the_agent(project)
    try:
        ask(client, agent, "What is the weather like in Sydney right now?")
        ask(client, agent, "And in Melbourne?")
    finally:
        delete_the_agent(project, agent)
