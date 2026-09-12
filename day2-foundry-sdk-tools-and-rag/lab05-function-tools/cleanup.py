"""Delete only recorded lab resources. https://learn.microsoft.com/azure/search/search-howto-create-search-index"""
import json
import os
from pathlib import Path
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
ROOT = Path(__file__).resolve().parent
def main() -> None:
    load_dotenv(ROOT / '.env')
    path = ROOT / 'data/resource-state.json'
    if not path.exists():
        print('Nothing recorded to delete.')
        return
    saved = json.loads(path.read_text(encoding='utf-8'))
    assert saved['name'].startswith('acme-lab05-demo-'), 'Unexpected resource name'
    if input('Delete only '+saved['name']+' resources? Type yes: ') != 'yes':
        return
    try:
        from azure.ai.projects import AIProjectClient
        client = AIProjectClient(os.environ['PROJECT_ENDPOINT'], DefaultAzureCredential())
        from openai import NotFoundError
        for response_id in saved.get('responses', []):
            try:
                client.get_openai_client().responses.delete(response_id)
            except NotFoundError:
                pass
        if 'version' in saved:
            client.agents.delete_version(saved['name'], saved['version'])
    except ResourceNotFoundError:
        pass
    path.unlink()
    print('Recorded lab resources removed; shared services and source data retained.')
if __name__ == '__main__':
    main()
