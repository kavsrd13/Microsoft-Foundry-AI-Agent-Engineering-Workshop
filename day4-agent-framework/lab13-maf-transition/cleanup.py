"""Remove local lab output only. https://learn.microsoft.com/agent-framework/overview/"""
from pathlib import Path
def main() -> None:
    data = Path(__file__).parent / 'data'
    outputs = [data / name for name in ('result.json', 'session.json', 'timings.json')]
    existing = [p for p in outputs if p.exists()]
    if existing and input('Delete local generated output? Type yes: ') == 'yes':
        for path in existing:
            path.unlink(missing_ok=True)
    print('No cloud agents were created by the core demo. Local cleanup complete.')
if __name__ == '__main__':
    main()
