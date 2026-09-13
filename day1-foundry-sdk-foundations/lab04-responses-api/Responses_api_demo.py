import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT") or os.getenv("MODEL_DEPLOYMENT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")

client = OpenAI(
    base_url=endpoint,
    api_key=api_key,
    default_headers={"api-key": api_key},
)

def chat_with_model():
    print("--- Responses API with OpenAI client (Type 'quit' to exit) ---")
    last_response_id = None

    while True:
        input_text = input("\nYou: ")
        if input_text.lower() in ["quit", "exit"]:
            break

        response = client.responses.create(
            model=deployment,
            input=input_text,
            previous_response_id=last_response_id,
        )

        print("Assistant:", response.output_text)
        last_response_id = response.id

if __name__ == "__main__":
    chat_with_model()