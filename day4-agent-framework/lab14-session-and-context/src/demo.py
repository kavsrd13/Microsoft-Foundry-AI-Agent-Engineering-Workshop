"""Local session memory plus preference context. https://learn.microsoft.com/agent-framework/concepts/agents/conversations/context-providers"""
import asyncio
import json
import os
from pathlib import Path
from typing import Any
from agent_framework import Agent, AgentSession, ContextProvider, SessionContext, SupportsAgentRun, InMemoryHistoryProvider
from agent_framework_foundry import FoundryChatClient
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv
ROOT = Path(__file__).resolve().parents[1]
class Preferences(ContextProvider):
    async def before_run(self, *, agent: SupportsAgentRun, session: AgentSession, context: SessionContext, state: dict[str, Any]) -> None:
        profiles = json.loads((ROOT / 'data/user_preferences.json').read_text())
        profile = next(p for p in profiles if p['user_id'] == session.state['user_id'])
        context.extend_instructions(self.source_id, f"Use {profile['language']} and a {profile['tone']} tone. Preferred channel: {profile['preferred_channel']}.")
async def main() -> None:
    load_dotenv(ROOT / '.env')
    profiles = json.loads((ROOT / 'data/user_preferences.json').read_text())
    async with DefaultAzureCredential() as credential:
        client = FoundryChatClient(project_endpoint=os.environ['PROJECT_ENDPOINT'], model=os.environ['MODEL_DEPLOYMENT_NAME'], credential=credential)
        async with client:
            agent = Agent(client, instructions='Help with public services. Do not invent policy.', context_providers=[InMemoryHistoryProvider(), Preferences('preferences')], default_options={'store': False})
            session = AgentSession()
            session.state['user_id'] = profiles[0]['user_id']
            print((await agent.run('My case reference is ACME-204. Please remember it.', session=session)).text)
            (ROOT / 'data/session.json').write_text(json.dumps(session.to_dict(), indent=2))
            restored = AgentSession.from_dict(json.loads((ROOT / 'data/session.json').read_text()))
            print((await agent.run('What case reference did I give you?', session=restored)).text)
            other = AgentSession()
            other.state['user_id'] = profiles[1]['user_id']
            print((await agent.run('Introduce how you can help. Do you know my case reference?', session=other)).text)
if __name__ == '__main__':
    asyncio.run(main())
