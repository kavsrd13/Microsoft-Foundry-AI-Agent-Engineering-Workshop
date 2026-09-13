import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
model_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")

# 2. Initialize the standard OpenAI client
openai_client = OpenAI(
     base_url=azure_openai_endpoint,
     api_key=api_key,
     default_headers={"api-key": api_key} # Required for Azure API key auth
)

def chat_with_model():
    print("--- Chatting with model using Responses API (Type 'quit' to exit) ---")
    last_response_id = None

    while True:
        input_text = input("\nYou: ")
        if input_text.lower() in ["quit", "exit"]:
            break

        try:
            # 3. Use the Responses API
            response = openai_client.responses.create(
                model=model_deployment,
                instructions="You are a helpful AI assistant that answers questions and provides information.",
                input=input_text,
                #previous_response_id=last_response_id, # Passes conversation history

            )

            print("Assistant:", response)
            #print("Full Response Object:", response)

            # Save the ID to maintain context in the next loop
            last_response_id = response.id

        except Exception as e:
            print(f"Error occurred: {e}")

if __name__ == "__main__":
    chat_with_model()