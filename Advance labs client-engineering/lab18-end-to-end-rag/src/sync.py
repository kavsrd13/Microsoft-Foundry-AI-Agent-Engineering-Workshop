"""Re-embed changed chunks and remove obsolete chunks, including removed sources."""
import json
from chunks import manifest, changes
from clients import ROOT, search, embedding, name

docs = json.loads((ROOT / 'data/chunks.json').read_text())
state = ROOT / 'data' / f'{name}-manifest.json'
previous = json.loads(state.read_text()) if state.exists() else {}
current = manifest(docs)
upserts, deletes = changes(previous, current)
for doc in docs:
    if doc['id'] in upserts:
        doc['vector'] = embedding(doc['content'])
        results = search.upload_documents([doc])
        if not all(r.succeeded for r in results):
            raise RuntimeError('Search rejected an upload; checkpoint unchanged. Rerun sync.')
if deletes:
    results = search.delete_documents([{'id': key} for key in deletes])
    if not all(r.succeeded for r in results):
        raise RuntimeError('Search rejected a deletion; checkpoint unchanged. Rerun sync.')
# Save only after Search accepts every action. Repeat safely after an interrupted run.
temporary = state.with_suffix('.tmp')
temporary.write_text(json.dumps(current, indent=2))
temporary.replace(state)
print('Uploaded', len(upserts), 'deleted', len(deletes), 'unchanged', len(current) - len(upserts))
