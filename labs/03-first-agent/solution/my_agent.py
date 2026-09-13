"""Lab 03 - Build your first agent.

An agent is a name, a model, some instructions and (optionally) tools, stored
in your project. This file creates one, gives it two versions, then gives it
three tools and runs the tool loop by hand.

Run it with:  python my_agent.py
"""

import json
import os

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FunctionTool, PromptAgentDefinition
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

MODEL = os.environ["MODEL_DEPLOYMENT"]

# Put your initials here so your agent does not clash with anyone else's.
AGENT_NAME = "acme-agent-" + os.environ.get("YOUR_INITIALS", "xx")


# --- Task 2 -----------------------------------------------------------------
def create_two_versions(project):
    """Publish two versions of the same agent, with different instructions."""
    print("\n=== Creating agent versions ===")

    first = project.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=MODEL,
            instructions="You are a council assistant. Answer in Australian English.",
        ),
    )
    print("created version", first.version)

    second = project.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=MODEL,
            instructions=(
                "You are a council assistant. Answer in Australian English, "
                "in one short sentence."
            ),
        ),
    )
    print("created version", second.version)

    print("\nStored versions of", AGENT_NAME + ":")
    for version in project.agents.list_versions(agent_name=AGENT_NAME):
        print(" - version", version.version)

    # The first version still exists, unchanged. Versions never overwrite.
    return second.version


# --- Task 3 -----------------------------------------------------------------
def ask_the_agent(project):
    """Call the agent by name. Notice we do not pass a model or instructions."""
    print("\n=== Asking the agent ===")

    agent_client = project.get_openai_client(agent_name=AGENT_NAME)

    response = agent_client.responses.create(
        input="Why should an assistant use a tool instead of guessing?",
    )

    print(response.output_text)


# --- Task 4: the three tools ------------------------------------------------
def load_orders():
    with open("orders.json", encoding="utf-8") as file:
        return json.load(file)


def get_order_status(order_id):
    """Look up one order."""
    for order in load_orders():
        if order["order_id"] == order_id:
            return order
    return {"error": "Order not found"}


def find_orders_for_customer(customer_name):
    """Find every order belonging to a customer."""
    matches = []
    for order in load_orders():
        if customer_name.lower() in order["customer_name"].lower():
            matches.append(order)
    return matches


# The model never sees the Python above. It only sees these descriptions.
TOOL_SCHEMAS = [
    FunctionTool(
        name="get_order_status",
        description="Get the status of one order by its order ID.",
        strict=True,
        parameters={
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
            "additionalProperties": False,
        },
    ),
    FunctionTool(
        name="find_orders_for_customer",
        description="Find all orders belonging to a customer name.",
        strict=True,
        parameters={
            "type": "object",
            "properties": {"customer_name": {"type": "string"}},
            "required": ["customer_name"],
            "additionalProperties": False,
        },
    ),
]

# Our own list of what we are willing to run. A name that is not in here is
# never executed, no matter what the model asks for.
AVAILABLE_TOOLS = {
    "get_order_status": get_order_status,
    "find_orders_for_customer": find_orders_for_customer,
}


# --- Task 5 -----------------------------------------------------------------
def add_tools_to_the_agent(project):
    """Publish a new version that has tools attached."""
    print("\n=== Adding tools ===")

    version = project.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=MODEL,
            instructions=(
                "You help staff with orders. Always use the tools for order "
                "facts. Never guess an order status. Amounts are in AUD."
            ),
            tools=TOOL_SCHEMAS,
        ),
    )
    print("created version", version.version, "with", len(TOOL_SCHEMAS), "tools")
    return version.version


def run_the_tool_loop(project, version):
    """Ask a question that needs tools, and answer the model's tool requests."""
    print("\n=== Running the tool loop ===")

    client = project.get_openai_client()
    agent_reference = {
        "agent": {"type": "agent_reference", "name": AGENT_NAME, "version": version}
    }

    first_order = load_orders()[0]
    question = (
        f"What orders does {first_order['customer_name']} have, "
        f"and what is the status of {first_order['order_id']}?"
    )
    print("Question:", question, "\n")

    response = client.responses.create(input=question, extra_body=agent_reference)

    # Keep going until the model stops asking for tools.
    while True:
        tool_calls = [item for item in response.output if item.type == "function_call"]
        if not tool_calls:
            break

        tool_results = []
        for call in tool_calls:
            function = AVAILABLE_TOOLS[call.name]
            arguments = json.loads(call.arguments)

            print(f"  model asked for: {call.name}({arguments})")
            result = function(**arguments)

            tool_results.append({
                "type": "function_call_output",
                "call_id": call.call_id,       # this is what links result to request
                "output": json.dumps(result),
            })

        response = client.responses.create(
            input=tool_results,
            previous_response_id=response.id,
            extra_body=agent_reference,
        )

    print("\nAnswer:", response.output_text)


# --- Task 6 -----------------------------------------------------------------
def delete_the_agent(project):
    """Tidy up. Only ever deletes the agent this lab created."""
    print("\n=== Cleaning up ===")
    if not AGENT_NAME.startswith("acme-agent-"):
        raise ValueError("Refusing to delete anything that is not this lab's agent")
    project.agents.delete(agent_name=AGENT_NAME)
    print("deleted", AGENT_NAME)


# --- Main -------------------------------------------------------------------
if __name__ == "__main__":
    project = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )

    create_two_versions(project)
    ask_the_agent(project)
    version_with_tools = add_tools_to_the_agent(project)
    run_the_tool_loop(project, version_with_tools)

    # Uncomment when you have finished the lab:
    # delete_the_agent(project)

    print("\nDone.")
