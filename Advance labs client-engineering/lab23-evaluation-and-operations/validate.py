"""Offline teaching checks; no service execution."""
import ast
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    for path in (root / 'src').glob('*.py'):
        ast.parse(path.read_text(encoding='utf-8'))
    import runpy
    from datetime import datetime, timezone
    gate = runpy.run_path(str(root / 'src/gate.py'))['failures']
    report = {'evidence_kind':'live', 'candidate_revision':'test', 'case_count':20,
              'cases':[{}]*20, 'dataset_sha256':'0'*64, 'measured_at':datetime.now(timezone.utc).isoformat(),
              'metrics':{'recall_at_5':.9, 'groundedness':4.5, 'correctness':4.5, 'leakage_count':0}}
    assert not gate(report, 'test')
    assert gate(report, 'different-revision')
    assert gate(report | {'evidence_kind':'fixture'}, 'test')
    assert gate(report | {'metrics':report['metrics'] | {'groundedness':float('nan')}}, 'test')
    assert gate(report | {'metrics':report['metrics'] | {'leakage_count':1}}, 'test')
    assert gate(report | {'measured_at':'2000-01-01T00:00:00+00:00'}, 'test')
    print('PASS: gate unit tests use fabricated in-memory inputs only, not release evidence')


if __name__ == '__main__':
    main()
