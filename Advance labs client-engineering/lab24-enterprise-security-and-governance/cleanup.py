"""Delete only generated local lab reports."""
from pathlib import Path


def main() -> None:
    data = Path(__file__).resolve().parent / 'data'
    files = [data / name for name in ['redteam-results.json'] if (data / name).exists()]
    if files and input('Delete these local reports? ' + ', '.join(p.name for p in files) + ' [y/N] ').lower() == 'y':
        for path in files:
            path.unlink(missing_ok=True)
    print('Local cleanup finished. Shared Azure resources were not removed.')


if __name__ == '__main__':
    main()
