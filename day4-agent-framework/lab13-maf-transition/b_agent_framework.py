"""Same task through MAF. https://learn.microsoft.com/agent-framework/integrations/by-component/model-providers/microsoft-foundry"""
import asyncio
import os
from pathlib import Path
from agent_framework import Agent
from agent_framework_foundry import FoundryChatClient
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv
async def main() -> None:
    load_dotenv()
    async with DefaultAzureCredential() as credential, AIProjectClient(endpoint=os.environ['PROJECT_ENDPOINT'], credential=credential) as project:
        client = FoundryChatClient(project_client=project, model=os.environ['MODEL_DEPLOYMENT_NAME'])
        agent = Agent(client, instructions='Use Australian English. Answer in two sentences.', default_options={'store': False})
        print((await agent.run('Explain why a government service assistant should cite its sources.')).text)
if __name__ == '__main__':
    asyncio.run(main())
