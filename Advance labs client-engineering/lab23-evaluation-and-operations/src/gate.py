"""Fail a release on missing, stale or failing evidence. https://learn.microsoft.com/azure/foundry/observability/how-to/evaluate-agent"""
import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path


def failures(report: dict, revision: str) -> list[str]:
    problems = []
    if report.get('evidence_kind') != 'live':
        problems.append('A live report is required; a teaching fixture cannot approve a release')
    if report.get('candidate_revision') != revision:
        problems.append('Report revision does not match the candidate')
    if report.get('case_count', 0) < 20 or len(report.get('cases', [])) != report.get('case_count'):
        problems.append('At least 20 completed cases are required')
    if len(report.get('dataset_sha256', '')) != 64:
        problems.append('Dataset digest missing')
    measured = datetime.fromisoformat(report.get('measured_at', '1970-01-01T00:00:00+00:00'))
    age = (datetime.now(timezone.utc) - measured).total_seconds()
    if not 0 <= age <= 86400:
        problems.append('Evidence must be from the last 24 hours')
    for name, low, high in [('recall_at_5', .8, 1), ('groundedness', 4, 5), ('correctness', 4, 5), ('leakage_count', 0, 0)]:
        value = report.get('metrics', {}).get(name)
        if type(value) not in [int, float] or not math.isfinite(value) or not low <= value <= high:
            problems.append(f'{name} must be between {low} and {high}')
    return problems


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--revision', required=True)
    args = parser.parse_args()
    problems = failures(json.loads(args.report.read_text(encoding='utf-8')), args.revision)
    for problem in problems:
        print('FAIL:', problem)
    print('GATE FAILED' if problems else 'GATE PASSED for the measured reference RAG scope only')
    raise SystemExit(1 if problems else 0)


if __name__ == '__main__':
    main()
