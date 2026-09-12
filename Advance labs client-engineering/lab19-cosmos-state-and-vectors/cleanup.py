"""Deletes only this identity's fixed synthetic lab items, not containers."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))
from store import container, signed_in_partition

user = signed_in_partition()
for name, ids in [('sessions', ['session-1','preferences']), ('vectors',['bins','parking','library'])]:
    for item in ids:
        container(name).delete_item(item=item, partition_key=user)
print('Deleted this identity\'s lab items. Instructor removes dedicated resources after review.')
