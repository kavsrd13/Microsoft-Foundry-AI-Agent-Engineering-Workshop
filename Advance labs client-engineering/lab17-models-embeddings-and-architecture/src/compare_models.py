"""Compare deployed models on one task. https://learn.microsoft.com/azure/foundry/agents/quickstarts/responses-api"""
import json
import os
import time
from pathlib import Path
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    load_dotenv(root / '.env')
    client = AIProjectClient(endpoint=os.environ['PROJECT_ENDPOINT'], credential=DefaultAzureCredential()).get_openai_client()
    rows = []
    for model in os.environ['MODEL_DEPLOYMENTS'].split(','):
        start = time.perf_counter()
        response = client.responses.create(model=model.strip(), store=False,
            instructions='Use Australian English. Use only supplied facts; acknowledge missing information.',
            input='Synthetic council facts: library opens at 9 am weekdays. Waste pickup varies by address. '
                  'Resident asks: When does the library open and when is my bin collected?')
        row = {'deployment': model.strip(), 'seconds': round(time.perf_counter()-start, 3),
               'input_tokens': response.usage.input_tokens, 'output_tokens': response.usage.output_tokens,
               'answer': response.output_text}
        rows.append(row)
        print(json.dumps(row, indent=2))
    (root / 'data/model-results.json').write_text(json.dumps(rows, indent=2))


if __name__ == '__main__':
    main()
