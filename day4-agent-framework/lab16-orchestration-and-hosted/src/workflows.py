"""Actual sequential and concurrent workflows. https://learn.microsoft.com/agent-framework/workflows/orchestrations/"""
import asyncio
import json
import os
import time
from pathlib import Path
from agent_framework import Agent
from agent_framework_orchestrations import SequentialBuilder, ConcurrentBuilder
from agent_framework_foundry import FoundryChatClient
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv
async def main() -> None:
    root = Path(__file__).resolve().parents[1]
    load_dotenv(root / '.env')
    task = 'Prepare a short order service briefing from this synthetic data: ' + (root / 'data/orders.json').read_text()
    timings = {}
    async with DefaultAzureCredential() as credential:
        async with FoundryChatClient(project_endpoint=os.environ['PROJECT_ENDPOINT'], model=os.environ['MODEL_DEPLOYMENT_NAME'], credential=credential) as client:
            for label, builder in [('sequential', SequentialBuilder), ('concurrent', ConcurrentBuilder)]:
                agents = [Agent(client, name=name, instructions=instructions, default_options={'store': False}) for name, instructions in [('retriever', 'Extract three relevant order facts from the supplied data.'), ('analyst', 'Identify service implications using available facts. Do not invent facts.'), ('writer', 'Write a concise Australian English briefing using the information available.')]]
                workflow = builder(participants=agents).build()
                start = time.perf_counter()
                result = await workflow.run(task)
                timings[label] = round(time.perf_counter() - start, 2)
                print(label, result.get_outputs())
    (root / 'data/timings.json').write_text(json.dumps(timings, indent=2))
    print('Measured seconds:', timings)
if __name__ == '__main__':
    asyncio.run(main())
