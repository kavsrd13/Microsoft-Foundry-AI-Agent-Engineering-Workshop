"""Classify synthetic text. https://learn.microsoft.com/azure/ai-services/content-safety/quickstart-text"""
import os
from pathlib import Path
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv


def main() -> None:
    load_dotenv()
    client = ContentSafetyClient(os.environ['CONTENT_SAFETY_ENDPOINT'], DefaultAzureCredential())
    result = client.analyze_text(AnalyzeTextOptions(text='Please help me find the library opening hours.'))
    for category in result.categories_analysis:
        print(category.category, category.severity)
    print('This benign smoke test is not a red-team or security certification.')


if __name__ == '__main__':
    main()
