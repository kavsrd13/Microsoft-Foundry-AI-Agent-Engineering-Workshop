"""Offline contract checks, not a Cosmos service test."""
import ast
import json
import runpy
import sys
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path
root = Path(__file__).parent
for path in root.rglob('*.py'):
    ast.parse(path.read_text(encoding='utf-8'))
policy = json.loads((root/'data/vector-policy.json').read_text())['vectorEmbeddings'][0]
assert policy['dimensions'] == 256 and policy['distanceFunction'] == 'cosine'
assert json.loads((root/'data/index-policy.json').read_text())['vectorIndexes'][0]['type'] == 'flat'
records = json.loads((root/'data/records.json').read_text())
assert len({row['id'] for row in records}) == len(records)
# Execute the actual save/read/cleanup scripts with an in-memory service fake.
# This proves arguments and ownership boundaries, not Cosmos persistence or TTL.
items = {}
current_user = 'tenant:user-a'
class FakeContainer:
    def __init__(self, name):
        self.name = name
    def upsert_item(self, item):
        items[(self.name, item['userId'], item['id'])] = dict(item)
    def read_item(self, item, partition_key):
        return items[(self.name, partition_key, item)]
    def delete_item(self, item, partition_key):
        del items[(self.name, partition_key, item)]

store = SimpleNamespace(container=FakeContainer, signed_in_partition=lambda: current_user)
with patch.dict(sys.modules, {'store': store}):
    runpy.run_path(str(root / 'src/save.py'))
    assert items[('sessions', current_user, 'session-1')]['ttl'] == 3600
    assert items[('sessions', current_user, 'preferences')]['ttl'] == 86400
    runpy.run_path(str(root / 'src/read.py'))
    current_user = 'tenant:user-b'
    try:
        runpy.run_path(str(root / 'src/read.py'))
    except KeyError:
        pass
    else:
        raise AssertionError('An unsaved identity must not recover another identity session')
    runpy.run_path(str(root / 'src/save.py'))
    for user in ['tenant:user-a', 'tenant:user-b']:
        for record in records:
            FakeContainer('vectors').upsert_item({**record, 'userId': user})
    runpy.run_path(str(root / 'cleanup.py'))
    assert len(items) == 5 and all(key[1] == 'tenant:user-a' for key in items)
print('PASS: syntax, vector policies, real save/read/cleanup calls against a fake, TTL values, isolated reads and current-user cleanup. Azure persistence, TTL expiry and vector ranking untested.')
