"""Offline teaching checks; no service execution."""
import ast
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    for path in (root / 'src').glob('*.py'):
        ast.parse(path.read_text(encoding='utf-8'))
    import runpy
    cosine = runpy.run_path(str(root / 'src/embeddings.py'))['cosine']
    assert abs(cosine([1,0], [1,0])-1) < 1e-9
    assert cosine([1,0], [0,1]) == 0
    assert (root / 'data/policy-page.png').is_file()
    print('PASS: cosine mechanics and bundled image; live model outputs not tested')


if __name__ == '__main__':
    main()
