"""Direct Responses call. https://learn.microsoft.com/azure/foundry/agents/quickstarts/responses-api"""
import os
from pathlib import Path
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
def main() -> None:
    load_dotenv(Path(__file__).resolve().parents[1] / '.env')
    with DefaultAzureCredential() as credential, AIProjectClient(endpoint=os.environ['PROJECT_ENDPOINT'], credential=credential) as project:
        with project.get_openai_client() as client:
            response = client.responses.create(model=os.environ['MODEL_DEPLOYMENT_NAME'], instructions='Use Australian English. Answer in two sentences.', input='Explain why a government service assistant should cite its sources.', store=False)
            print(response.output_text)
if __name__ == '__main__':
    main()
