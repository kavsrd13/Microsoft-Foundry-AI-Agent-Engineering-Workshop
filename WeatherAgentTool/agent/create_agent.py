from dotenv import load_dotenv
load_dotenv()

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


PROJECT_ENDPOINT = (
    "https://agentresource123.services.ai.azure.com/"
    "api/projects/proj-default"
)

STORAGE_QUEUE_ENDPOINT = (
    "https://functiontool12.queue.core.windows.net"
)


project = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
)


weather_tool = AzureFunctionTool(
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
            description=(
                "Get weather information for a location. "
                "Use this tool whenever the user asks about weather."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": (
                            "The city or location for which weather "
                            "information is required."
                        ),
                    }
                },
                "required": ["location"],
            },
        ),
    )
)


agent = project.agents.create_version(
    agent_name="WeatherAgent",
    definition=PromptAgentDefinition(
        model="gpt-4o",
        instructions=(
            "You are a helpful weather assistant. "
            "When the user asks about weather, "
            "always use the GetWeather tool. "
            "Return the tool result clearly."
        ),
        tools=[weather_tool],
    ),
)


print("\nAgent created successfully.")
print(f"Agent ID: {agent.id}")
print(f"Agent name: {agent.name}")
print(f"Agent version: {agent.version}")


openai_client = project.get_openai_client()


print("\nSending a weather question to the agent...")


response = openai_client.responses.create(
    input="What is the weather in Mumbai?",
    extra_body={
        "agent_reference": {
            "name": agent.name,
            "version": str(agent.version),
            "type": "agent_reference",
        }
    },
)


print("\nFinal response:")
print(response.output_text)
