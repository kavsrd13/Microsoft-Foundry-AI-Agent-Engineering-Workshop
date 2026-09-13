import os
from pathlib import Path
from dotenv import load_dotenv
from openai import AzureOpenAI



endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")


def main():
    if not endpoint or not deployment or not subscription_key:
        print("Missing one or more required env vars: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_API_KEY")
        return

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=subscription_key,
        api_version=api_version,
    )

    try:
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant.",
                },
                {
                    "role": "user",
                    "content": "I am going to Paris, what should I see?",
                },
            ],
            max_completion_tokens=500,
        )

        content = response.choices[0].message.content
        if content:
            print(content)
        else:
            print("Model returned no text content.")
            print(f"Finish reason: {response.choices[0].finish_reason}")
            print(response.model_dump_json(indent=2))
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()