"""Lab 08 - Give the agent memory.

A model remembers nothing. Anything it "knows" about an earlier turn is
something your application handed it. This lab shows where that information
lives and how long it lasts.

Run it with:  python agent_memory.py
"""

import base64
import json
import os
import time

from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

DATABASE_NAME = "workshop-memory"
CONTAINER_NAME = "sessions"

ONE_HOUR = 3600
ONE_DAY = 86400


# --- Task 2 -----------------------------------------------------------------
def who_am_i(credential):
    """Work out who is signed in, from the token itself.

    We ask Azure Identity for a token and read the claims out of it. The
    important part is where this value comes FROM: the identity service, not
    from anything a caller typed.

    In a web app you would validate an incoming token properly first
    (Lab 13 does exactly that) and use the verified claims. Never take a
    user id from a request body.
    """
    token = credential.get_token("https://cosmos.azure.com/.default").token

    # A JWT is three base64 parts separated by dots. The middle one is the claims.
    claims_part = token.split(".")[1]
    padding = "=" * (-len(claims_part) % 4)
    claims = json.loads(base64.urlsafe_b64decode(claims_part + padding))

    tenant_id = claims["tid"]
    object_id = claims["oid"]
    return f"{tenant_id}:{object_id}"


# --- Task 3 -----------------------------------------------------------------
def save_a_conversation(container, user_id):
    """Write a conversation and a preference, with different lifetimes."""
    print("\n=== Saving ===")

    # Short-term: this conversation. Gone in an hour.
    container.upsert_item({
        "id": "conversation-1",
        "userId": user_id,             # this is the partition key
        "ttl": ONE_HOUR,
        "messages": [
            {"role": "user", "content": "My case reference is ACME-204."},
            {"role": "assistant", "content": "Noted, ACME-204."},
        ],
    })
    print(f"  saved conversation-1  (expires in {ONE_HOUR}s)")

    # Long-term: how this person likes to be answered. Survives the day.
    container.upsert_item({
        "id": "preferences",
        "userId": user_id,
        "ttl": ONE_DAY,
        "language": "Australian English",
        "style": "short answers",
    })
    print(f"  saved preferences     (expires in {ONE_DAY}s)")

    print("\nSame container, different lifetimes. That is the difference")
    print("between short-term and long-term memory in practice.")


def read_it_back(container, user_id):
    """Read the saved state. A point read needs the id AND the partition key."""
    print("\n=== Reading back ===")

    conversation = container.read_item(item="conversation-1", partition_key=user_id)
    preferences = container.read_item(item="preferences", partition_key=user_id)

    print("  conversation:", conversation["messages"][0]["content"])
    print("  style:       ", preferences["style"])
    return conversation, preferences


# --- Task 4 -----------------------------------------------------------------
def use_the_memory_in_a_prompt(conversation, preferences):
    """Storage does not give the model memory. Your code does.

    This is the step people skip. Saving to a database changes nothing until
    the application chooses what to put back into the next request.
    """
    print("\n=== Turning stored state into a prompt ===")

    history = ""
    for message in conversation["messages"]:
        history += f"{message['role']}: {message['content']}\n"

    instructions = (
        f"Answer in {preferences['language']} using {preferences['style']}.\n"
        f"Here is the conversation so far:\n{history}"
    )

    print(instructions)
    print("This text is what you would pass as `instructions` to the model.")
    print("Nothing is automatic - the database stores, the application remembers.")


# --- Task 5 -----------------------------------------------------------------
def watch_something_expire(container, user_id):
    """Save an item that lives for 15 seconds, then watch it disappear."""
    print("\n=== Watching a short-lived item expire ===")

    container.upsert_item({
        "id": "temporary-note",
        "userId": user_id,
        "ttl": 15,
        "note": "This will not exist for long.",
    })
    print("  saved temporary-note with ttl=15")

    item = container.read_item(item="temporary-note", partition_key=user_id)
    print("  reading it now:", item["note"])

    print("  waiting 20 seconds ...")
    time.sleep(20)

    try:
        container.read_item(item="temporary-note", partition_key=user_id)
        print("  still there - Cosmos removes expired items lazily, try again")
    except Exception as error:
        print(f"  gone: {type(error).__name__}")
        print("\nNo try/except hiding it in your own code either - an expired")
        print("session SHOULD be a visible 'not found', not a silent empty answer.")


# --- Task 6 -----------------------------------------------------------------
def why_a_partition_key_is_not_a_password(container, user_id):
    """A partition key routes data. It does not stop anyone reading it."""
    print("\n=== An important limitation ===")

    everything = list(container.query_items(
        query="SELECT c.id, c.userId FROM c",
        enable_cross_partition_query=True,
    ))

    print(f"  a cross-partition query returned {len(everything)} items")
    for item in everything:
        print(f"    {item['id']} belongs to {item['userId'][:20]}...")

    print("\n  Our credential can read every partition, including other users'.")
    print("  Partition keys make lookups fast and cheap. They are NOT access")
    print("  control. The trusted application decides which partition to read.")
    print("  Never give an end user this database role or these credentials.")


# --- Task 7 -----------------------------------------------------------------
def clean_up(container, user_id):
    print("\n=== Cleaning up ===")
    for item_id in ["conversation-1", "preferences", "temporary-note"]:
        try:
            container.delete_item(item=item_id, partition_key=user_id)
            print("  deleted", item_id)
        except Exception:
            print("  ", item_id, "was already gone")


# --- Main -------------------------------------------------------------------
if __name__ == "__main__":
    credential = DefaultAzureCredential()

    cosmos = CosmosClient(os.environ["COSMOS_ENDPOINT"], credential=credential)
    container = (cosmos
                 .get_database_client(DATABASE_NAME)
                 .get_container_client(CONTAINER_NAME))

    user_id = who_am_i(credential)
    print("Signed in as:", user_id)

    save_a_conversation(container, user_id)
    conversation, preferences = read_it_back(container, user_id)
    use_the_memory_in_a_prompt(conversation, preferences)
    watch_something_expire(container, user_id)
    why_a_partition_key_is_not_a_password(container, user_id)

    clean_up(container, user_id)

    print("\nDone.")
