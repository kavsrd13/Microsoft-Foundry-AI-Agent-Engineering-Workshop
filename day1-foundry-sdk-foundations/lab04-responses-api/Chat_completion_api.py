import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT") or os.getenv("MODEL_DEPLOYMENT")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")



def main():
    endpoint_for_azure = endpoint.replace("/openai/v1", "")
    client = AzureOpenAI(
        azure_endpoint=endpoint_for_azure,
        api_key=subscription_key,
        api_version="2024-10-21",
    )

    print("Chat started. Type 'exit' to stop.\n")
    while True:
        user_text = input("You: ").strip()
        if user_text.lower() in {"exit", "quit"}:
            break

        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_text},
            ],
            max_completion_tokens=500,
        )

        assistant_text = response.choices[0].message.content or ""
        print(f"Assistant: {assistant_text}\n")

if __name__ == "__main__":
    main()