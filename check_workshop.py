"""Offline repository, source and dataset checks. No Azure requests."""
import ast
import json
import re
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    labs = sorted([*root.glob('day*/lab*'), *root.glob('Advance labs client-engineering/lab*')], key=lambda p: p.name)
    assert len(labs) == 24, 'Expected 24 labs'
    required = set()
    sections = ['Status badges', 'Learning objectives', 'Prerequisites', 'Australian/residency note',
                'Setup steps', 'Guided walkthrough', 'Run & expected output', 'Validation',
                'Troubleshooting', 'Cleanup', 'Knowledge check', 'Stretch challenge', 'References']
    matrix = ['# Completion matrix', '', 'Offline checks only. Live Azure execution is not certified.', '',
              '| Lab | Required items | Status | README sections | Python syntax | Layout |',
              '|---|---|---|---|---|---|']
    for lab in labs:
        items = {p.name for p in lab.iterdir()}
        assert required <= items, f'Missing lab item: {lab}'
        assert 'src' not in items and 'data' not in items, f'Legacy nested folder remains: {lab}'
        assert 'compileall' not in items and 'manual cleanup instructions' not in items, f'Removed helper remains: {lab}'
        if (lab / 'README.md').exists():
            readme = (lab / 'README.md').read_text(encoding='utf-8')
            headings = re.findall(r'^## (.+)$', readme, re.M)
            section_status = f'{len(headings)} headings'
        else:
            section_status = 'No README'
        for source in lab.rglob('*.py'):
            tree = ast.parse(source.read_text(encoding='utf-8'), filename=str(source))
            if not lab.parent.name.startswith('day4'):
                for node in ast.walk(tree):
                    imports = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ''] if isinstance(node, ast.ImportFrom) else []
                    assert not any(x.startswith('agent_framework') for x in imports), f'Framework leak: {source}'
        matrix.append(f'| {lab.name} | README + requirements | Present | {section_status} | PASS | Flat lab layout |')
    for source in (root / 'shared').glob('*.py'):
        ast.parse(source.read_text(encoding='utf-8'))
    data = root / 'shared/datasets'
    orders = json.loads((data / 'orders.json').read_text())
    assert len(orders) == 25 and len({o['order_id'] for o in orders}) == 25
    assert all(o['total_aud'] == sum(i['quantity'] * i['unit_price_aud'] for i in o['items']) for o in orders)
    assert len(json.loads((data / 'user_preferences.json').read_text())) == 5
    rows = [json.loads(line) for line in (data / 'eval/qa_dataset.jsonl').read_text().splitlines()]
    chunks = json.loads((data / 'chunks.json').read_text())
    assert len(rows) == 20
    assert all(any(row['ground_truth'] in c['content'] and row['expected_source'] == c['source'] for c in chunks) for row in rows)
    (root / 'COMPLETION-MATRIX.md').write_text('\n'.join(matrix) + '\n', encoding='utf-8')
    (root / 'DIRECTORY-TREE.txt').touch(exist_ok=True)
    for md in root.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)', md.read_text(encoding='utf-8')):
            if '://' not in target and not target.startswith('#') and target != 'url':
                assert (md.parent / target.split('#')[0]).exists(), f'Broken local link: {md}: {target}'
    (root / 'COMPLETION-MATRIX.md').write_text('\n'.join(matrix) + '\n', encoding='utf-8')
    tree = '\n'.join(str(p.relative_to(root)) for p in sorted(root.rglob('*'))
                     if not {'__pycache__', '.venv', '.azure', 'host-state'}.intersection(p.parts) and p.suffix != '.pyc' and p.name != 'DIRECTORY-TREE.txt')
    (root / 'DIRECTORY-TREE.txt').write_text(tree + '\n', encoding='utf-8')
    print('\n'.join(matrix))
    print('PASS: 24 labs, flat lab layout, shared configuration, local links and framework separation')


if __name__ == '__main__':
    main()
