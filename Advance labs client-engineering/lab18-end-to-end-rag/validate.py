"""Offline invariants only: no Azure requests or simulated live metrics."""
import json
import sys
import runpy
import tempfile
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path
import pymupdf

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / 'src'))
from chunks import documents, manifest, changes, metrics, group_filter, split

before = documents('policy.pdf', 1, 'A' * 1200, ['staff'], 'fixed')
after = documents('policy.pdf', 1, 'Updated policy', ['hr'], 'fixed')
upserts, deletes = changes(manifest(before), manifest(after))
assert upserts == [after[0]['id']] and len(deletes) == len(before) - 1
assert changes(manifest(after), manifest(after)) == ([], [])
assert changes(manifest(after), {}) == ([], [after[0]['id']])
assert changes({}, manifest(after)) == ([after[0]['id']], [])
assert all(d['source'] == 'policy.pdf' and d['page'] == 1 and d['allowed_groups'] == ['staff'] for d in before)
assert split('A' * 600, 'fixed')[0][-80:] == split('A' * 600, 'fixed')[1][:80]
assert len(split('First paragraph\n\nSecond paragraph', 'paragraph')) == 1
assert group_filter([]) == 'false' and "o''hara" in group_filter(["o'hara"])
assert metrics(['wrong', 'right', 'right'], ['right'], 5) == dict(precision=0.2, recall=1.0, reciprocal_rank=0.5)
assert metrics([], ['right'], 5) == dict(precision=0.0, recall=0.0, reciprocal_rank=0)
for source in json.loads((ROOT / 'data/sources.json').read_text()):
    path = ROOT / 'data' / source['file']
    if path.suffix == '.pdf' and not path.name.startswith('scanned'):
        with pymupdf.open(path) as pdf:
            assert all(page.get_text().strip() for page in pdf)
assert len(json.loads((ROOT / 'data/questions.json').read_text())) == 3
# Execute the real sync script against a recording fake. Failed writes must not
# advance the checkpoint; the next run must repeat unfinished work.
with tempfile.TemporaryDirectory() as folder:
    sandbox = Path(folder)
    (sandbox / 'data').mkdir()
    checkpoint = sandbox / 'data/lab18-test-manifest.json'
    checkpoint.write_text(json.dumps(manifest(before)))
    (sandbox / 'data/chunks.json').write_text(json.dumps(after))
    uploads, removals = [], []
    def upload(batch):
        uploads.extend(batch)
        return [SimpleNamespace(succeeded=True)]
    def reject_delete(batch):
        return [SimpleNamespace(succeeded=False)]
    def delete(batch):
        removals.extend(batch)
        return [SimpleNamespace(succeeded=True)]
    search = SimpleNamespace(upload_documents=upload, delete_documents=reject_delete)
    clients = SimpleNamespace(ROOT=sandbox, search=search, embedding=lambda text: [0.0] * 1536, name='lab18-test')
    with patch.dict(sys.modules, {'clients': clients}):
        try:
            runpy.run_path(str(ROOT / 'src/sync.py'))
        except RuntimeError:
            pass
        else:
            raise AssertionError('A rejected deletion must fail the sync')
        assert json.loads(checkpoint.read_text()) == manifest(before)
        search.delete_documents = delete
        runpy.run_path(str(ROOT / 'src/sync.py'))
        assert json.loads(checkpoint.read_text()) == manifest(after)
        assert {item['id'] for item in removals} == set(deletes)
        assert len(uploads) == 2 and all(len(item['vector']) == 1536 for item in uploads)
        runpy.run_path(str(ROOT / 'src/sync.py'))
        assert len(uploads) == 2  # no-op does not incur another embedding/upload
        assert not checkpoint.with_suffix('.tmp').exists()
print('PASS: add/update/delete/no-op, failed-write checkpoint recovery, stale chunk removal, ACL inheritance, overlap, deny-empty, metrics and PDF text. Offline fakes only; no Azure requests.')
