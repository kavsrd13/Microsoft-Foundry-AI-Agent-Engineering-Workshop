"""Hosted entry point. https://learn.microsoft.com/azure/foundry/how-to/develop/framework-hosted-agents"""
import os
from agent_framework import Agent
from agent_framework_foundry import FoundryChatClient
from agent_framework_foundry_hosting import ResponsesHostServer
from azure.identity import DefaultAzureCredential


def main() -> None:
    client = FoundryChatClient(
        project_endpoint=os.environ['AZURE_AI_PROJECT_ENDPOINT'],
        model=os.environ['AZURE_AI_MODEL_DEPLOYMENT_NAME'],
        credential=DefaultAzureCredential(),
    )
    agent = Agent(client, name='acme-lab16-assistant',
                  instructions='Explain public service concepts concisely in Australian English.')
    ResponsesHostServer(agent).run()


if __name__ == '__main__':
    main()
