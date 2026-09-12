"""Extract actual source files, then create page-linked chunks."""
import argparse
import json
import os
from pathlib import Path
import pymupdf
from chunks import documents

ROOT = Path(__file__).resolve().parents[1]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--strategy', choices=['fixed', 'paragraph'], default='fixed')
    parser.add_argument('--ocr', action='store_true')
    args = parser.parse_args()
    result = []
    sources = json.loads((ROOT / 'data/sources.json').read_text())
    for source in sources:
        path = ROOT / 'data' / source['file']
        if args.ocr:
            from dotenv import load_dotenv
            from azure.identity import DefaultAzureCredential
            from azure.ai.documentintelligence import DocumentIntelligenceClient
            load_dotenv(ROOT / '.env')
            client = DocumentIntelligenceClient(os.environ['DOCUMENT_INTELLIGENCE_ENDPOINT'], DefaultAzureCredential())
            with path.open('rb') as stream:
                analysis = client.begin_analyze_document('prebuilt-read', body=stream).result()
            pages = [(p.page_number, '\n\n'.join(line.content for line in p.lines)) for p in analysis.pages]
        elif path.suffix == '.txt':
            pages = [(1, path.read_text())]
        else:
            with pymupdf.open(path) as pdf:
                pages = [(i + 1, '\n\n'.join(block[4] for block in page.get_text('blocks'))) for i, page in enumerate(pdf)]
        for page, text in pages:
            assert text.strip(), f'No embedded text in {path.name}; use --ocr for scanned PDFs'
            result += documents(source['file'], page, text, source['allowed_groups'], args.strategy)
    (ROOT / 'data/chunks.json').write_text(json.dumps(result, indent=2))
    print(len(result), 'chunks; strategy:', args.strategy)
