"""Owned artefact cleanup: https://learn.microsoft.com/azure/foundry/agents/quickstarts/responses-api"""
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    names = ['live-output.txt', 'response-ids.json']
    existing = [root / 'data' / name for name in names if (root / 'data' / name).exists()]
    if not existing:
        print('Nothing to remove.')
        return
    print('Remove these lab outputs:', ', '.join(path.name for path in existing))
    if input('Delete these owned outputs? [y/N] ').lower() != 'y':
        return
    import json
    import os
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential
    from dotenv import load_dotenv
    from openai import NotFoundError
    load_dotenv(root / '.env')
    state = root / 'data' / 'response-ids.json'
    if state.exists():
        with DefaultAzureCredential() as credential, AIProjectClient(endpoint=os.environ['PROJECT_ENDPOINT'], credential=credential) as project, project.get_openai_client() as client:
            for response_id in json.loads(state.read_text(encoding='utf-8')):
                try:
                    client.responses.delete(response_id)
                except NotFoundError:
                    pass
    for path in existing:
        path.unlink(missing_ok=True)
    print('Lab outputs removed. Shared infrastructure retained.')


if __name__ == '__main__':
    main()
