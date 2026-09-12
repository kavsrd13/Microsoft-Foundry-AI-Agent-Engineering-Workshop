"""Lab 09, part 2 - Call the hosted tool, then publish it over MCP.

Three ways to reach the same function:
  1. Straight HTTP, from your own code.
  2. Through an agent's tool-calling loop.
  3. Over MCP, so any MCP client can discover it.

Run it with:  python use_the_tool.py
(the Function host from part 1 must be running in another terminal)
"""

import base64
import json
import os
from urllib.parse import urlparse

import httpx
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

TOOL_URL = os.environ["ORDER_TOOL_URL"]


# --- Task 3 -----------------------------------------------------------------
def call_the_tool(order_id="ORD-001"):
    """Call the Function over HTTP, with whatever credential suits where we are."""
    url = TOOL_URL.rstrip("/") + "/" + order_id
    headers = {}

    if urlparse(url).hostname in ("localhost", "127.0.0.1"):
        # Local only. There is no platform to authenticate us, so we hand the
        # function the header it expects. This is a test fixture, NOT security.
        fake_principal = {"claims": [{"typ": "roles", "val": "Orders.Read"}]}
        encoded = base64.b64encode(json.dumps(fake_principal).encode()).decode()
        headers["X-MS-CLIENT-PRINCIPAL"] = encoded
    else:
        # Deployed. Ask Entra for a real token for this API.
        token = DefaultAzureCredential().get_token(os.environ["TOOL_SCOPE"]).token
        headers["Authorization"] = "Bearer " + token

    response = httpx.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    return response.json()


def try_the_tool_directly():
    print("\n=== Calling the tool over HTTP ===")
    order = call_the_tool("ORD-001")
    print(json.dumps(order, indent=2))


def try_it_without_permission():
    """Show that the role check actually does something."""
    print("\n=== What happens without the right role ===")

    url = TOOL_URL.rstrip("/") + "/ORD-001"

    no_header = httpx.get(url, timeout=20)
    print(f"  no principal at all      -> {no_header.status_code} (not authenticated)")

    wrong_role = {"claims": [{"typ": "roles", "val": "Something.Else"}]}
    encoded = base64.b64encode(json.dumps(wrong_role).encode()).decode()
    response = httpx.get(url, headers={"X-MS-CLIENT-PRINCIPAL": encoded}, timeout=20)
    print(f"  signed in, wrong role    -> {response.status_code} (not authorised)")

    right_role = {"claims": [{"typ": "roles", "val": "Orders.Read"}]}
    encoded_ok = base64.b64encode(json.dumps(right_role).encode()).decode()
    missing_url = TOOL_URL.rstrip("/") + "/ORD-999999"
    response = httpx.get(missing_url, headers={"X-MS-CLIENT-PRINCIPAL": encoded_ok},
                         timeout=20)
    print(f"  allowed, no such order   -> {response.status_code} (not found)")

    print("\n  401, 403 and 404 mean different things. Keep them different.")


# --- Task 4 -----------------------------------------------------------------
def let_the_agent_use_it(client):
    """The model asks for the tool; our code decides whether to call it."""
    print("\n=== Letting an agent use the tool ===")

    tool_schema = {
        "type": "function",
        "name": "get_order_status",
        "description": "Look up one order by its order ID, for example ORD-001.",
        "parameters": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
            "additionalProperties": False,
        },
        "strict": True,
    }

    question = "What is the status of ORD-001?"
    print("Question:", question)

    response = client.responses.create(
        model=os.environ["MODEL_DEPLOYMENT"],
        input=question,
        tools=[tool_schema],
    )

    for item in response.output:
        if item.type != "function_call":
            continue

        # We check the name ourselves before running anything.
        if item.name != "get_order_status":
            print("  refusing to run", item.name)
            continue

        arguments = json.loads(item.arguments)
        print(f"  model asked for: {item.name}({arguments})")

        result = call_the_tool(arguments["order_id"])

        response = client.responses.create(
            model=os.environ["MODEL_DEPLOYMENT"],
            previous_response_id=response.id,
            input=[{
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": json.dumps(result),
            }],
        )

    print("\nAnswer:", response.output_text)
    print("\nThe model never saw the token and never ran any Python.")


# --- Main -------------------------------------------------------------------
if __name__ == "__main__":
    try_the_tool_directly()
    try_it_without_permission()

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )
    client = OpenAI(
        base_url=os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/") + "/openai/v1/",
        api_key=token_provider,
    )
    let_the_agent_use_it(client)

    print("\nDone. Next: mcp_server.py and mcp_client.py.")
