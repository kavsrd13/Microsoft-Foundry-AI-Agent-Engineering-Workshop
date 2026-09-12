"""Actual Search outputs are scored; relevant sources never enter the query."""
import json
import hashlib
from datetime import datetime, timezone
from clients import ROOT
from query import retrieve
from chunks import metrics

dataset = (ROOT / 'data/questions.json').read_bytes()
cases = json.loads(dataset)
for mode in ['keyword', 'vector', 'hybrid', 'semantic']:
    scores = []
    evidence = []
    for case in cases:
        hits = retrieve(case['question'], case['groups'], mode)
        ranked = list(dict.fromkeys(hit['source'] for hit in hits))[:5]
        score = metrics(ranked, case['relevant_sources'], k=5)
        scores.append(score)
        evidence.append(dict(question=case['question'], expected_ids=case['relevant_sources'], retrieved_ids=ranked))
        print(mode, case['question'], score)
    print(mode, 'MEAN', {key: round(sum(s[key] for s in scores) / len(scores), 3) for key in scores[0]})
    report = dict(evidence_kind='live', measured_at=datetime.now(timezone.utc).isoformat(), mode=mode,
        unit='unique source documents', k=5, case_count=len(cases), dataset_sha256=hashlib.sha256(dataset).hexdigest(),
        metrics=dict(recall_at_5=sum(s['recall'] for s in scores) / len(scores),
            precision_at_5=sum(s['precision'] for s in scores) / len(scores),
            mrr=sum(s['reciprocal_rank'] for s in scores) / len(scores)), cases=evidence)
    (ROOT / f'data/retrieval-{mode}.json').write_text(json.dumps(report, indent=2))
    if mode == 'semantic':
        (ROOT / 'data/retrieval-report.json').write_text(json.dumps(report, indent=2))
