"""Local evidence checks; https://learn.microsoft.com/azure/foundry/observability/how-to/evaluate-agent"""
import argparse
import ast
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--live', action='store_true', help='Check saved output after a live run')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    checks = {}
    for path in (root / 'src').glob('*.py'):
        try:
            ast.parse(path.read_text(encoding='utf-8'))
            checks[path.name + ' syntax'] = True
        except SyntaxError:
            checks[path.name + ' syntax'] = False
    checks['environment template'] = (root / '.env.example').is_file()
    if root.name.startswith('lab11'):
        path = root / 'data' / 'qa_dataset.jsonl'
        rows = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()] if path.exists() else []
        checks['20 labelled source-backed examples'] = len(rows) == 20 and all(
            all(row.get(key) for key in ['query', 'ground_truth', 'context', 'expected_source']) for row in rows)
    if args.live:
        evidence = root / 'data' / 'live-retrieval.json'
        checks['saved live artefact exists and is nonempty'] = evidence.is_file() and evidence.stat().st_size > 0
        if root.name.startswith('lab11') and evidence.exists():
            results = json.loads(evidence.read_text(encoding='utf-8'))
            checks['all 20 rows evaluated with metrics'] = len(results) == 20 and all(row.get('metrics') for row in results)
        if root.name.startswith('lab12'):
            print('Also confirm this trace ID in Application Insights; local output is not ingestion proof.')
    for name, passed in checks.items():
        print(('PASS' if passed else 'FAIL') + ' ' + name)
    print('Local checks only; Azure execution and regional support are separate checks.')
    raise SystemExit(0 if all(checks.values()) else 1)


if __name__ == '__main__':
    main()
