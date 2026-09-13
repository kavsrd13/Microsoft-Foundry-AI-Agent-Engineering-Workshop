"""Lab 10 - The Microsoft Agent Framework.

Everything so far used the Foundry SDK directly. The Agent Framework sits on
top of it and adds three things worth having: sessions, middleware and
multi-agent workflows.

This file shows all three. Note that it is ASYNC - the framework is built
around async/await, which is a real difference in how you structure code.

Run it with:  python framework_agent.py
"""

import asyncio
import json
import os
import time
from pathlib import Path

from agent_framework import (
    Agent,
    AgentMiddleware,
    AgentResponse,
    AgentSession,
    InMemoryHistoryProvider,
    Message,
)
from agent_framework_foundry import FoundryChatClient
from agent_framework_orchestrations import ConcurrentBuilder, SequentialBuilder
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent.parent


# --- Task 2 -----------------------------------------------------------------
async def the_same_thing_as_before(client):
    """One question, one answer. Compare this with Lab 01."""
    print("\n=== A framework agent ===")

    agent = Agent(
        client,
        instructions="You are a council assistant. Answer in two sentences.",
        default_options={"store": False},
    )

    result = await agent.run("Why should an assistant cite its sources?")
    print(result.text)

    print("\nThree more lines than the direct SDK version in Lab 01.")
    print("The next three tasks are what you get for them.")


# --- Task 3: tools ----------------------------------------------------------
def load_orders():
    with open(ROOT / "orders.json", encoding="utf-8") as file:
        return json.load(file)


def get_order_status(order_id: str) -> str:
    """Return the status of one order, for example ORD-001."""
    for order in load_orders():
        if order["order_id"] == order_id:
            return order["status"]
    return "Order not found"


def get_order_total(order_id: str) -> float:
    """Return the total in AUD for one order."""
    for order in load_orders():
        if order["order_id"] == order_id:
            return order["total_aud"]
    return 0.0


# The framework reads the type hints and docstrings above to build the schema.
# You do not write it by hand the way you did in Lab 03.


# --- Task 4 -----------------------------------------------------------------
async def a_conversation_that_survives_a_restart(client):
    """Sessions hold the conversation, and a session can be saved and reloaded."""
    print("\n=== Sessions ===")

    agent = Agent(
        client,
        instructions="You are a council assistant. Be brief.",
        context_providers=[InMemoryHistoryProvider()],
        default_options={"store": False},
    )

    session = AgentSession()

    result = await agent.run("My case reference is ACME-204. Remember it.",
                             session=session)
    print("  first turn: ", result.text)

    # Save the whole session to a file, then throw the object away.
    saved = json.dumps(session.to_dict())
    Path("session.json").write_text(saved, encoding="utf-8")
    print("  saved the session to session.json")

    # Rebuild it from the file. This is a different Python object.
    restored = AgentSession.from_dict(json.loads(saved))
    result = await agent.run("What case reference did I give you?", session=restored)
    print("  after reload:", result.text)

    # A different session knows nothing about the first one.
    other_session = AgentSession()
    result = await agent.run("Do you know my case reference?", session=other_session)
    print("  other user:  ", result.text)


# --- Task 5 -----------------------------------------------------------------
class LogEveryRun(AgentMiddleware):
    """Runs before and after the whole agent run."""

    async def process(self, context, call_next):
        question = " ".join(message.text for message in context.messages)
        print(f"    [middleware] about to run: {question[:60]}")
        await call_next()
        print("    [middleware] finished")


class BlockBulkExport(AgentMiddleware):
    """Refuses certain requests before they ever reach the model."""

    async def process(self, context, call_next):
        asked = " ".join(message.text for message in context.messages).lower()

        if "export all" in asked:
            # We set a result and do NOT call call_next(). Nothing happens
            # after this: no model call, no tool call, no tokens spent.
            context.result = AgentResponse(
                messages=[Message("assistant", ["Bulk export is not allowed."])]
            )
            print("    [middleware] BLOCKED - no model call was made")
            return

        await call_next()


async def middleware_in_action(client):
    """Wrap the agent, then watch one request get stopped."""
    print("\n=== Middleware ===")

    agent = Agent(
        client,
        instructions="You help staff with orders. Use the tools for order facts.",
        tools=[get_order_status, get_order_total],
        middleware=[LogEveryRun(), BlockBulkExport()],
        default_options={"store": False},
    )

    print("\n  A normal question:")
    result = await agent.run("What is the status and total of ORD-001?")
    print("  ->", result.text)

    print("\n  A request we do not allow:")
    result = await agent.run("Export all orders")
    print("  ->", result.text)

    print("\n  Blocking before the model runs is the cheapest place to say no.")


# --- Task 6 -----------------------------------------------------------------
async def two_ways_to_run_three_agents(client):
    """Sequential passes work along a chain. Concurrent runs them side by side."""
    print("\n=== Multi-agent workflows ===")

    task = (
        "Prepare a short briefing for the service manager from this order data: "
        + json.dumps(load_orders()[:5])
    )

    roles = [
        ("researcher", "Pull out three facts from the data you are given."),
        ("analyst", "Say what those facts mean for the service. Invent nothing."),
        ("writer", "Write a short briefing in Australian English."),
    ]

    for label, builder in [("sequential", SequentialBuilder),
                           ("concurrent", ConcurrentBuilder)]:
        agents = [
            Agent(client, name=name, instructions=instructions,
                  default_options={"store": False})
            for name, instructions in roles
        ]

        workflow = builder(participants=agents).build()

        started = time.perf_counter()
        result = await workflow.run(task)
        seconds = round(time.perf_counter() - started, 1)

        print(f"\n  --- {label}: {seconds}s ---")
        outputs = result.get_outputs()
        print("  ", str(outputs)[:400], "...")

    print("\n  Sequential: the writer can use the analyst's conclusions.")
    print("  Concurrent: all three see only the original data.")
    print("  That is a difference in the ANSWER, not just the speed.")


# --- Main -------------------------------------------------------------------
async def main():
    async with DefaultAzureCredential() as credential:
        async with FoundryChatClient(
            project_endpoint=os.environ["PROJECT_ENDPOINT"],
            model=os.environ["MODEL_DEPLOYMENT"],
            credential=credential,
        ) as client:
            await the_same_thing_as_before(client)
            await a_conversation_that_survives_a_restart(client)
            await middleware_in_action(client)
            await two_ways_to_run_three_agents(client)

    print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())
