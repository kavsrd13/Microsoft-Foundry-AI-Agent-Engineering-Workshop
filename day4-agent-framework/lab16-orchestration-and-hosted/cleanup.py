"""Remove local lab output only. https://learn.microsoft.com/agent-framework/overview/"""
from pathlib import Path
import shutil
def main() -> None:
    data = Path(__file__).parent / 'data'
    outputs = [data / name for name in ('result.json', 'session.json', 'timings.json')]
    existing = [p for p in outputs if p.exists()]
    host_state = data / 'host-state'
    if host_state.exists():
        assert host_state.resolve().parent == data.resolve(), 'Host state must remain inside this lab data folder'
        existing.append(host_state)
    if existing and input('Delete local generated output? Type yes: ') == 'yes':
        for path in existing:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink(missing_ok=True)
    print('Local cleanup complete. Hosted Azure resources: follow src/DEPLOY.md for the dedicated environment.')
if __name__ == '__main__':
    main()
