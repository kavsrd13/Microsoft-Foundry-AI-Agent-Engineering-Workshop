"""Model deployment and processing geography. https://learn.microsoft.com/azure/foundry/how-to/deploy-models-openai"""
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

def main() -> None:
    load_dotenv()
    project = AIProjectClient(endpoint=os.environ["PROJECT_ENDPOINT"], credential=DefaultAzureCredential())
    print("Project:", os.environ["PROJECT_ENDPOINT"])
    deployments = list(project.deployments.list())
    for deployment in deployments:
        print(deployment.as_dict())
    assert deployments, "Deploy a supported chat model in this project first."


if __name__ == "__main__":
    main()
