"""Exercises 05-08 — Tools and the RAG pipeline (Day 2)."""

from .day1 import SETUP_PS

LAB05 = {
    "num": "05",
    "slug": "05-function-tools",
    "short": "Function calling and tool dispatch",
    "group": "Day 2 — Tools and retrieval",
    "track": "Foundry SDK",
    "module_tags": ["Module 3", "Module 6"],
    "title": "Give an agent tools and run the function-calling loop",
    "minutes": 45,
    "lab_path": "day2-foundry-sdk-tools-and-rag/lab05-function-tools",
    "env_note": "`azure-ai-projects==2.6.0`",
    "blurb": "Declare strict tool schemas, dispatch the model's calls to ordinary Python, and return results by "
             "call ID.",
    "intro": [
        "In this exercise you give an agent three tools over a synthetic order dataset and run the full "
        "function-calling loop by hand, so that nothing about it stays magical.",
        "The single most important idea here is that **the model never executes your code**. It emits a "
        "structured request naming a function and its arguments. Your application decides whether to honour "
        "that request, runs the function under its own identity, and returns the result. Every authorisation "
        "decision in Exercises 08, 20 and 21 depends on understanding that boundary correctly.",
    ],
    "objectives": [
        "Write strict JSON tool schemas and attach them to an agent version.",
        "Dispatch a returned `function_call` to a real Python function.",
        "Return a `function_call_output` correlated by `call_id`.",
        "Explain which component executes a tool and which identity authorises it.",
    ],
    "prereqs": [
        "A Foundry project and a working chat deployment.",
        "A project role that permits creating agents (the same role used in Exercise 03).",
    ],
    "sections": [
        {
            "h2": "Set up and inspect the data",
            "steps": [
                [{"code": "cd day2-foundry-sdk-tools-and-rag/lab05-function-tools\n" + SETUP_PS,
                  "lang": "powershell"}],
                ["Fill in `.env` — this exercise needs only `PROJECT_ENDPOINT` and `MODEL_DEPLOYMENT` — then:",
                 {"code": "python validate.py", "lang": "powershell"},
                 {"ok": "`PASS OFFLINE: 25 synthetic orders loaded` confirms the fixture is intact."}],
                ["Open `data/orders.json`. Each of the 25 synthetic orders has an `order_id`, `customer_name`, "
                 "`status`, `region`, a line-item list and a `total_aud`. No real customer data is present, and "
                 "none should ever be added."],
            ],
        },
        {
            "h2": "Read the tool declarations",
            "intro": ["Open `src/demo.py`. There are two distinct halves: three plain Python functions, and the "
                      "schemas that describe them to the model."],
            "steps": [
                ["The functions are ordinary code with no SDK involvement at all:",
                 {"code": """def get_order_status(order_id: str) -> dict:
    orders = json.loads((ROOT / 'data/orders.json').read_text(encoding='utf-8'))
    return next((o for o in orders if o['order_id'] == order_id), {'error': 'Order not found'})""",
                  "lang": "python"}],
                ["The schemas describe *names and argument types only*. The model receives this, never the "
                 "function body:",
                 {"code": """FunctionTool(
    name=name,
    description=name.replace('_', ' '),
    strict=True,
    parameters={'type': 'object',
                'properties': {argument: {'type': 'string'}},
                'required': [argument],
                'additionalProperties': False})""", "lang": "python"},
                 {"note": "`strict=True` together with `additionalProperties: False` constrains the model to "
                          "the exact argument shape you declared. Without it you must defend against "
                          "unexpected keys in your dispatch code."}],
                ["The tools are attached to an **agent version**, so the tool list is part of the versioned "
                 "definition rather than a per-request detail. The created version number is saved into "
                 "`data/resource-state.json` and reused on later runs."],
            ],
        },
        {
            "h2": "Run the tool loop",
            "intro": ["The loop is the part worth reading twice. It repeats until the model stops asking for tools."],
            "steps": [
                ["Run the demo:",
                 {"code": "python src/demo.py", "lang": "powershell"},
                 "Expect a few `Tool: ...` lines showing each function and its real result, followed by a "
                 "natural-language answer that uses those facts."],
                ["Trace the four stages in the source:",
                 {"bullets": [
                     "The model returns output items; the application filters for `type == 'function_call'`.",
                     "For each call, the application looks the name up in its **own** dictionary of permitted "
                     "functions and invokes it. A name that is not in that dictionary is never executed.",
                     "Each result is wrapped as a `function_call_output` carrying the original `call_id`.",
                     "Those outputs are sent back with `previous_response_id`, and the loop repeats.",
                 ]},
                 {"code": """outputs.append({'type': 'function_call_output',
                'call_id': call.call_id,
                'output': json.dumps(result)})""", "lang": "python"}],
                ["The `call_id` is what correlates a result with the request that asked for it. When the model "
                 "requests several tools at once, this is the only thing keeping the answers straight — not the "
                 "order, and not the function name."],
                ["Notice the nine-minute guard:",
                 {"code": """if time.monotonic() - started > 540:
    raise TimeoutError('Tool loop exceeded nine-minute classroom budget; start a new response.')""",
                  "lang": "python"},
                 "A tool loop is a loop, and a badly instructed model can keep asking. A bound is a design "
                 "requirement, not a workaround."],
            ],
        },
        {
            "h2": "Experiment with the boundary",
            "steps": [
                ["Ask about an order that does not exist. Edit the input string in `src/demo.py` to reference "
                 "`ACME-99999` and run again. The function returns `{'error': 'Order not found'}`, and the "
                 "model should report that rather than inventing a status.",
                 {"tip": "This is a small but real grounding test. A model that fabricates a status here would "
                         "fabricate one in production."}],
                ["Remove one entry from the `functions` dictionary while leaving its schema in the tool list. "
                 "The model can now request a tool the application refuses to dispatch, and you get a `KeyError`. "
                 "In production that is a rejection path you write deliberately — see Exercise 20, where the "
                 "equivalent check returns HTTP 403.",
                 "Restore the dictionary afterwards."],
                ["Answer in your notes: if these functions read a live records system rather than a JSON file, "
                 "**whose** identity would the query run under? The application's — not the end user's. "
                 "Exercise 21 is where that distinction gets solved properly."],
            ],
        },
    ],
    "knowledge_check": [
        {"q": "Who executes a Python tool function?",
         "options": ["A. The model", "B. The application", "C. Azure AI Search"],
         "answer": "B",
         "why": "The model only emits a structured request. Your code chooses whether to honour it and runs it "
                "under its own identity."},
        {"q": "What correlates a tool result with the request that asked for it?",
         "options": ["A. `call_id`", "B. The customer name", "C. The order in which results are returned"],
         "answer": "A",
         "why": "With parallel tool calls, nothing else is reliable."},
        {"q": "What does the model receive about a tool?",
         "options": ["A. The function's source code", "B. A vector of the function",
                     "C. Its name, description and argument schema"],
         "answer": "C",
         "why": "Declaring a schema is not hosting. Exercise 20 makes the execution host an explicitly separate, "
                "authenticated service."},
    ],
    "summary": [
        "You declared strict tool schemas, attached them to an agent version, and ran the function-calling loop "
        "manually: detect calls, dispatch to permitted functions, return results by `call_id`, repeat.",
        "The boundary you practised here — model proposes, application authorises and executes — is the same "
        "boundary enforced with HTTP status codes in Exercise 20 and with validated user identity in Exercise 21.",
    ],
    "cleanup": [
        {"code": "python cleanup.py", "lang": "powershell"},
        "This removes only the agent recorded in `data/resource-state.json`, whose name begins with "
        "`acme-lab05-demo-`. Shared project resources are left alone.",
    ],
    "refs": [
        ("Function calling", "https://learn.microsoft.com/azure/foundry/agents/how-to/tools/function-calling"),
    ],
}


LAB06 = {
    "num": "06",
    "slug": "06-document-intelligence",
    "short": "Extract documents with Document Intelligence",
    "group": "Day 2 — Tools and retrieval",
    "track": "Foundry SDK",
    "module_tags": ["Module 4"],
    "title": "Extract PDF layout as Markdown and build a page-linked chunk set",
    "minutes": 45,
    "lab_path": "day2-foundry-sdk-tools-and-rag/lab06-document-intelligence",
    "env_note": "`azure-ai-documentintelligence==1.0.2`, API version `2024-11-30`",
    "blurb": "Run the prebuilt-layout model, keep table markup, preserve physical page numbers, and chunk with "
             "overlap.",
    "intro": [
        "This is the first step of the retrieval pipeline the client identified as their highest-value use "
        "case: turning documents into text that can be indexed, cited and permission-filtered.",
        "The interesting part is not the API call. It is what you must preserve while extracting: table "
        "structure, physical page numbers so answers can be cited, and the access labels that will later decide "
        "who may see each passage.",
    ],
    "objectives": [
        "Extract document layout as Markdown with the `prebuilt-layout` model.",
        "Map returned content back to the physical PDF page it came from.",
        "Produce overlapping chunks with source, page and permission metadata.",
        "Recognise what a naive fixed-width chunker destroys.",
    ],
    "prereqs": [
        "An Azure AI Document Intelligence resource, and **Cognitive Services User** on it.",
        "Python 3.11 and Azure CLI signed in.",
    ],
    "before_extra": [
        {"note": "This exercise needs no Foundry project and no model deployment. Its `.env` contains only "
                 "`DOCUMENT_INTELLIGENCE_ENDPOINT`."},
    ],
    "sections": [
        {
            "h2": "Set up",
            "steps": [
                [{"code": "cd day2-foundry-sdk-tools-and-rag/lab06-document-intelligence\n" + SETUP_PS,
                  "lang": "powershell"}],
                ["Set `DOCUMENT_INTELLIGENCE_ENDPOINT` in `.env`, then:",
                 {"code": "python validate.py", "lang": "powershell"},
                 {"ok": "`PASS OFFLINE: independent PDF inputs present` confirms the three synthetic PDFs are "
                        "in `data/benefits/`."}],
                ["Open the three PDFs in `data/benefits/`. They are synthetic Acme policies: a code of conduct, "
                 "a leave policy and a travel policy. The leave policy contains a table — watch what happens to "
                 "it."],
            ],
        },
        {
            "h2": "Extract layout as Markdown",
            "intro": ["Open `src/demo.py`. The service call is four lines; everything else is about preserving "
                      "provenance."],
            "steps": [
                ["The analysis requests Markdown output explicitly:",
                 {"code": """result = client.begin_analyze_document(
    'prebuilt-layout',
    body=document,
    content_type='application/octet-stream',
    output_content_format='markdown',
    string_index_type='unicodeCodePoint',
).result()""", "lang": "python"},
                 {"bullets": [
                     "`prebuilt-layout` returns structure — headings, tables, reading order — not just a flat "
                     "text dump.",
                     "`output_content_format='markdown'` keeps tables as pipe tables, so a table survives into "
                     "the indexed text instead of collapsing into loose words.",
                     "`string_index_type='unicodeCodePoint'` makes the returned character offsets match Python "
                     "string indexing, which matters for the next step.",
                 ]}],
                ["Run it:",
                 {"code": "python src/demo.py", "lang": "powershell"},
                 "Expect a page count per PDF, a saved `.md` file per PDF, and a final chunk count."],
                ["Open the generated `data/acme-leave-policy.md` next to the original PDF. Confirm that headings "
                 "became Markdown headings and the entitlement table became a Markdown table."],
            ],
        },
        {
            "h2": "Keep the page number, then chunk",
            "intro": ["An answer that cannot cite its page is much less useful to a public-sector reviewer. "
                      "This is where that is preserved."],
            "steps": [
                ["Each page carries spans that point into the returned Markdown. The code reassembles a page's "
                 "content from those spans, so every chunk knows its physical page:",
                 {"code": """for page in result.pages:
    content = ''.join(result.content[s.offset:s.offset + s.length] for s in page.spans)
    for start in range(0, len(content), 1500):
        chunks.append({'id': f'{pdf.stem}-{page.page_number}-{start}',
                       'content': content[start:start + 1800],
                       'source': pdf.name,
                       'page': page.page_number,
                       'allowed_groups': [...]})""", "lang": "python"}],
                ["Work out the chunking arithmetic: the window is **1,800 characters** and the step is "
                 "**1,500**, so consecutive chunks share **300 characters**. That overlap exists so a sentence "
                 "split across a boundary still appears whole in one of the two chunks.",
                 {"note": "These are *characters*, not tokens. Character windows are simple to teach and easy "
                          "to reason about, but they are not token-aware and they are not heading-aware."}],
                ["Notice the permission labels applied at extraction time:",
                 {"code": "'allowed_groups': ['hr-internal'] if 'leave' in pdf.name "
                          "else ['citizen-service', 'hr-internal']", "lang": "python"},
                 "The leave policy is HR-only; the others are shared. Exercise 08 enforces exactly these labels "
                 "at query time, so this is the moment access control actually begins."],
                ["Open `data/chunks.json` and find a chunk that starts mid-sentence. Then find the leave "
                 "entitlement table in the full Markdown and check whether any chunk splits it.",
                 {"warn": "A fixed-width window will eventually cut a table in half, and half a table can be "
                          "actively misleading when it is retrieved and quoted as evidence. Exercise 18 "
                          "compares this with a paragraph-preserving strategy."}],
                ["Confirm the saved outputs:",
                 {"code": "python validate.py --live", "lang": "powershell"},
                 {"note": "This checks that extraction outputs exist on disk. It is an *output* check, not a "
                          "fresh cloud call — the validator says so itself."}],
            ],
        },
    ],
    "knowledge_check": [
        {"q": "Which model extracts document layout?",
         "options": ["A. `prebuilt-layout`", "B. A chat deployment", "C. The HNSW algorithm"],
         "answer": "A",
         "why": "It returns structure and reading order, unlike a plain text extraction."},
        {"q": "What preserves table markup through extraction?",
         "options": ["A. Document IDs", "B. Requesting Markdown output", "C. Increasing quota"],
         "answer": "B",
         "why": "`output_content_format='markdown'` keeps tables as pipe tables instead of flattening them."},
        {"q": "Why keep the physical page number on each chunk?",
         "options": ["A. For billing", "B. For authentication", "C. So an answer can cite its source page"],
         "answer": "C",
         "why": "Citations are what let a reviewer verify an answer. Exercises 08, 18 and 21 all cite source "
                "and page."},
    ],
    "summary": [
        "You extracted three synthetic policies as Markdown, preserved table structure and physical page "
        "numbers, and produced overlapping chunks carrying source, page and permission metadata.",
        "You also saw the cost of a naive chunker. Exercise 18 measures a paragraph-preserving alternative "
        "against this one, and Exercise 07 hands the same job to a managed indexer instead.",
    ],
    "cleanup": [
        {"code": "python cleanup.py", "lang": "powershell"},
        "This exercise provisions nothing in Azure. Clean-up removes the local extraction outputs — the "
        "generated `.md` files and `data/chunks.json`.",
        {"tip": "Keep `data/chunks.json` if you intend to compare your real extraction against Exercise 07's "
                "bundled fixture; that comparison is described in Exercise 07."},
    ],
    "refs": [
        ("Document Intelligence layout model",
         "https://learn.microsoft.com/azure/ai-services/document-intelligence/prebuilt/layout?view=doc-intel-4.0.0"),
        ("Chunking guidance", "https://learn.microsoft.com/azure/search/vector-search-how-to-chunk-documents"),
    ],
}


LAB07 = {
    "num": "07",
    "slug": "07-search-integrated-vectorization",
    "short": "Integrated vectorization in Azure AI Search",
    "group": "Day 2 — Tools and retrieval",
    "track": "Foundry SDK",
    "module_tags": ["Module 4"],
    "title": "Build a managed ingestion pipeline with integrated vectorization",
    "minutes": 90,
    "lab_path": "day2-foundry-sdk-tools-and-rag/lab07-search-integrated-vectorization",
    "env_note": "`azure-search-documents==12.0.0`, `azure-storage-blob==12.30.1`",
    "blurb": "Wire a Blob data source, a Text Split skill and an embedding skill into an indexer, then query "
             "with hybrid search and semantic ranking.",
    "intro": [
        "Exercise 06 chunked documents in Python. This exercise hands the same work to Azure AI Search, which "
        "runs it as a managed pipeline: an **indexer** reads a data source, a **skillset** splits and embeds "
        "the text, and **index projections** write one document per chunk.",
        "This is the client's *integrated vectorization* requirement in full — indexer, Text Split skill and "
        "embedding skill — and it is the managed alternative to the fully visible Python pipeline you build in "
        "Exercise 18. Building both is what lets you argue for one.",
    ],
    "objectives": [
        "Create a vector index with an HNSW profile and a semantic configuration.",
        "Configure a Blob data source that authenticates with a managed identity, not a connection secret.",
        "Chain a Text Split skill and an Azure OpenAI embedding skill in a skillset.",
        "Project chunk fields — including page and permission metadata — onto child documents.",
        "Run a hybrid query with semantic reranking.",
    ],
    "prereqs": [
        "An Azure AI Search service with **semantic ranking enabled**, and a system-assigned managed identity.",
        "A storage account for indexer input.",
        "An Azure OpenAI resource with a `text-embedding-3-small` deployment.",
        "Roles: **Search Service Contributor** and **Search Index Data Contributor** for you; "
        "**Storage Blob Data Reader** and **Cognitive Services OpenAI User** for the *Search service's* "
        "managed identity.",
    ],
    "before_extra": [
        {"warn": "The identity assignments above are the usual cause of failure in this exercise. The Search "
                 "service, not you, reads the blobs and calls the embedding model. Assign those two roles to "
                 "the Search service's managed identity and allow time for propagation before you run anything."},
    ],
    "sections": [
        {
            "h2": "Set up",
            "steps": [
                [{"code": "cd day2-foundry-sdk-tools-and-rag/lab07-search-integrated-vectorization\n" + SETUP_PS,
                  "lang": "powershell"}],
                ["Fill in `.env`:",
                 {"code": """SEARCH_ENDPOINT=https://YOUR-SEARCH.search.windows.net
STORAGE_ACCOUNT_URL=https://YOUR-STORAGE.blob.core.windows.net
STORAGE_RESOURCE_ID=/subscriptions/.../providers/Microsoft.Storage/storageAccounts/YOUR-STORAGE
AZURE_OPENAI_ENDPOINT=https://YOUR-OPENAI.openai.azure.com
EMBEDDING_DEPLOYMENT=text-embedding-3-small""", "lang": "text"},
                 {"tip": "`STORAGE_RESOURCE_ID` is the full ARM resource ID. Get it with "
                         "`az storage account show -n YOUR-STORAGE -g YOUR-RG --query id -o tsv`."}],
                [{"code": "python validate.py", "lang": "powershell"},
                 {"ok": "`PASS OFFLINE: page metadata and permission strings present`."}],
            ],
        },
        {
            "h2": "Understand the five objects you are about to create",
            "intro": ["Open `src/demo.py`. It creates five Search objects plus a blob container. Read them "
                      "before running, because the relationships matter more than the syntax."],
            "steps": [
                ["**The index** defines the target schema, including the vector field and its profile:",
                 {"code": """SearchField(name='content_vector',
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=1536,
            vector_search_profile_name='vectors')""", "lang": "python"},
                 "The index also declares an `AzureOpenAIVectorizer`, which is what lets you later search with "
                 "plain text and have Search embed the query for you."],
                ["**The data source** points at the blob container using a resource ID rather than a key:",
                 {"code": "connection_string='ResourceId=' + os.environ['STORAGE_RESOURCE_ID'] + ';'",
                  "lang": "python"},
                 {"note": "That `ResourceId=` form tells Search to authenticate with its managed identity. "
                          "There is no account key anywhere in this exercise."}],
                ["**The Text Split skill** produces chunks from each document's text:",
                 {"code": """SplitSkill(context='/document', text_split_mode='pages',
           maximum_page_length=1000, page_overlap_length=100,
           inputs=[InputFieldMappingEntry(name='text', source='/document/content')],
           outputs=[OutputFieldMappingEntry(name='textItems', target_name='chunks')])""", "lang": "python"},
                 {"warn": "`text_split_mode='pages'` does **not** mean physical PDF pages. It means text "
                          "windows. This is a genuinely confusing piece of naming, and it is why this lab "
                          "carries the real page number as a separate field."}],
                ["**The embedding skill** runs over each chunk, generating vectors inside the pipeline:",
                 {"code": """AzureOpenAIEmbeddingSkill(context='/document/chunks/*', dimensions=1536, **embedding,
    inputs=[InputFieldMappingEntry(name='text', source='/document/chunks/*')],
    outputs=[OutputFieldMappingEntry(name='embedding', target_name='vector')])""", "lang": "python"},
                 "The `/document/chunks/*` context is what makes this run once per chunk rather than once per "
                 "document."],
                ["**Index projections** write one index document per chunk and carry the parent's metadata down:",
                 {"code": """SearchIndexerIndexProjectionSelector(
    target_index_name=name, parent_key_field_name='parent_id',
    source_context='/document/chunks/*',
    mappings=[InputFieldMappingEntry(name='content', source='/document/chunks/*'),
              InputFieldMappingEntry(name='content_vector', source='/document/chunks/*/vector'),
              InputFieldMappingEntry(name='source', source='/document/source'),
              InputFieldMappingEntry(name='page', source='/document/page'),
              InputFieldMappingEntry(name='allowed_groups', source='/document/allowed_groups')])""",
                  "lang": "python"},
                 "This is the step that keeps citation and permission data attached to each chunk. "
                 "`skipIndexingParentDocuments` means only chunks are indexed, not the whole parent."],
            ],
        },
        {
            "h2": "Run the pipeline and inspect execution",
            "steps": [
                ["Create everything. The script uploads each record from `data/chunks.json` as a JSON blob, "
                 "then creates the index, data source, skillset and indexer:",
                 {"code": "python src/demo.py", "lang": "powershell"},
                 "The indexer starts automatically when it is created."],
                ["Wait, then check that the run actually succeeded:",
                 {"code": "python validate.py --live", "lang": "powershell"},
                 {"ok": "`PASS LIVE: indexer succeeded and index contains documents`. The validator asserts "
                        "status `success`, zero errors **and** zero failed items — a partially failed indexer "
                        "run is a failure."},
                 {"tip": "If it fails, read the indexer's execution history in the portal. The error is almost "
                         "always a missing role on the *Search service's* managed identity."}],
                ["Query the index with hybrid search and semantic reranking:",
                 {"code": "python src/query.py", "lang": "powershell"},
                 {"code": """results = client.search(
    search_text=question,
    vector_queries=[VectorizableTextQuery(text=question, fields='content_vector',
                                          k_nearest_neighbors=50)],
    query_type='semantic',
    semantic_configuration_name='semantic',
    select=['content', 'source', 'page', 'allowed_groups'],
    top=3)""", "lang": "python"}],
                ["Three things are happening in that one call, and it is worth naming them separately:",
                 {"bullets": [
                     "`search_text` runs keyword (BM25) retrieval.",
                     "`vector_queries` runs vector similarity — and because the index has a vectorizer, Search "
                     "embeds your query text itself, using its own managed identity.",
                     "`query_type='semantic'` reranks the combined candidate set with a semantic reranker.",
                 ]},
                 "Confirm the returned results carry `source`, `page` and `allowed_groups`. Those fields "
                 "survived the whole managed pipeline, which is exactly what you configured the projections to do."],
                ["Re-run the indexer after changing input:",
                 {"code": "python src/query.py --run-indexer", "lang": "powershell"}],
            ],
        },
        {
            "h2": "Compare managed and custom ingestion",
            "intro": [
                "You now have one managed pipeline. Exercise 18 builds the same capability in visible Python. "
                "Note the trade-offs while this one is fresh.",
                {"table": (["", "Managed indexer (this exercise)", "Custom pipeline (Exercise 18)"], [
                    ["Chunking", "Configured in the skillset", "Your own code, inspectable and testable"],
                    ["Embedding", "Runs inside the pipeline under the Search identity",
                     "Explicit call you make and can measure"],
                    ["Scheduling and change detection", "Built in", "You build a manifest and checkpoint"],
                    ["Debugging", "Indexer execution history", "Ordinary Python, every intermediate visible"],
                    ["Best for", "Standard documents in a supported store", "Unusual sources or bespoke logic"],
                ])},
            ],
            "steps": [
                ["Optionally, feed your **real** Exercise 06 extraction into this managed pipeline. Back up "
                 "this lab's `data/chunks.json`, copy Exercise 06's version over it, use a fresh resource name, "
                 "and re-run. The field names are compatible.",
                 {"note": "Watch what happens: the skillset will split your already-small chunks again. That "
                          "double-split boundary is a real design consideration, not a bug — it is why you "
                          "normally pass full extracted pages to a managed skillset, not pre-made chunks."}],
            ],
        },
    ],
    "knowledge_check": [
        {"q": "Who generates the vectors at index time in this pipeline?",
         "options": ["A. The browser", "B. The embedding skill, running under the Search identity",
                     "C. Your Python process"],
         "answer": "B",
         "why": "That is the defining feature of integrated vectorization, and it is why the Search service "
                "needs Cognitive Services OpenAI User."},
        {"q": "What carries the original PDF page number onto each chunk?",
         "options": ["A. The index projection field mapping", "B. The HNSW algorithm",
                     "C. The semantic reranker"],
         "answer": "A",
         "why": "`SplitSkill`'s 'pages' are text windows, not physical pages. The real page is carried through "
                "explicitly as a projected field."},
        {"q": "Which identity reads the blobs for indexing?",
         "options": ["A. The signed-in end user", "B. The chat model", "C. The Search service's managed identity"],
         "answer": "C",
         "why": "The `ResourceId=` connection form selects managed identity, so no storage key is used."},
    ],
    "summary": [
        "You built a complete managed ingestion pipeline — Blob data source, Text Split skill, embedding skill, "
        "index projections and indexer — and queried it with hybrid retrieval plus semantic reranking.",
        "You also kept citation and permission metadata attached through every stage, which is what makes "
        "Exercise 08's security filtering possible on top of this index.",
    ],
    "cleanup": [
        "This exercise creates billable Search and Storage objects. Clean-up is important.",
        {"code": "python cleanup.py", "lang": "powershell"},
        "It asks you to confirm, then deletes **only** the objects whose names begin with `acme-lab07-demo-`: "
        "the indexer, skillset, data source, index and blob container. It asserts that prefix before deleting "
        "anything, so it cannot remove a shared index.",
        {"warn": "The Search service, storage account and Azure OpenAI resource themselves are shared "
                 "prerequisites and are deliberately left in place."},
    ],
    "refs": [
        ("Integrated vectorization",
         "https://learn.microsoft.com/azure/search/vector-search-integrated-vectorization"),
        ("Hybrid search", "https://learn.microsoft.com/azure/search/hybrid-search-overview"),
        ("Semantic ranking", "https://learn.microsoft.com/azure/search/semantic-search-overview"),
    ],
}


LAB08 = {
    "num": "08",
    "slug": "08-secure-rag",
    "short": "Security-trimmed retrieval",
    "group": "Day 2 — Tools and retrieval",
    "track": "Foundry SDK",
    "module_tags": ["Module 4", "Module 8"],
    "title": "Filter retrieval by group membership and prove the failure mode",
    "minutes": 45,
    "lab_path": "day2-foundry-sdk-tools-and-rag/lab08-secure-rag",
    "env_note": "`azure-search-documents==12.0.0` plus `azure-ai-projects==2.6.0`",
    "blurb": "Apply a trusted group filter before retrieval, compare two identities, and demonstrate the leak "
             "that occurs when the filter is omitted.",
    "intro": [
        "An agent must only surface documents the user is permitted to see. In this exercise you enforce that "
        "with an OData filter applied **at retrieval time**, compare what two different identities can reach, "
        "and then deliberately remove the filter to watch restricted content leak.",
        "The negative control is the most valuable part. Security controls that have never been observed failing "
        "are rarely trusted, and a filter that silently stops being applied is invisible unless you have seen "
        "what its absence looks like.",
    ],
    "objectives": [
        "Build an OData filter from trusted group membership.",
        "Compare the documents two synthetic identities can retrieve.",
        "Observe restricted documents leaking when the filter is omitted.",
        "Ground an answer in authorised context only.",
        "Explain why an application-side filter is not a service-enforced end-user ACL.",
    ],
    "prereqs": [
        "An Azure AI Search service, with **Search Service Contributor** and **Search Index Data Contributor**.",
        "A Foundry project and chat deployment, for the optional grounded-answer step.",
    ],
    "sections": [
        {
            "h2": "Set up and inspect the permission fixture",
            "steps": [
                [{"code": "cd day2-foundry-sdk-tools-and-rag/lab08-secure-rag\n" + SETUP_PS, "lang": "powershell"}],
                ["Fill in `SEARCH_ENDPOINT`, `PROJECT_ENDPOINT` and `MODEL_DEPLOYMENT`, then:",
                 {"code": "python validate.py", "lang": "powershell"},
                 {"ok": "The offline check confirms the fixture produces *distinct* identity sets and that at "
                        "least one document is restricted — without that, the negative control would prove "
                        "nothing."}],
                ["Open `data/chunks.json` and confirm the two labels in use: leave-policy chunks carry "
                 "`hr-internal` only, while the other policies carry both `citizen-service` and `hr-internal`. "
                 "So an HR officer should see strictly more than a citizen-service user."],
            ],
        },
        {
            "h2": "Read the filter, including its escaping",
            "steps": [
                ["The filter is nine lines of `src/demo.py` and deserves close reading:",
                 {"code": """def group_filter(groups: list[str]) -> str:
    # Trusted server-side membership only; escape OData literal characters.
    values = ','.join(g.replace("'", "''") for g in groups)
    return f"allowed_groups/any(g: search.in(g, '{values}'))" if groups else 'false'""",
                  "lang": "python"}],
                ["Three decisions are encoded there:",
                 {"bullets": [
                     "`allowed_groups/any(...)` matches if **any** of the document's labels is in the caller's "
                     "group list.",
                     "Single quotes are doubled, because a group name containing an apostrophe would otherwise "
                     "break out of the OData literal. This is injection defence, not tidiness.",
                     "An empty group list returns the literal `false` — **deny by default**. Returning an empty "
                     "filter instead would have matched everything, which is the classic version of this bug.",
                 ]},
                 {"tip": "Change the `else 'false'` to `else ''` and re-run to see the deny-by-default rule "
                         "invert into a total leak. Then change it back."}],
            ],
        },
        {
            "h2": "Compare two identities",
            "steps": [
                ["Run the demo:",
                 {"code": "python src/demo.py", "lang": "powershell"},
                 "It creates a small index, uploads the fixture, then queries once per synthetic identity."],
                ["Compare the two printed ID lists. The HR officer's set should be a strict superset of the "
                 "citizen-service set. The script asserts that every returned document actually carries one of "
                 "the caller's groups, so a wrong filter fails loudly rather than quietly returning too much."],
                ["Now the negative control. The script deliberately runs one unfiltered query:",
                 {"code": """unfiltered = list(client.search('*', top=1000))
leaked = [d['id'] for d in unfiltered if 'citizen-service' not in d['allowed_groups']]
assert leaked, 'Negative control requires at least one HR-only document'
print('EXPECTED NEGATIVE CONTROL: omitted filter exposes HR-only IDs:', leaked)""", "lang": "python"},
                 {"warn": "Those IDs are exactly what a citizen-service user would have received if the filter "
                          "had been dropped. Note that no error occurred — the query succeeded. This failure "
                          "mode is silent, which is why it must be tested for rather than assumed away."}],
                ["Optionally, ground an answer in authorised context only:",
                 {"code": "python src/demo.py --answer", "lang": "powershell"},
                 "Each persona's answer is generated from that persona's authorised passages alone, with "
                 "instructions to cite source and page and to say when information is absent. The filtering "
                 "happens *before* anything reaches the model — a model cannot be asked to forget context it "
                 "has already been given."],
            ],
        },
        {
            "h2": "Understand the boundary this does not cross",
            "intro": [
                "This exercise enforces access in the application. That is a real control, but it is important "
                "to be precise about what it is not.",
            ],
            "steps": [
                ["The Search credential authorises **the application**, not the end user. Search is returning "
                 "whatever the application asks for; the application is choosing to ask for less."],
                ["The group membership here comes from fixed synthetic identities in the script. In production "
                 "it must come from validated Entra claims — with group overage handled through an approved "
                 "path — and never from a value the browser supplied.",
                 {"warn": "If a client can send its own `allowed_groups`, there is no access control at all. "
                          "Exercise 21 builds the correct version: signature, issuer, audience and lifetime "
                          "validated first, groups taken only from verified claims."}],
                ["Read the preview boundary note, which explains why this lab does not ship speculative "
                 "native-ACL API calls:",
                 {"code": "python src/demo.py --preview", "lang": "powershell"},
                 "Native document-level ACLs are a separate capability requiring compatible source permission "
                 "ingestion, index schema and delegated token handling configured together. A flag cannot "
                 "convert a string-filter index into one."],
                ["Record in your notes where the three layers sit: the *label* is applied at ingestion "
                 "(Exercise 06), the *filter* is applied at retrieval (here), and the *identity* is validated "
                 "at the API boundary (Exercise 21). All three are required."],
            ],
        },
    ],
    "knowledge_check": [
        {"q": "Where must permission filtering happen?",
         "options": ["A. After the model produces an answer", "B. During retrieval, before context reaches the model",
                     "C. In the browser's styling"],
         "answer": "B",
         "why": "Once unauthorised text is in the model's context it may appear in the answer. Filtering must "
                "come first."},
        {"q": "Where should the caller's group list come from?",
         "options": ["A. Validated identity claims resolved server-side", "B. A field in the chat request body",
                     "C. A dropdown in the UI"],
         "answer": "A",
         "why": "Anything the client supplies can be forged. Exercise 21 demonstrates verifying the token "
                "signature before trusting a single claim."},
        {"q": "What does the negative control prove?",
         "options": ["A. That an empty result set is returned",
                     "B. That restricted document IDs appear when the filter is omitted",
                     "C. That both identities get the same answer"],
         "answer": "B",
         "why": "It makes the silent failure mode visible, so you know what a missing filter looks like."},
    ],
    "summary": [
        "You built a deny-by-default OData group filter with proper literal escaping, compared what two "
        "identities can retrieve, watched restricted documents leak when the filter was dropped, and grounded "
        "an answer in authorised context only.",
        "You also placed this control accurately: it is application-enforced trimming, and it depends entirely "
        "on the group list being trustworthy. Exercise 21 supplies that trust.",
    ],
    "cleanup": [
        {"code": "python cleanup.py", "lang": "powershell"},
        "Only the index recorded in `data/resource-state.json` is deleted. The Search service itself is a "
        "shared prerequisite and remains.",
        {"warn": "The unfiltered query in this exercise is a teaching fixture over synthetic data. Never copy "
                 "that code path into an application — an unfiltered retrieval route must not exist in "
                 "something users can reach."},
    ],
    "refs": [
        ("Document-level access overview",
         "https://learn.microsoft.com/azure/search/search-document-level-access-overview"),
        ("Security trimming", "https://learn.microsoft.com/azure/search/search-security-trimming-for-azure-search"),
    ],
}

LABS = [LAB05, LAB06, LAB07, LAB08]
