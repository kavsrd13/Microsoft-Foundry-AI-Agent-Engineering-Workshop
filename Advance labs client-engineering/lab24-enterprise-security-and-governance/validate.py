"""Offline teaching checks; no service execution."""
import ast
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    for path in (root / 'src').glob('*.py'):
        ast.parse(path.read_text(encoding='utf-8'))
    import json
    controls = json.loads((root / 'data/control-evidence.json').read_text())
    assert len(controls) >= 10
    assert all(c['status'] == 'pending' for c in controls), 'Bundled controls must not claim tenant verification'
    assert len(json.loads((root / 'data/probes.json').read_text())) == 4
    print('PASS: evidence template and probes; tenant controls remain pending')


if __name__ == '__main__':
    main()
