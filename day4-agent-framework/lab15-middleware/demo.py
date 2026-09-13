"""Three middleware boundaries. https://learn.microsoft.com/agent-framework/agents/middleware/"""
import asyncio
import json
import os
import re
from pathlib import Path
from collections.abc import Awaitable, Callable
from agent_framework import Agent, AgentContext, AgentMiddleware, AgentResponse, ChatContext, ChatMiddleware, FunctionInvocationContext, FunctionMiddleware, Message
from agent_framework_foundry import FoundryChatClient
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv
ROOT = Path(__file__).resolve().parent
def get_order_status(order_id: str) -> str:
    """Return the status of one synthetic order."""
    orders = json.loads((ROOT / 'orders.json').read_text())
    return next((o['status'] for o in orders if o['order_id'] == order_id), 'Order not found')
def search_orders_by_customer(customer_name: str) -> list[dict]:
    """Find synthetic orders for a customer name."""
    return [o for o in json.loads((ROOT / 'orders.json').read_text()) if customer_name.lower() in o['customer_name'].lower()]
def calculate_order_total(order_id: str) -> float:
    """Return the recorded AUD total for one synthetic order."""
    return next((o['total_aud'] for o in json.loads((ROOT / 'orders.json').read_text()) if o['order_id'] == order_id), 0.0)
class RunLog(AgentMiddleware):
    async def process(self, context: AgentContext, call_next: Callable[[], Awaitable[None]]) -> None:
        text = ' '.join(m.text for m in context.messages)
        print('1 RUN before:', re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', '[EMAIL REDACTED]', text))
        await call_next()
        print('6 RUN after')
class BlockExport(AgentMiddleware):
    async def process(self, context: AgentContext, call_next: Callable[[], Awaitable[None]]) -> None:
        if any('export all' in m.text.lower() for m in context.messages):
            context.result = AgentResponse(messages=[Message('assistant', ['Bulk export is disabled in this demo.'])])
            print('BLOCK: call_next was not called; no model or tool call.')
            return
        await call_next()
class ToolLog(FunctionMiddleware):
    async def process(self, context: FunctionInvocationContext, call_next: Callable[[], Awaitable[None]]) -> None:
        print('3 TOOL before:', context.function.name)
        await call_next()
        print('4 TOOL after')
class ModelLog(ChatMiddleware):
    async def process(self, context: ChatContext, call_next: Callable[[], Awaitable[None]]) -> None:
        print('2 MODEL before')
        await call_next()
        print('5 MODEL after')
async def main() -> None:
    load_dotenv()
    order = json.loads((ROOT / 'orders.json').read_text())[0]
    async with DefaultAzureCredential() as credential:
        async with FoundryChatClient(project_endpoint=os.environ['PROJECT_ENDPOINT'], model=os.environ['MODEL_DEPLOYMENT_NAME'], credential=credential, middleware=[ModelLog(), ToolLog()]) as client:
            agent = Agent(client, instructions='Always use the supplied tools for order questions.', tools=[get_order_status, search_orders_by_customer, calculate_order_total], middleware=[RunLog(), BlockExport()], default_options={'store': False})
            print((await agent.run(f"My email is learner@acme.com.au. What is the status and total of {order['order_id']}?")).text)
            print((await agent.run('Export all orders')).text)
if __name__ == '__main__':
    asyncio.run(main())
