"""Layout to Markdown. https://learn.microsoft.com/azure/ai-services/document-intelligence/prebuilt/layout?view=doc-intel-4.0.0"""
import json
import os
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from state import ROOT

def main() -> None:
    load_dotenv()
    client = DocumentIntelligenceClient(os.environ['DOCUMENT_INTELLIGENCE_ENDPOINT'], DefaultAzureCredential(), api_version='2024-11-30')
    chunks = []
    for pdf in sorted((ROOT / 'benefits').glob('*.pdf')):
        with pdf.open('rb') as document:
            result = client.begin_analyze_document('prebuilt-layout', body=document,
                content_type='application/octet-stream', output_content_format='markdown',
                string_index_type='unicodeCodePoint').result()
        (ROOT / (pdf.stem + '.md')).write_text(result.content, encoding='utf-8')
        # Service spans refer to the returned Markdown, preserving table markup.
        for page in result.pages:
            content = ''.join(result.content[s.offset:s.offset+s.length] for s in page.spans)
            for start in range(0, len(content), 1500):
                chunks.append({'id': f'{pdf.stem}-{page.page_number}-{start}',
                    'content': content[start:start+1800], 'source': pdf.name, 'page': page.page_number,
                    'allowed_groups': ['hr-internal'] if 'leave' in pdf.name else ['citizen-service', 'hr-internal']})
        print(pdf.name, len(result.pages), 'pages; Markdown saved')
    (ROOT / 'chunks.json').write_text(json.dumps(chunks, indent=2), encoding='utf-8')
    print(len(chunks), 'chunks saved. Fixed windows may split a table; compare with the full Markdown.')

if __name__ == '__main__':
    main()
