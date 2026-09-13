"""Read a synthetic policy image. https://learn.microsoft.com/azure/ai-foundry/openai/how-to/responses"""
import base64
import os
from pathlib import Path
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv


def main() -> None:
    root = Path(__file__).resolve().parent
    load_dotenv()
    picture = base64.b64encode((root / 'policy-page.png').read_bytes()).decode()
    client = AIProjectClient(endpoint=os.environ['PROJECT_ENDPOINT'], credential=DefaultAzureCredential()).get_openai_client()
    response = client.responses.create(model=os.environ['VISION_DEPLOYMENT'], store=False,
        input=[{'role': 'user', 'content': [
            {'type': 'input_text', 'text': 'Read the leave entitlement table. Give both numbers and the page number; say if unclear.'},
            {'type': 'input_image', 'image_url': 'data:image/png;base64,' + picture}]}])
    print(response.output_text)


if __name__ == '__main__':
    main()
