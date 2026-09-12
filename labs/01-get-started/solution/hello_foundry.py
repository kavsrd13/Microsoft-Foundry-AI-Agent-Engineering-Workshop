"""Lab 01 - Get started with Microsoft Foundry.

The finished file. You build this up one task at a time in the exercise.
Run it with:  python hello_foundry.py
"""

import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

MODEL = os.environ["MODEL_DEPLOYMENT"]


# --- Task 2 -----------------------------------------------------------------
def show_deployments(project):
    """Print the models this project can use."""
    print("\n=== Models deployed in this project ===")
    for deployment in project.deployments.list():
        print(" -", deployment.name)


# --- Task 3 -----------------------------------------------------------------
def ask_one_question(client):
    """Send one question and print the answer."""
    print("\n=== One question, one answer ===")

    response = client.responses.create(
        model=MODEL,
        instructions="You are a council assistant. Answer briefly in Australian English.",
        input="A resident's bin was not collected. What should they do?",
    )

    print(response.output_text)


# --- Task 4 -----------------------------------------------------------------
def have_a_conversation(client):
    """Ask two questions that share one conversation, so the second remembers."""
    print("\n=== A conversation that remembers ===")

    # A conversation is a server-side resource. It is what carries the context.
    conversation = client.conversations.create()

    questions = [
        "My case reference is ACME-204. Please remember it.",
        "What case reference did I give you?",
    ]

    for question in questions:
        response = client.responses.create(
            model=MODEL,
            instructions="Answer briefly in Australian English.",
            conversation=conversation.id,
            input=question,
        )
        print("You:", question)
        print("Assistant:", response.output_text)
        print()


# --- Task 5 -----------------------------------------------------------------
def stream_an_answer(client):
    """Print the answer word by word, as the model produces it."""
    print("\n=== A streamed answer ===")

    stream = client.responses.create(
        model=MODEL,
        input="In two sentences, explain why a council assistant should cite its sources.",
        stream=True,
    )

    for event in stream:
        # A stream sends many kinds of event. We only want the text pieces.
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)

    print()


# --- Main -------------------------------------------------------------------
if __name__ == "__main__":
    project = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )
    client = project.get_openai_client()

    show_deployments(project)
    ask_one_question(client)
    have_a_conversation(client)
    stream_an_answer(client)

    print("\nDone.")
