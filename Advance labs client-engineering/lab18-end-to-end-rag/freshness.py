from dotenv import load_dotenv
load_dotenv()

"""Reproducible source add/update/delete, without editing the supplied PDFs."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('action', choices=['add', 'update', 'delete'])
args = parser.parse_args()
manifest = ROOT / 'sources.json'
sources = [s for s in json.loads(manifest.read_text()) if s['file'] != 'service-hours.txt']
if args.action != 'delete':
    sources.append(dict(file='service-hours.txt', allowed_groups=['staff']))
    time = '4 pm' if args.action == 'add' else '6 pm'
    (ROOT / 'service-hours.txt').write_text('SYNTHETIC TRAINING RECORD\n\nThe service desk closes at ' + time + ' on Fridays.')
manifest.write_text(json.dumps(sources, indent=2))
print(args.action, 'source manifest changed; now run ingest.py then sync.py')
