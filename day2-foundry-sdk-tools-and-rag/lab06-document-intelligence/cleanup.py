"""Remove generated extraction outputs. https://learn.microsoft.com/azure/ai-services/document-intelligence/prebuilt/layout"""
from pathlib import Path
def main() -> None:
    data = Path(__file__).resolve().parent / 'data'
    outputs = [data / (p.stem + '.md') for p in (data / 'benefits').glob('*.pdf')]
    outputs.append(data / 'chunks.json')
    if input('Delete generated Markdown and chunks.json? Type yes: ') != 'yes':
        return
    for output in outputs:
        output.unlink(missing_ok=True)
    print('Local generated outputs removed. Document Intelligence service retained.')
if __name__ == '__main__':
    main()
