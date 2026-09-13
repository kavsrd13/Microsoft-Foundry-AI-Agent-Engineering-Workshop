import asyncio
import os

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential

async def main() -> None:
    agent = Agent(
        client=FoundryChatClient(
            project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
            model=os.environ["FOUNDRY_MODEL"],
            credential=AzureCliCredential(),
        ),
        instructions="You are a research assistant. Use web search to find current information.",
        tools=[
            FoundryChatClient.get_web_search_tool(),
        ],
    )

    result = await agent.run("What are the latest updates to Microsoft Foundry?")
    print(f"Agent: {result}")

if __name__ == "__main__":
    asyncio.run(main())
