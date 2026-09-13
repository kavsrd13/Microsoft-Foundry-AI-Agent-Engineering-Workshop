"""Lab 02 - Choose a model.

Measure two chat models on the same task, compare embedding sizes, work out
what it costs, and send a picture to a vision model.

Run it with:  python choose_a_model.py
"""

import base64
import json
import math
import os
import time

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# The question is the same for both models. One fact is in the notes, the
# other is not - we want to see which model admits it does not know.
COUNCIL_FACTS = (
    "Council facts: the library opens at 9 am on weekdays. "
    "Waste pickup days vary by address."
)
RESIDENT_QUESTION = "When does the library open, and when is my bin collected?"


# --- Task 2 -----------------------------------------------------------------
def compare_two_models(client):
    """Ask two deployments the same question and record what each one costs."""
    print("\n=== Comparing models ===")

    results = []
    deployment_names = os.environ["MODEL_DEPLOYMENTS"].split(",")

    for name in deployment_names:
        name = name.strip()

        started = time.perf_counter()
        response = client.responses.create(
            model=name,
            instructions=(
                "Use Australian English. Use only the facts you are given. "
                "If something is not in the facts, say you do not know."
            ),
            input=COUNCIL_FACTS + " Resident asks: " + RESIDENT_QUESTION,
        )
        seconds = time.perf_counter() - started

        result = {
            "deployment": name,
            "seconds": round(seconds, 2),
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "answer": response.output_text,
        }
        results.append(result)

        print(f"\n--- {name} ---")
        print(f"took {result['seconds']}s, "
              f"{result['input_tokens']} in / {result['output_tokens']} out tokens")
        print(result["answer"])

    return results


# --- Task 3 -----------------------------------------------------------------
def cosine_similarity(first, second):
    """How close are two vectors? 1.0 means identical direction, 0.0 unrelated."""
    dot_product = sum(a * b for a, b in zip(first, second))
    first_length = math.sqrt(sum(a * a for a in first))
    second_length = math.sqrt(sum(b * b for b in second))
    return dot_product / (first_length * second_length)


def compare_embedding_sizes(embeddings_client):
    """Embed the same sentences at two sizes and compare the rankings."""
    print("\n=== Comparing embedding sizes ===")

    with open("texts.json", encoding="utf-8") as file:
        texts = json.load(file)

    question = texts[0]
    candidates = texts[1:]

    for size in [256, 1536]:
        response = embeddings_client.embeddings.create(
            model=os.environ["EMBEDDING_DEPLOYMENT"],
            input=texts,
            dimensions=size,
        )
        vectors = [item.embedding for item in response.data]

        question_vector = vectors[0]
        scores = []
        for candidate_vector, candidate_text in zip(vectors[1:], candidates):
            score = cosine_similarity(question_vector, candidate_vector)
            scores.append((round(score, 4), candidate_text))
        scores.sort(reverse=True)

        bytes_per_vector = size * 4  # each number is a 4-byte float

        print(f"\n--- {size} dimensions ---")
        print(f"{bytes_per_vector} bytes per vector, "
              f"{response.usage.total_tokens} tokens charged")
        print(f"Question: {question}")
        for score, text in scores:
            print(f"  {score}  {text}")


# --- Task 4 -----------------------------------------------------------------
def estimate_cost(results, price_per_million_input, price_per_million_output, requests):
    """Turn measured token counts into a monthly-ish number."""
    print("\n=== What would this cost? ===")
    print(f"(using {price_per_million_input} per million input tokens, "
          f"{price_per_million_output} per million output, "
          f"{requests} requests)")

    for result in results:
        input_cost = result["input_tokens"] * price_per_million_input / 1_000_000
        output_cost = result["output_tokens"] * price_per_million_output / 1_000_000
        total = (input_cost + output_cost) * requests
        print(f"  {result['deployment']}: {round(total, 2)}")

    print("These rates are made up. Replace them with the real price for YOUR")
    print("model, and remember Search, storage and hosting are extra.")


# --- Task 5 -----------------------------------------------------------------
def read_a_picture(client):
    """Send an image to a vision-capable model."""
    print("\n=== Reading a picture ===")

    with open("policy-page.png", "rb") as file:
        encoded_image = base64.b64encode(file.read()).decode()

    response = client.responses.create(
        model=os.environ["VISION_DEPLOYMENT"],
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Read the leave table. Give both numbers and the page number.",
                    },
                    {
                        "type": "input_image",
                        "image_url": "data:image/png;base64," + encoded_image,
                    },
                ],
            }
        ],
    )

    print(response.output_text)


# --- Main -------------------------------------------------------------------
if __name__ == "__main__":
    credential = DefaultAzureCredential()

    project = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=credential,
    )
    client = project.get_openai_client()

    # Embeddings live on the Azure OpenAI resource, not the project endpoint.
    # We hand the OpenAI client an Entra token instead of an API key.
    token_provider = get_bearer_token_provider(
        credential, "https://cognitiveservices.azure.com/.default"
    )
    embeddings_client = OpenAI(
        base_url=os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/") + "/openai/v1/",
        api_key=token_provider,
    )

    results = compare_two_models(client)
    compare_embedding_sizes(embeddings_client)
    estimate_cost(results, price_per_million_input=1.0,
                  price_per_million_output=2.0, requests=1000)
    read_a_picture(client)

    print("\nDone.")
