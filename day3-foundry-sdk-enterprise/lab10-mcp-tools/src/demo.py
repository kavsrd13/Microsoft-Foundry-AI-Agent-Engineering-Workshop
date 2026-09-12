"""Read-only MCP: https://learn.microsoft.com/azure/foundry/agents/how-to/tools/model-context-protocol"""
import json
import os
from pathlib import Path
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    load_dotenv(root / '.env')
    with DefaultAzureCredential() as credential, AIProjectClient(
        endpoint=os.environ['PROJECT_ENDPOINT'], credential=credential
    ) as project, project.get_openai_client() as client:
        tools = [{'type': 'mcp', 'server_label': 'microsoft_learn',
                  'server_url': 'https://learn.microsoft.com/api/mcp',
                  'allowed_tools': ['microsoft_docs_search'], 'require_approval': 'always'}]
        response = client.responses.create(model=os.environ['MODEL_DEPLOYMENT_NAME'],
            input='Search Microsoft Learn for Azure AI Search security filters.', tools=tools)
        state = root / 'data' / 'response-ids.json'
        ids = json.loads(state.read_text(encoding='utf-8')) if state.exists() else []
        ids.append(response.id)
        (root / 'data' / 'response-ids.json').write_text(json.dumps(ids), encoding='utf-8')
        while approvals := [item for item in response.output if item.type == 'mcp_approval_request']:
            decisions = []
            for item in approvals:
                print(item.server_label, item.name, item.arguments)
                permitted = item.server_label == 'microsoft_learn' and item.name == 'microsoft_docs_search'
                approved = permitted and input('Approve this public documentation query? [y/N] ').lower() == 'y'
                decisions.append({'type': 'mcp_approval_response',
                    'approval_request_id': item.id, 'approve': approved})
            response = client.responses.create(model=os.environ['MODEL_DEPLOYMENT_NAME'],
                previous_response_id=response.id, input=decisions, tools=tools)
            ids.append(response.id)
            (root / 'data' / 'response-ids.json').write_text(json.dumps(ids), encoding='utf-8')
        print(response.output_text)
        (root / 'data' / 'live-output.txt').write_text(response.output_text, encoding='utf-8')


if __name__ == '__main__':
    main()
