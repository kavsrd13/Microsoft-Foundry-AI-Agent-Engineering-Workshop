"""Owned artefact cleanup: https://learn.microsoft.com/azure/foundry/agents/quickstarts/responses-api"""
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    names = ['live-retrieval.json']
    existing = [root / 'data' / name for name in names if (root / 'data' / name).exists()]
    if not existing:
        print('Nothing to remove.')
        return
    print('Remove these lab outputs:', ', '.join(path.name for path in existing))
    if input('Delete these owned outputs? [y/N] ').lower() != 'y':
        return
    
    for path in existing:
        path.unlink(missing_ok=True)
    print('Lab outputs removed. Shared infrastructure retained.')


if __name__ == '__main__':
    main()
