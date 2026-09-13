"""Create an agent with an Azure Functions queue-based tool and ask a question."""
import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AzureFunctionBinding,
    AzureFunctionDefinition,
    AzureFunctionStorageQueue,
    AzureFunctionDefinitionFunction,
    AzureFunctionTool,
    PromptAgentDefinition,
)
from dotenv import load_dotenv

load_dotenv()

PROJECT_ENDPOINT = os.environ["PROJECT_ENDPOINT"]
STORAGE_QUEUE_ENDPOINT = os.environ["STORAGE_QUEUE_ENDPOINT"]
MODEL = os.environ.get("MODEL_DEPLOYMENT", "gpt-4o-mini")

# 1. Create project client using Microsoft Entra credentials
project = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
)
openai = project.get_openai_client()

# 2. Define the Azure Function tool pointing to the input and output queues
tool = AzureFunctionTool(
    azure_function=AzureFunctionDefinition(
        input_binding=AzureFunctionBinding(
            storage_queue=AzureFunctionStorageQueue(
                queue_name="get-weather-input-queue",
                queue_service_endpoint=STORAGE_QUEUE_ENDPOINT,
            )
        ),
        output_binding=AzureFunctionBinding(
            storage_queue=AzureFunctionStorageQueue(
                queue_name="get-weather-output-queue",
                queue_service_endpoint=STORAGE_QUEUE_ENDPOINT,
            )
        ),
        function=AzureFunctionDefinitionFunction(
            name="GetWeather",
            description="Get the weather in a location.",
            parameters={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The location to look up (e.g. Seattle, WA).",
                    }
                },
                "required": ["location"],
            },
        ),
    )
)

# 3. Create a versioned prompt agent with the Azure Function tool attached
agent = project.agents.create_version(
    agent_name="azure-function-agent-get-weather",
    definition=PromptAgentDefinition(
        model=MODEL,
        instructions="You are a helpful support agent. When asked about the weather, use the GetWeather tool.",
        tools=[tool],
    ),
)
print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

# 4. Ask a question that triggers the Azure Function queue tool
print("
Asking: What is the weather in Seattle, WA?")
response = openai.responses.create(
    input="What is the weather in Seattle, WA?",
    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
)

print(f"
Response from agent:
{response.output_text}")
