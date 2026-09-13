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
        instructions="You are a helpful assistant.",
    )

    print("Agent: ", end="", flush=True)
    async for chunk in agent.run("Tell me a fun fact.", stream=True):
        if chunk.text:
            print(chunk.text, end="", flush=True)
    print()

if __name__ == "__main__":
    asyncio.run(main())
