"""GA application security filters. https://learn.microsoft.com/azure/search/search-document-level-access-overview"""
import argparse
import json
import os
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex, SimpleField, SearchableField
from azure.ai.projects import AIProjectClient
from dotenv import load_dotenv
from state import ROOT, state

def group_filter(groups: list[str]) -> str:
    # Trusted server-side membership only; escape OData literal characters.
    values = ','.join(g.replace("'", "''") for g in groups)
    return f"allowed_groups/any(g: search.in(g, '{values}'))" if groups else 'false'

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--answer', action='store_true', help='Send only authorised context to Foundry')
    parser.add_argument('--preview', action='store_true', help='Show the disabled native-ACL design note')
    args = parser.parse_args()
    if args.preview:
        print('PREVIEW: native ACL/RBAC 2026-08-01-preview requires a compatible source and index schema.')
        print('This GA package does not execute preview APIs. See data/native-acl-preview.md.')
        return
    load_dotenv(ROOT / '.env')
    credential = DefaultAzureCredential()
    name = state()['name']
    SearchIndexClient(os.environ['SEARCH_ENDPOINT'], credential).create_or_update_index(SearchIndex(name=name, fields=[
        SimpleField(name='id', type='Edm.String', key=True), SearchableField(name='content', type='Edm.String'),
        SimpleField(name='source', type='Edm.String'), SimpleField(name='page', type='Edm.Int32'),
        SimpleField(name='allowed_groups', type='Collection(Edm.String)', filterable=True)]))
    client = SearchClient(os.environ['SEARCH_ENDPOINT'], name, credential)
    docs = json.loads((ROOT / 'data/chunks.json').read_text(encoding='utf-8'))
    result = client.upload_documents(docs)
    assert all(item.succeeded for item in result), 'Document upload failed'
    print('Uploaded', len(docs), 'documents. Search indexing may take a few seconds; rerun if results are empty.')
    for identity, groups in [('Synthetic citizen', ['citizen-service']), ('Synthetic HR officer', ['hr-internal'])]:
        authorised = list(client.search('*', filter=group_filter(groups), top=1000))
        assert authorised, 'Wait for indexing, then rerun'
        assert all(set(d['allowed_groups']) & set(groups) for d in authorised)
        print(identity, 'authorised IDs:', [d['id'] for d in authorised])
        if args.answer:
            context = '\n'.join(f"[{d['source']} p{d['page']}] {d['content']}" for d in authorised)
            project = AIProjectClient(os.environ['PROJECT_ENDPOINT'], credential)
            response = project.get_openai_client().responses.create(model=os.environ['MODEL_DEPLOYMENT'], store=False,
                instructions='Answer from supplied context only. Cite source and page. Say if information is absent.',
                input='Summarise the policies I can access.\n'+context)
            print(response.output_text)
    unfiltered = list(client.search('*', top=1000))
    leaked = [d['id'] for d in unfiltered if 'citizen-service' not in d['allowed_groups']]
    assert leaked, 'Negative control requires at least one HR-only document'
    print('EXPECTED NEGATIVE CONTROL: omitted filter exposes HR-only IDs:', leaked)
    print('Synthetic fixture only. Never expose an unfiltered retrieval route in an application.')

if __name__ == '__main__':
    main()
