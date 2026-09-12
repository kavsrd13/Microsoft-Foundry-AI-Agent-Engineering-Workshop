"""Report unverified production controls; never convert pending into pass automatically."""
import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence', type=Path, default=Path(__file__).resolve().parents[1] / 'data/control-evidence.json')
    args = parser.parse_args()
    controls = json.loads(args.evidence.read_text(encoding='utf-8'))
    pending = [c['control'] for c in controls if c['status'] != 'verified' or not all(c.get(k) for k in ['owner', 'evidence', 'checked_at'])]
    for name in pending:
        print('PENDING:', name)
    print('Evidence fields are complete; human review required.' if not pending else 'Not production-ready: evidence is incomplete.')
    raise SystemExit(1 if pending else 0)


if __name__ == '__main__':
    main()
