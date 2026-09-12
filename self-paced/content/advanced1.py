"""Exercises 17-20 — Advanced client-engineering labs."""

ADV = "Advance labs client-engineering"

SETUP_ADV = """py -3.11 -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
az login
python validate.py"""


LAB17 = {
    "num": "17",
    "slug": "17-models-embeddings-and-architecture",
    "short": "Model choice, embeddings and architecture",
    "group": "Advanced — client engineering",
    "track": "Advanced",
    "module_tags": ["Module 1", "Module 2"],
    "title": "Compare models, measure embeddings and map the platform architecture",
    "minutes": 120,
    "lab_path": f"{ADV}/lab17-models-embeddings-and-architecture",
    "env_note": "`azure-ai-projects==2.6.0` plus `openai==3.11.0`; Foundry Local is a separate optional install",
    "blurb": "Measure two models on one task, compare embedding dimensions, run a vision input, cost it out, "
             "and produce an architecture decision with evidence.",
    "intro": [
        "This exercise is the platform and model-selection module in practice. Rather than reading a catalogue, "
        "you measure: two deployments on an identical task, two embedding dimensions on identical text, a "
        "multimodal input, and the cost arithmetic that follows from those measurements.",
        "It is split into short independent parts. Each produces a piece of evidence for a written architecture "
        "and model decision — which is the actual deliverable, not the scripts.",
    ],
    "objectives": [
        "Map platform components and the bring-your-own data stores to real resource IDs.",
        "Compare two model deployments on one task, with measured latency and token usage.",
        "Measure embedding dimensions, similarity ranking, token cost and vector storage size.",
        "Send an image to a vision-capable model and reason about when not to.",
        "Calculate token cost from measured usage using your own current rates.",
        "Optionally run a model entirely on-device with Foundry Local.",
    ],
    "prereqs": [
        "A Foundry project with **two** chat deployments of different size or capability.",
        "A vision-capable deployment for the multimodal part.",
        "An Azure OpenAI resource with `text-embedding-3-small`, and **Cognitive Services OpenAI User** on it.",
        "Optional: a supported Windows device for Foundry Local, installed into a **separate** environment.",
    ],
    "sections": [
        {
            "h2": "Set up",
            "steps": [
                [{"code": f"cd \"{ADV}/lab17-models-embeddings-and-architecture\"\n" + SETUP_ADV,
                  "lang": "powershell"}],
                ["Fill in `.env`. Note that `MODEL_DEPLOYMENTS` is a **comma-separated list**:",
                 {"code": """PROJECT_ENDPOINT=https://YOUR-RESOURCE.services.ai.azure.com/api/projects/YOUR-PROJECT
MODEL_DEPLOYMENTS=YOUR-SMALL-CHAT-DEPLOYMENT,YOUR-LARGER-CHAT-DEPLOYMENT
VISION_DEPLOYMENT=YOUR-VISION-CAPABLE-DEPLOYMENT
AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE.openai.azure.com
EMBEDDING_DEPLOYMENT=text-embedding-3-small
LOCAL_MODEL_ALIAS=qwen2.5-0.5b""", "lang": "text"},
                 {"warn": "`AZURE_OPENAI_ENDPOINT` is the **Azure OpenAI resource** URL, not the Foundry "
                          "project endpoint. Mixing these two up is the most common failure in this exercise "
                          "and in Exercise 18."}],
                ["No API keys are used. In `src/embeddings.py` the OpenAI client is given a token provider:",
                 {"code": """token = get_bearer_token_provider(DefaultAzureCredential(),
                                  'https://cognitiveservices.azure.com/.default')
client = OpenAI(base_url=..., api_key=token)""", "lang": "python"},
                 {"note": "That `api_key=` parameter receives an Entra token **callback**, not a stored key. "
                          "The callback refreshes the token as needed."}],
            ],
        },
        {
            "h2": "Part 1 — Map the architecture",
            "intro": ["Open `data/architecture-and-model-decisions.md`. This is a worksheet, and it is the part "
                      "of the exercise that survives the classroom."],
            "steps": [
                ["Fill in the component table with **actual resource IDs and identities**, not product names. "
                 "The rows cover the Foundry account and projects, the model catalogue, Agent Service, "
                 "Tools/Toolboxes, Foundry IQ, the Control Plane, Foundry Local, Storage, Azure AI Search and "
                 "Cosmos DB.",
                 {"tip": "Inspect the `type` value of each resource in Azure Resource Explorer. Foundry's "
                         "consolidated account and project model does not mean Storage, Search and Cosmos stop "
                         "being separately billed resources with their own providers and their own data-plane "
                         "access."}],
                ["Trace two flows on a diagram, separately:",
                 {"bullets": [
                     "**Request**: browser identity → API → authorised Search query → model → response.",
                     "**Ingestion**: original document → extraction → chunks → embeddings → index.",
                 ]},
                 "Mark every point where the flow crosses a process, network, identity or data-residency "
                 "boundary."],
                ["Place conversation storage on the diagram honestly. For a basic managed setup you may not "
                 "claim state sits in your own Cosmos account; for standard bring-your-own, inspect the actual "
                 "configured connections. Exercise 19 verifies this."],
                ["Complete the deployment comparison table — Global Standard, Regional Standard, provisioned "
                 "throughput (PTU), serverless/API offering, managed compute and Local — recording what you "
                 "must justify for each.",
                 {"warn": "These are not interchangeable SKU names, and not every catalogue model offers every "
                          "option. Check per model. Do **not** provision all of them to complete the table; "
                          "this is an inspection exercise."}],
                ["Complete the **authoring surfaces** comparison at the end of the worksheet: locate your agent "
                 "in the portal, in the Exercise 03 SDK source, in the REST reference, and in the VS Code "
                 "Foundry extension. Record one confirmed capability and one limitation per surface.",
                 {"note": "Do not assume portal, extension and SDK expose every preview at the same time. The "
                          "SDK path is the mandatory hands-on one; duplicating a build in all four surfaces is "
                          "optional."}],
            ],
        },
        {
            "h2": "Part 2 — Compare two models on one task",
            "steps": [
                [{"code": "python src/compare_models.py", "lang": "powershell"}],
                ["Both deployments receive an identical prompt containing a deliberate trap: the library "
                 "opening time **is** in the supplied facts, and the bin collection day **is not**.",
                 {"code": """input='Synthetic council facts: library opens at 9 am weekdays. '
      'Waste pickup varies by address. Resident asks: When does the library '
      'open and when is my bin collected?'""", "lang": "python"}],
                ["Score each answer on three things: does it give the opening time correctly; does it "
                 "**acknowledge** that the bin day is unknown rather than inventing one; and how does its "
                 "latency and token usage compare.",
                 {"ok": "A model that invents a bin collection day has failed, regardless of how fluent or fast "
                        "it is. That behaviour is the single most important property for resident enquiries."}],
                ["Run it **three times**.",
                 {"warn": "A single latency reading is not a benchmark. Note how much the numbers move between "
                          "runs before quoting any of them."}],
                ["Results are saved to `data/model-results.json` with real `input_tokens` and `output_tokens` "
                 "from the service. Part 4 uses that file."],
            ],
        },
        {
            "h2": "Part 3 — Measure embeddings",
            "steps": [
                [{"code": "python src/embeddings.py", "lang": "powershell"},
                 "The same texts are embedded twice, at 256 and at 1,536 dimensions."],
                ["Compare the four measurements the script prints for each dimension: the cosine-similarity "
                 "ranking, elapsed time, total tokens, and `raw_float32_bytes_per_vector`.",
                 {"table": (["Dimensions", "Bytes per vector (float32)", "Relative index size"], [
                     ["256", "1,024", "1×"],
                     ["1,536", "6,144", "6×"],
                 ])},
                 "At a million chunks that is roughly 1 GB against 6 GB of raw vector data, before index "
                 "overhead. That is the trade-off you are being asked to reason about."],
                ["Check whether the similarity **ranking** actually changed between the two dimensions on this "
                 "small sample.",
                 {"warn": "Three short texts cannot establish that fewer dimensions preserve retrieval quality. "
                          "If the ranking is identical here, that is an observation about this sample, not a "
                          "finding about your corpus. Measure on representative data before reducing dimensions."}],
                ["Note the rule that governs everything downstream: **index vectors and query vectors must use "
                 "the same model and the same dimensions.** Changing either requires a new compatible index and "
                 "a full re-embed, not an environment-variable change.",
                 {"note": "Exercise 18's incremental sync detects *source* changes. It cannot detect that you "
                          "swapped embedding models, which is exactly why that change forces a rebuild."}],
            ],
        },
        {
            "h2": "Part 4 — Cost the workload",
            "steps": [
                ["Use the token counts you actually measured in Part 2:",
                 {"code": "python src/estimate_cost.py --input-per-million 1 --output-per-million 2 --requests 1000",
                  "lang": "powershell"}],
                ["Those rates are **illustrative placeholders**. Replace both with the current approved pricing "
                 "for the specific model you measured, in one currency, and record the pricing date and source.",
                 {"warn": "The same supplied rates are applied to every row in the file. If your two "
                          "deployments have different prices — and they usually do — run the script once per "
                          "model with that model's rates. Do not compare two models using one model's price."}],
                ["Model tokens are only part of the bill. Add to the worksheet: Search tier, replicas and "
                 "partitions; Blob capacity and operations; Cosmos throughput and storage; Functions and "
                 "hosting; evaluation judge tokens (Exercise 11 alone is ~100 calls per run); and telemetry "
                 "ingestion and retention."],
                ["Produce low, expected and high traffic scenarios. A single point estimate is not a budget."],
            ],
        },
        {
            "h2": "Part 5 — Multimodal input",
            "steps": [
                ["Open `data/policy-page.png` and read the leave entitlement table yourself, so you know the "
                 "correct answer before the model gives you one."],
                [{"code": "python src/multimodal.py", "lang": "powershell"},
                 "The image is base64-encoded and sent as an `input_image` content part alongside the text "
                 "instruction."],
                ["Check both numbers the model returns against the image, and check whether it correctly "
                 "reports the page number."],
                ["Now the design discussion. You have two ways to read a document: this one, and Document "
                 "Intelligence plus retrieval from Exercises 06 and 18.",
                 {"table": (["", "Vision model", "Document Intelligence + retrieval"], [
                     ["Output", "Generative; may paraphrase or err", "Deterministic extraction with spans"],
                     ["Citations", "Whatever the model states", "Real page numbers preserved through the pipeline"],
                     ["Scale", "One image per request", "Whole corpora, indexed and incrementally updated"],
                     ["Best for", "Ad-hoc reading, charts, layout questions", "Searchable, citable record sets"],
                 ])},
                 {"note": "For the client's records-and-enquiries use case, the right answer is usually "
                          "extraction plus retrieval. Vision is a complement, not a substitute."}],
            ],
        },
        {
            "h2": "Part 6 — Optional: Foundry Local",
            "intro": [
                {"warn": "This part needs supported hardware and a **separate** virtual environment. Install "
                         "`foundry-local-sdk-winml==1.2.4` on supported Windows, or `foundry-local-sdk==2.0.1` "
                         "cross-platform. Do not add it to this exercise's environment."},
            ],
            "steps": [
                [{"code": "python src/local_model.py", "lang": "powershell"},
                 "The first run downloads runtime and model assets, which can take some time."],
                ["Once the model is cached, disconnect from the network and run it again. Inference should "
                 "still work.",
                 {"note": "This script uses **no** Azure subscription and **no** Azure credential. It is "
                          "genuinely on-device."}],
                ["Now the important qualification for a sovereignty discussion.",
                 {"warn": "Local inference does not make a connected application sovereign. If the same "
                          "application still calls a hosted tool, a remote search index or a cloud telemetry "
                          "endpoint, data still leaves the device. Local inference removes *one* egress path, "
                          "not all of them."}],
                ["Add a Foundry Local row to your architecture diagram, and mark which other components in your "
                 "design would still reach the network."],
            ],
        },
    ],
    "knowledge_check": [
        {"q": "What must match between the vectors you index and the vectors you query with?",
         "options": ["A. The embedding model and the dimension count", "B. Only the file name",
                     "C. Only the region"],
         "answer": "A",
         "why": "Vectors from different models or dimensions are not comparable. Changing either forces a new "
                "index and a full re-embed."},
        {"q": "What does a single latency measurement prove?",
         "options": ["A. One observed request time", "B. A general ranking of the two models",
                     "C. A production service level"],
         "answer": "A",
         "why": "Latency varies with load, region, prompt and throttling. Repeat and report the spread."},
        {"q": "Does running a model with Foundry Local mean all application data stays on the device?",
         "options": ["A. No — tools, retrieval and telemetry may still be remote", "B. Yes, always",
                     "C. Only for PDF inputs"],
         "answer": "A",
         "why": "It removes the model-inference egress path only. Every other remote dependency remains."},
    ],
    "summary": [
        "You mapped the platform to real resource IDs, measured two models on one task including whether each "
        "admits what it does not know, compared embedding dimensions on ranking and storage, calculated cost "
        "from measured tokens, sent a multimodal input, and optionally ran a model on-device.",
        "The deliverable is the completed worksheet: a diagram with identity and residency boundaries marked, a "
        "justified deployment-type choice, and a cost estimate with stated assumptions.",
    ],
    "cleanup": [
        {"code": "python cleanup.py", "lang": "powershell"},
        "This prompts before deleting the generated local reports `data/model-results.json` and "
        "`data/embedding-results.json`. It is safe to run repeatedly.",
        "Shared Azure services are instructor-owned and are not touched. Manage any Foundry Local model cache "
        "through the Local SDK rather than deleting cache folders by hand.",
    ],
    "refs": [
        ("Foundry SDK overview", "https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview"),
        ("Embeddings", "https://learn.microsoft.com/azure/ai-foundry/openai/how-to/embeddings"),
        ("Deployment types", "https://learn.microsoft.com/azure/ai-foundry/openai/how-to/deployment-types"),
        ("Foundry Local", "https://learn.microsoft.com/azure/foundry-local/get-started"),
    ],
}


LAB18 = {
    "num": "18",
    "slug": "18-end-to-end-rag",
    "short": "Build and measure a RAG pipeline",
    "group": "Advanced — client engineering",
    "track": "Advanced",
    "module_tags": ["Module 4"],
    "title": "Build a connected RAG pipeline and measure its retrieval quality",
    "minutes": 150,
    "lab_path": f"{ADV}/lab18-end-to-end-rag",
    "env_note": "`azure-search-documents==12.0.0`, `openai==3.11.0`, `PyMuPDF==1.28.2`, "
                "`azure-ai-documentintelligence==1.0.2`",
    "blurb": "PDF to cited answer with every intermediate visible: chunking strategies, incremental sync, OCR, "
             "four retrieval modes and measured recall.",
    "intro": [
        "This is the centrepiece exercise for the client's highest-value use case. You build the whole pipeline "
        "in short, readable scripts — source PDF → extracted text → chunks → embeddings → index → retrieved "
        "passages → cited answer — with every intermediate artefact on disk where you can inspect it.",
        "Exercise 07 built the managed equivalent. Here nothing is hidden, which is what lets you compare "
        "chunking strategies, handle updates and deletions correctly, and actually measure retrieval quality "
        "rather than assuming it.",
        "It runs in three parts of roughly 50, 40 and 60 minutes. You can stop between them.",
    ],
    "objectives": [
        "Extract real PDF text and compare fixed-width with paragraph-preserving chunking.",
        "Generate 1,536-dimensional embeddings and store them with source, page and ACL metadata.",
        "Add, change and delete a source, and verify stale chunks disappear.",
        "Ingest an image-only PDF with Document Intelligence OCR.",
        "Compare keyword, vector, hybrid and semantic retrieval against labelled questions.",
        "Compute precision@k, recall@k and MRR — and state what they do not prove.",
    ],
    "prereqs": [
        "An Azure AI Search service with **semantic ranking enabled**.",
        "An Azure OpenAI resource with `text-embedding-3-small` and a Responses-capable model.",
        "Roles: **Search Service Contributor** (schema), **Search Index Data Contributor** (data and query), "
        "**Cognitive Services OpenAI User** (embeddings and model).",
        "A dedicated index name beginning `lab18-`. The code refuses anything else.",
        "Optional, for OCR: a Document Intelligence resource.",
    ],
    "before_extra": [
        {"warn": "`AZURE_OPENAI_ENDPOINT` is the Azure OpenAI **resource** URL, not the Foundry project "
                 "endpoint. This is the single most common setup error in this exercise."},
        {"note": "The offline validator for this exercise is unusually thorough — it runs the real `sync.py` "
                 "against an in-memory fake, including a rejected-write scenario, and asserts the checkpoint "
                 "did not advance. Run `python validate.py` before touching Azure; it costs nothing and catches "
                 "most mistakes."},
    ],
    "sections": [
        {
            "h2": "Set up",
            "steps": [
                [{"code": f"cd \"{ADV}/lab18-end-to-end-rag\"\n" + SETUP_ADV, "lang": "powershell"}],
                [{"code": """SEARCH_ENDPOINT=https://YOUR-SEARCH.search.windows.net
SEARCH_INDEX=lab18-YOUR-LOWERCASE-INITIALS
AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE.openai.azure.com
EMBEDDING_DEPLOYMENT=text-embedding-3-small
MODEL_DEPLOYMENT=YOUR-RESPONSES-MODEL
DOCUMENT_INTELLIGENCE_ENDPOINT=https://YOUR-DI.cognitiveservices.azure.com""", "lang": "text"}],
                [{"ok": "The offline validator should end with a long PASS line covering add/update/delete, "
                        "no-op, failed-write checkpoint recovery, stale chunk removal, ACL inheritance, chunk "
                        "overlap, deny-empty filters, the metric formulas and PDF text presence."}],
                ["Open `data/sources.json`. This is the authoritative source list with its access labels, and "
                 "`freshness.py` edits it for you later.",
                 {"code": """[{"file": "acme-code-of-conduct.pdf", "allowed_groups": ["staff"]},
 {"file": "acme-leave-policy.pdf",   "allowed_groups": ["staff", "hr"]},
 {"file": "acme-travel-policy.pdf",  "allowed_groups": ["staff"]}]""", "lang": "json"}],
            ],
        },
        {
            "h2": "Part A — Extract, chunk, index and query",
            "steps": [
                ["Extract and chunk with the fixed strategy:",
                 {"code": "python src/ingest.py --strategy fixed", "lang": "powershell"}],
                ["Open `data/chunks.json`. Every chunk has a **stable ID derived from source, page and "
                 "ordinal** — not a random one:",
                 {"code": """id=hashlib.sha256(f'{source}:{page}:{i}'.encode()).hexdigest()""", "lang": "python"},
                 {"note": "Stability is what makes incremental sync possible in Part B. If IDs changed on every "
                          "run, every chunk would look new and you would re-embed the whole corpus each time."}],
                ["Note what is **not** in that file: the vector. Embeddings are generated during `sync.py`, so "
                 "the chunk file stays readable and diffable."],
                ["Create the index, then sync:",
                 {"code": "python src/index.py\npython src/sync.py", "lang": "powershell"},
                 "`sync.py` prints uploaded, deleted and unchanged counts. On a first run everything is uploaded."],
                ["Ask a question and get a cited answer:",
                 {"code": 'python src/query.py "How many annual leave days do full-time staff receive?" --answer',
                  "lang": "powershell"},
                 {"tip": "Search takes a moment to make new documents queryable. If results are empty "
                         "immediately after a sync, wait briefly and re-run."}],
                ["Take a baseline measurement:",
                 {"code": "python src/measure.py", "lang": "powershell"},
                 "Copy the printed numbers, or the JSON report, somewhere outside the report filename — the "
                 "next step overwrites it."],
                ["Now switch chunking strategy and re-measure:",
                 {"code": """python src/ingest.py --strategy paragraph
python src/sync.py
python src/measure.py""", "lang": "powershell"}],
                ["Compare chunk count, precision, recall and reciprocal rank between the two strategies.",
                 {"bullets": [
                     "**fixed** — 500 *characters* with 80 characters of overlap. Simple, and blind to structure.",
                     "**paragraph** — packs whole PDF text blocks, so a long block can exceed the target size "
                     "rather than be cut.",
                 ]},
                 {"warn": "On a three-document corpus the two strategies may tie exactly. Report that. Do not "
                          "invent an improvement, and do not generalise from it."}],
                ["Neither strategy is heading-aware. Discuss how you would carry the current section heading "
                 "into each chunk, and why that usually helps a policy corpus more than tuning the window size."],
            ],
        },
        {
            "h2": "Part B — Freshness, updates and deletions",
            "intro": ["Real corpora change. This part proves that changes propagate and, just as importantly, "
                      "that removed content stops being retrievable."],
            "steps": [
                ["Run the full add / update / delete cycle. `freshness.py` edits the source manifest for you so "
                 "you never have to hand-edit the supplied PDFs:",
                 {"code": """python src/freshness.py add
python src/ingest.py
python src/sync.py
python src/query.py "When does the service desk close on Fridays?" --answer""", "lang": "powershell"},
                 {"ok": "Expected answer: **4 pm**."}],
                [{"code": """python src/freshness.py update
python src/ingest.py
python src/sync.py
python src/query.py "When does the service desk close on Fridays?" --answer""", "lang": "powershell"},
                 {"ok": "Expected answer: **6 pm**. If you still get 4 pm, the stale chunk was not replaced."}],
                [{"code": """python src/freshness.py delete
python src/ingest.py
python src/sync.py
python src/query.py "When does the service desk close on Fridays?" --answer""", "lang": "powershell"},
                 {"ok": "No source now supports an answer, and the assistant should say so rather than "
                        "recalling the old one."},
                 {"tip": "Inspect the **result sources**, not just the prose. A confident-sounding answer with "
                         "no supporting source is the failure you are testing for."}],
                ["Run `python src/sync.py` once more with nothing changed. It should report **zero uploads and "
                 "zero deletes** — no wasted embedding calls.",
                 {"note": "This is the change-detection mechanism: `manifest()` hashes each document and "
                          "`changes()` compares it with the saved checkpoint."}],
                ["Read the write-ordering in `src/sync.py`. It is the part worth taking away:",
                 {"code": """# Save only after Search accepts every action.
temporary = state.with_suffix('.tmp')
temporary.write_text(json.dumps(current, indent=2))
temporary.replace(state)""", "lang": "python"},
                 {"bullets": [
                     "Every upload and delete is checked; a rejection raises and the checkpoint is **not** "
                     "advanced.",
                     "The checkpoint is written to a temporary file and atomically replaced, so an interrupted "
                     "run cannot leave a half-written checkpoint.",
                     "Re-running after a failure safely repeats the unfinished work.",
                 ]},
                 {"warn": "The local manifest is a teaching checkpoint for **one writer**. It is not a "
                          "distributed scheduler or a transaction log. Keep it with the index, and delete it if "
                          "the index is ever recreated."}],
                ["Try two more cases: reduce a source's chunk count and confirm the obsolete ordinal IDs are "
                 "deleted; and change a source's `allowed_groups`, which is a content change and therefore "
                 "triggers an update."],
            ],
        },
        {
            "h2": "Part B (extension) — Scanned records and OCR",
            "steps": [
                ["First remove the text source so the comparison stays clean:",
                 {"code": "python src/freshness.py delete", "lang": "powershell"}],
                ["Create an image-only PDF from an existing synthetic policy:",
                 {"code": "python src/scanned.py", "lang": "powershell"},
                 "This rasterises each page, producing `data/scanned-conduct.pdf` with images and no embedded "
                 "text."],
                ["Add it to `data/sources.json` with `allowed_groups: [\"staff\"]`, then try normal ingestion:",
                 {"code": "python src/ingest.py", "lang": "powershell"},
                 {"ok": "It should fail deliberately with `No embedded text in scanned-conduct.pdf; use --ocr "
                        "for scanned PDFs`. A silent empty extraction would be far worse."}],
                ["Now use OCR:",
                 {"code": "python src/ingest.py --ocr\npython src/sync.py", "lang": "powershell"},
                 "`prebuilt-read` processes the real PDF bytes and returns lines grouped by page, so page "
                 "numbers survive into your citations."],
                ["Two distinctions worth recording:",
                 {"bullets": [
                     "Local PyMuPDF text extraction is **not** OCR. It reads embedded text; it cannot read "
                     "pixels.",
                     "OCR line grouping is **not** layout-aware paragraph segmentation. You get lines, not "
                     "semantic blocks.",
                 ]}],
                ["Remove the scanned source from the manifest, then ingest and sync again before returning to "
                 "the benchmark."],
            ],
        },
        {
            "h2": "Part C — Measure retrieval quality",
            "intro": ["`measure.py` queries the real index four times per question and scores the results. "
                      "Read how it avoids cheating before you read its numbers."],
            "steps": [
                ["Only the question and the caller's groups enter Search. The relevant-source labels are used "
                 "**after** retrieval, never inserted into the query or the model context.",
                 {"ok": "That ordering is what makes the measurement meaningful. An evaluation that feeds the "
                        "answer into the query measures nothing."}],
                ["The four modes differ by exactly one or two arguments in `retrieve()`:",
                 {"table": (["Mode", "What it sends"], [
                     ["keyword", "`search_text` only — BM25"],
                     ["vector", "`vector_queries` only — pure similarity"],
                     ["hybrid", "Both, fused"],
                     ["semantic", "Both, plus `query_type='semantic'` reranking"],
                 ])}],
                [{"code": "python src/measure.py", "lang": "powershell"},
                 "Each mode writes `data/retrieval-<mode>.json` with the dataset SHA-256, the expected and "
                 "retrieved source IDs per case, and the aggregate metrics."],
                ["Understand the metric definitions, measured at the **unique source-document** level after "
                 "deduplicating chunks:",
                 {"bullets": [
                     "**Precision@5** = relevant sources retrieved ÷ 5. Empty result slots count as misses.",
                     "**Recall@5** = relevant sources retrieved ÷ all labelled relevant sources.",
                     "**MRR** = mean reciprocal rank of the first relevant source within the top five.",
                 ]}],
                ["Now the honest limitation, and you should be able to state it unprompted:",
                 {"warn": "There are only three source documents and one relevant source per question, so the "
                          "**maximum possible precision@5 here is 0.2**. This is a formula lesson and an "
                          "integration check, not a quality benchmark. Before making any production claim you "
                          "need many distractor documents, multi-document questions and a held-out labelled set."}],
                ["Compare the four modes and record which performed best on this corpus — then note that "
                 "reranking improvements are not guaranteed and depend heavily on content and query style."],
                ["Finally, separate the two questions that are easy to conflate:",
                 {"note": "**Retrieval recall** asks whether the right document was found. **Groundedness** "
                          "asks whether the generated answer's claims are actually supported by what was "
                          "retrieved. A perfect recall score does not imply a grounded answer. Exercises 11 and "
                          "23 measure the second."}],
            ],
        },
        {
            "h2": "Part C — Security boundaries",
            "steps": [
                ["Change one source's `allowed_groups` from `staff` to `hr`, then ingest and sync. Query as "
                 "`staff` and confirm that source is now excluded."],
                ["Call `retrieve(question, [], 'hybrid')` from a short script. Expect **no results** — the "
                 "deny-by-default filter from Exercise 08 at work.",
                 "Restore the original ACLs and re-sync afterwards."],
                ["Be precise about what this CLI is:",
                 {"warn": "It authenticates the **application's** access to Search. It does not sign in a "
                          "resident. The `staff` group is hard-coded as an explicit simulation. Do not deploy "
                          "this CLI as a user-facing security boundary."}],
                ["For a real application the backend must validate token signature, issuer, audience and "
                 "lifetime, resolve group overage through an approved path, and only then pass trusted "
                 "memberships into `retrieve`. Exercise 21 builds exactly that.",
                 {"note": "Exercise 21 deliberately uses a different, GUID-based index schema. Mapping this "
                          "pipeline onto that schema is an integration exercise; the two are not drop-in "
                          "replacements for one another."}],
            ],
        },
    ],
    "knowledge_check": [
        {"q": "Why must an updated document with fewer chunks have its old IDs deleted?",
         "options": ["A. To save storage cost", "B. Otherwise stale passages remain retrievable",
                     "C. To reset the embedding model"],
         "answer": "B",
         "why": "Orphaned chunks stay in the index and can still be returned as evidence for an answer."},
        {"q": "Does a high recall@5 score prove the generated answer is grounded?",
         "options": ["A. Yes", "B. No — retrieval and answer quality are different measurements",
                     "C. Only with semantic ranking"],
         "answer": "B",
         "why": "Finding the right document says nothing about whether the model's claims are supported by it."},
        {"q": "Can a client supply its own `allowed_groups` as a query parameter?",
         "options": ["A. Yes, if the UI restricts the options", "B. Yes, over HTTPS",
                     "C. No — permissions must come from validated identity"],
         "answer": "C",
         "why": "Anything the client controls can be forged, which would defeat the filter entirely."},
    ],
    "summary": [
        "You built a complete retrieval pipeline with every intermediate visible, compared two chunking "
        "strategies, proved that additions, changes and deletions propagate while a no-op costs nothing, "
        "ingested an image-only PDF with OCR, measured four retrieval modes against labelled questions, and "
        "exercised the permission filter in both directions.",
        "Just as importantly, you can state what the numbers do not prove: a three-document corpus caps "
        "precision@5 at 0.2, and retrieval recall is not groundedness.",
    ],
    "cleanup": [
        {"code": "python cleanup.py", "lang": "powershell"},
        "This deletes **only** the `lab18-` index named in your `.env`, plus its local checkpoint. The Search "
        "service, Azure OpenAI resource and Document Intelligence resource are shared prerequisites and remain.",
        "Delete the generated reports in `data/` when you no longer need the evidence, and never commit live "
        "output or `.env`.",
    ],
    "refs": [
        ("Chunking documents", "https://learn.microsoft.com/azure/search/vector-search-how-to-chunk-documents"),
        ("Create a vector index", "https://learn.microsoft.com/azure/search/vector-search-how-to-create-index"),
        ("Indexing and deletion", "https://learn.microsoft.com/azure/search/search-howto-reindex"),
        ("Hybrid search", "https://learn.microsoft.com/azure/search/hybrid-search-overview"),
    ],
}


LAB19 = {
    "num": "19",
    "slug": "19-cosmos-state-and-vectors",
    "short": "Cosmos state, TTL and vectors",
    "group": "Advanced — client engineering",
    "track": "Advanced",
    "module_tags": ["Module 5"],
    "title": "Persist agent state in Cosmos DB and query vectors alongside it",
    "minutes": 120,
    "lab_path": f"{ADV}/lab19-cosmos-state-and-vectors",
    "env_note": "`azure-cosmos==4.17.0`, `openai==2.54.0` — note the different OpenAI pin",
    "blurb": "Save and recover conversation state across processes, apply TTL, query vectors in Cosmos, and "
             "inspect the service-owned enterprise_memory database.",
    "intro": [
        "Exercise 14 kept a conversation in a session object and a local file. This exercise answers the "
        "production question: **where does that state actually live**, who can read it, and how long does it "
        "survive?",
        "You will persist state in Cosmos DB partitioned by a *token-derived* identity, prove recovery in a "
        "separate process, apply different TTLs to short- and long-term memory, run a vector query against "
        "application data, and inspect the service-owned `enterprise_memory` database read-only.",
    ],
    "objectives": [
        "Derive a partition key from an SDK-acquired token rather than a request parameter.",
        "Save and recover conversation state across two separate processes.",
        "Distinguish short-term and long-term memory with TTL.",
        "Run a vector similarity query in Cosmos DB.",
        "Inspect `enterprise_memory` metadata safely, and reconcile RU/s requirements.",
        "Decide when Cosmos is the right vector store and when Azure AI Search is.",
    ],
    "prereqs": [
        "A Cosmos DB for NoSQL account with vector search enabled, in an approved region.",
        "**Cosmos DB Built-in Data Contributor** at `/dbs/workshop-memory`. Subscription Contributor is a "
        "control-plane role and does **not** grant data access.",
        "**Cognitive Services OpenAI User** on the embedding resource.",
        "Firewall or private endpoint routing that reaches your machine.",
    ],
    "before_extra": [
        {"table": (["Store", "Holds", "Owned by"], [
            ["Blob Storage", "Original files and extraction inputs", "The ingestion application"],
            ["Azure AI Search", "Chunks, searchable fields, embeddings, access metadata", "The retrieval application"],
            ["Cosmos `enterprise_memory`", "Service-managed agent state in a standard BYO setup", "The Foundry runtime"],
            ["Cosmos `workshop-memory`", "This exercise's conversation, preferences and vectors", "Your application"],
        ])},
        {"warn": "Never create, edit, delete or impose TTL on the service-owned `enterprise_memory` containers. "
                 "This exercise only ever reads their metadata."},
    ],
    "sections": [
        {
            "h2": "Prepare the database (instructor)",
            "intro": ["These commands create billable resources. Run them once per classroom, not per learner."],
            "steps": [
                [{"code": """$rg = 'YOUR-RESOURCE-GROUP'
$account = 'YOUR-COSMOS-ACCOUNT'
az cosmosdb sql database create -g $rg -a $account -n workshop-memory
az cosmosdb sql container create -g $rg -a $account -d workshop-memory -n sessions `
  --partition-key-path /userId --ttl -1
az cosmosdb sql container create -g $rg -a $account -d workshop-memory -n vectors `
  --partition-key-path /userId --vector-embeddings '@data/vector-policy.json' --idx '@data/index-policy.json'""",
                  "lang": "powershell"}],
                ["`--ttl -1` enables *item-level* TTL with no default expiry, so each document decides its own "
                 "lifetime. The scripts then set TTL per item."],
                ["Open `data/vector-policy.json` and `data/index-policy.json`. The policy uses **256 "
                 "dimensions** with cosine distance and a `flat` index.",
                 {"note": "256 fits within the flat index's dimension limit, and these are genuine shortened "
                          "`text-embedding-3-small` embeddings. For large collections, compare `quantizedFlat` "
                          "or DiskANN against representative data — not against three records."}],
            ],
        },
        {
            "h2": "Set up and read the identity model",
            "steps": [
                [{"code": f"cd \"{ADV}/lab19-cosmos-state-and-vectors\"\n" + SETUP_ADV, "lang": "powershell"}],
                [{"code": """COSMOS_ENDPOINT=https://YOUR-ACCOUNT.documents.azure.com:443/
AZURE_OPENAI_BASE_URL=https://YOUR-RESOURCE.openai.azure.com/openai/v1/
EMBEDDING_DEPLOYMENT_NAME=text-embedding-3-small""", "lang": "text"},
                 {"tip": "This exercise uses `AZURE_OPENAI_BASE_URL` — including the `/openai/v1/` path — and "
                         "`EMBEDDING_DEPLOYMENT_NAME`. Both differ from Exercise 18. Always copy this "
                         "exercise's own `.env.example`."}],
                ["Open `src/store.py`. The partition key is derived from a token the SDK acquired directly:",
                 {"code": """def signed_in_partition():
    token = credential.get_token('https://cosmos.azure.com/.default').token
    payload = token.split('.')[1]
    claims = json.loads(base64.urlsafe_b64decode(payload + '=' * (-len(payload) % 4)))
    return claims['tid'] + ':' + claims['oid']""", "lang": "python"},
                 {"warn": "Read the comment in the source carefully. This decodes a token **the credential just "
                          "obtained from Entra**, so its contents are trustworthy here. It is emphatically "
                          "**not** a validator for incoming web requests. A web API must validate signature, "
                          "issuer, audience and lifetime in middleware first — as Exercise 21 does — and use "
                          "that validated principal."}],
                ["Note that the partition is `tenant:object-id`, so identities from different tenants can never "
                 "collide."],
            ],
        },
        {
            "h2": "Prove persistence across processes",
            "steps": [
                ["Save state, then **let the process exit**:",
                 {"code": "python src/save.py", "lang": "powershell"},
                 {"code": """state.upsert_item({'id':'session-1', 'userId':user, 'ttl':3600,
                   'messages':[{'role':'user','content':'My synthetic case is ACME-204.'}]})
state.upsert_item({'id':'preferences', 'userId':user, 'ttl':86400,
                   'language':'English', 'style':'short answers'})""", "lang": "python"}],
                ["Now recover it in a **completely new process**:",
                 {"code": "python src/read.py", "lang": "powershell"},
                 {"ok": "ACME-204 and the preference come back. Nothing was held in memory between the two "
                        "commands — this is real durable state, unlike Exercise 14's in-process session."}],
                ["Notice the two different TTLs, which is the short- versus long-term memory distinction made "
                 "concrete:",
                 {"table": (["Item", "TTL", "Meaning"], [
                     ["`session-1`", "3,600 s", "Short-term: this conversation, valid for an hour"],
                     ["`preferences`", "86,400 s", "Long-term: how this person likes to be answered, for a day"],
                 ])}],
                ["Prove TTL actually expires things. Change the session TTL in `save.py` to `30`, run it, wait "
                 "at least 30 seconds, then run `read.py`.",
                 {"ok": "The session should be gone while the preference remains. There is no `try/except` "
                        "hiding the expected not-found error — you are meant to see it."},
                 "Restore `3600` afterwards."],
                ["Open the items in Data Explorer and inspect `_ts` and `ttl`. Capture the **request charge** "
                 "from Query Stats for a point read, then for a query, and compare them.",
                 {"note": "A point read needs both `id` and partition key and is the cheapest operation. A "
                          "cross-partition query is the most expensive. This is the RU cost model in one "
                          "comparison."}],
            ],
        },
        {
            "h2": "Test the isolation boundary honestly",
            "steps": [
                ["Sign in as a **different** identity with its own permitted access and run `read.py` *before* "
                 "saving anything.",
                 {"ok": "No session exists in that identity's partition. Then run `save.py` as that identity and "
                        "confirm it now has its own."}],
                ["Now state the limitation precisely, because this is the point most often got wrong:",
                 {"warn": "**A partition key improves routing; it is not row-level access control.** A "
                          "principal holding database-wide contributor access can query any partition. "
                          "Isolation here is enforced by the trusted application choosing the right partition, "
                          "not by the database refusing the request."}],
                ["It follows that production end users must never receive that database role or direct database "
                 "credentials. The application holds the data-plane role; the user authenticates to the "
                 "application. Exercise 21 shows that shape."],
            ],
        },
        {
            "h2": "Query vectors in Cosmos",
            "steps": [
                [{"code": "python src/vectors.py", "lang": "powershell"},
                 "Three synthetic records are embedded at 256 dimensions and upserted, then queried:",
                 {"code": """SELECT TOP 2 c.id, c.text, VectorDistance(c.embedding, @vector) AS distance
FROM c ORDER BY VectorDistance(c.embedding, @vector)""", "lang": "sql"}],
                [{"ok": "For the recycling question, the bin record should rank first."}],
                ["Note that the query passes `partition_key=user`, so the vector search runs **within one "
                 "identity's partition**. Vector similarity and access scoping compose here rather than "
                 "fighting each other."],
                ["The same rule from Exercise 17 applies: documents and query must use the same embedding model "
                 "and dimensions. Changing the vector policy requires a new compatible container and a "
                 "re-index — not an environment-variable change."],
            ],
        },
        {
            "h2": "Inspect the service-owned store (instructor-led)",
            "intro": [
                "Point `COSMOS_ENDPOINT` at the approved bring-your-own account **temporarily**, then restore it.",
            ],
            "steps": [
                [{"code": "python src/inspect_byo.py", "lang": "powershell"},
                 "This reads container names, partition paths and TTL metadata only. It never reads another "
                 "user's conversation content."],
                ["Standard setup uses the `enterprise_memory` database. Container names depend on the runtime "
                 "version — a classic runtime shows containers such as `thread-message-store`, "
                 "`system-thread-message-store` and `agent-entity-store`, while newer runtime state uses "
                 "`agent-definitions-v1` and `run-state-v1`.",
                 {"warn": "Record what *your* account actually shows. Do not assume a container list from "
                          "documentation."}],
                ["Now reconcile the throughput question, which is genuinely inconsistent in the published guidance:",
                 {"warn": "Current standard-setup documentation states a **3,000 RU/s account limit** and also "
                          "describes **five containers at 1,000 RU/s each**, while its troubleshooting section "
                          "still references three containers. Before provisioning, check your selected "
                          "runtime's actual template, container count and provisioned offers. Do not present "
                          "3,000 RU/s as sufficient for every topology."}],
                ["Also record which billing mode the account uses. Serverless consumption and provisioned RU/s "
                 "are different cost models and are not comparable line by line."],
                ["Restore your `COSMOS_ENDPOINT` to the lab account."],
            ],
        },
        {
            "h2": "Make the architecture decision",
            "intro": ["Record these decisions in a local `data/evidence.md` with your measured outputs attached."],
            "steps": [
                [{"table": (["Choose", "When"], [
                    ["**Cosmos** as vector store",
                     "Operational JSON and vector similarity belong together with your application data, "
                     "queried within one partition."],
                    ["**Azure AI Search**",
                     "Document ingestion pipelines, skillsets, hybrid and semantic retrieval, reranking and "
                     "search-specific features — this course's document use case."],
                ])}],
                ["Distinguish managed memory from custom RAG: managed memory is runtime-owned state; custom RAG "
                 "is retrieval your application performs. Neither automatically provides cross-session "
                 "preferences, and neither grants access to documents."],
                ["State the point that ties this back to Exercise 14:",
                 {"note": "Persisting a conversation does **not** give the model memory. After `read.py`, your "
                          "application must decide what to pass into the next run. The database stores; the "
                          "application remembers."}],
                ["Attach your evidence: save and read output, the TTL expiry result, the vector ranking, and "
                 "the request charges you captured."],
            ],
        },
    ],
    "knowledge_check": [
        {"q": "Why is `/userId` as a partition key not, by itself, authorisation?",
         "options": ["A. It is — Cosmos enforces it per user",
                     "B. Partitioning routes data; the application must constrain access using verified identity",
                     "C. Because it is a string"],
         "answer": "B",
         "why": "A principal with database-wide access can query any partition. Isolation depends on the "
                "trusted application choosing the partition."},
        {"q": "Why do original files and vectors live in different stores?",
         "options": ["A. Cost only", "B. Their ingestion, retrieval and persistence responsibilities differ",
                     "C. They must not — one store is always better"],
         "answer": "B",
         "why": "Blob holds originals, Search holds retrievable chunks and embeddings, Cosmos holds application "
                "or runtime state. Each has a different access and lifecycle model."},
        {"q": "Does persisting a conversation in Cosmos give the model memory?",
         "options": ["A. Yes, automatically", "B. No — the application must select and supply the saved context",
                     "C. Only with TTL enabled"],
         "answer": "B",
         "why": "The model is stateless. Storage makes recall *possible*; your code makes it happen."},
    ],
    "summary": [
        "You persisted agent state in Cosmos DB partitioned by a token-derived identity, recovered it in a "
        "separate process, watched TTL expire a short-term session while a long-term preference survived, ran a "
        "vector query scoped to one partition, and inspected the service-owned `enterprise_memory` metadata.",
        "You also reconciled the conflicting RU/s guidance against your actual account, and recorded when to "
        "choose Cosmos vectors over Azure AI Search.",
    ],
    "cleanup": [
        "Run clean-up only after completing both the save and vector steps:",
        {"code": "python cleanup.py", "lang": "powershell"},
        "It removes the fixed synthetic items in the **current identity's** partition only. A missing item "
        "raises visibly, including after a TTL expiry — remove any remaining IDs in Data Explorer if needed.",
        {"warn": "The instructor removes the dedicated `workshop-memory` database after review, once no other "
                 "participant needs it. Never delete `enterprise_memory`."},
    ],
    "refs": [
        ("Cosmos DB vector search", "https://learn.microsoft.com/azure/cosmos-db/nosql/vector-search"),
        ("Time to live", "https://learn.microsoft.com/azure/cosmos-db/nosql/time-to-live"),
        ("Standard agent setup", "https://learn.microsoft.com/azure/foundry/agents/concepts/standard-agent-setup"),
    ],
}


LAB20 = {
    "num": "20",
    "slug": "20-hosted-tools-and-integrations",
    "short": "Host tools and connect integrations",
    "group": "Advanced — client engineering",
    "track": "Advanced",
    "module_tags": ["Module 6", "Module 7"],
    "title": "Host a tool on Azure Functions and connect it through MCP, OpenAPI and connectors",
    "minutes": 120,
    "lab_path": f"{ADV}/lab20-hosted-tools-and-integrations",
    "env_note": "`azure-functions==1.24.0`, `mcp==1.26.0`, `openai==2.26.0`; needs Functions Core Tools v4",
    "blurb": "Build an authenticated HTTP tool, enforce an app role, expose it over MCP, and compare OpenAPI, "
             "Toolbox, Logic Apps and A2A integration paths.",
    "intro": [
        "Exercise 05 dispatched tools inside your own process. This exercise moves the tool to a **separate, "
        "authenticated service** — which is what production actually looks like — and then connects to it four "
        "different ways.",
        "The core build takes about two hours and everyone can complete it locally. Steps 9 to 11 are guided "
        "tenant extensions (Toolboxes, Logic Apps, agent-to-agent) that need prepared connections and "
        "permissions; label them explicitly as walkthroughs if your tenant cannot support them.",
    ],
    "objectives": [
        "Explain where a tool executes: the model proposes, the application invokes a separate host.",
        "Enforce an application role on an HTTP tool and return correct status codes.",
        "Call the tool with an Entra token from an agent's function-calling loop.",
        "Discover and invoke the same tool over MCP.",
        "Compare MCP, OpenAPI, Toolboxes, Logic Apps and A2A as integration paths.",
    ],
    "prereqs": [
        "Python 3.11 and **Azure Functions Core Tools v4**.",
        "For the cloud steps: a Python Function app, an API app registration, and someone with "
        "role-assignment rights.",
        "For the model step: a chat deployment and **Cognitive Services OpenAI User**.",
    ],
    "before_extra": [
        {"warn": "Azure Functions Core Tools does **not** emulate Easy Auth. Local runs use a synthetic "
                 "principal header purely to exercise the handler's logic. That proves code behaviour, never "
                 "authentication."},
    ],
    "sections": [
        {
            "h2": "Set up",
            "steps": [
                [{"code": f"cd \"{ADV}/lab20-hosted-tools-and-integrations\"\n" + SETUP_ADV,
                  "lang": "powershell"}],
                ["Create a local-only `local.settings.json` and keep it untracked:",
                 {"code": '{"IsEncrypted":false,"Values":{"FUNCTIONS_WORKER_RUNTIME":"python"}}', "lang": "json"},
                 {"tip": "This HTTP exercise has no storage binding. If your local host insists on one, run "
                         "Azurite and set `AzureWebJobsStorage` to `UseDevelopmentStorage=true`."}],
                ["Leave `ORDER_TOOL_URL` pointing at localhost for now. Fill the model values only when you "
                 "reach step 3."],
                ["Run both offline validators:",
                 {"code": "python validate.py\npython validate_http.py", "lang": "powershell"},
                 {"ok": "The first exercises the real handler for 401, missing-role 403, wrong-role 403, "
                        "authorised 200, missing-order 404 and the OpenAPI security declaration. The second "
                        "runs the real HTTP client against that handler through a loopback test server."}],
            ],
        },
        {
            "h2": "Read the authorisation logic",
            "intro": ["Open `function_app.py`. It is about twenty lines, and every branch is a deliberate "
                      "service boundary rather than generic error handling."],
            "steps": [
                [{"code": """principal_header = req.headers.get('X-MS-CLIENT-PRINCIPAL')
if not principal_header:
    return func.HttpResponse('Authentication required', status_code=401)
principal = json.loads(base64.b64decode(principal_header))
roles = [claim['val'] for claim in principal['claims']
         if claim['typ'] == principal.get('role_typ', 'roles')]
if 'Orders.Read' not in roles:
    return func.HttpResponse('Orders.Read required', status_code=403)""", "lang": "python"}],
                [{"table": (["Condition", "Status", "Meaning"], [
                    ["No principal header", "401", "Not authenticated"],
                    ["Principal without `Orders.Read`", "403", "Authenticated but not authorised"],
                    ["Unknown order ID", "404", "Authorised, but no such record"],
                    ["Authorised and found", "200", "Returns the order"],
                ])},
                 {"note": "401 and 403 are genuinely different answers and should never be collapsed. One says "
                          "*who are you*, the other says *you may not*."}],
                ["Now the question this trigger always provokes:",
                 {"code": "app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)", "lang": "python"},
                 {"warn": "`ANONYMOUS` is correct here because **Easy Auth authenticates before the trigger "
                          "runs** and supplies the principal header. It is absolutely not permission to deploy "
                          "this without platform authentication configured. A deployed function with ANONYMOUS "
                          "and no Easy Auth is an open endpoint."}],
            ],
        },
        {
            "h2": "Run the tool locally and call it from an agent",
            "steps": [
                ["In **terminal A**, start the function host:",
                 {"code": "func start", "lang": "powershell"}],
                ["In **terminal B**, call it:",
                 {"code": "python src/call_tool.py", "lang": "powershell"},
                 {"ok": "Expect the synthetic order ACME-204 with status `Scheduled`."}],
                ["Read how the client chooses its authentication path — the local branch is deliberately fenced "
                 "off:",
                 {"code": """if urlparse(url).hostname in ('localhost', '127.0.0.1'):
    # Synthetic local fixture only: this is not authentication.
    principal = {'role_typ':'roles', 'claims':[{'typ':'roles','val':'Orders.Read'}]}
    headers['X-MS-CLIENT-PRINCIPAL'] = base64.b64encode(...).decode()
else:
    assert urlparse(url).scheme == 'https'
    token = DefaultAzureCredential().get_token(os.environ['TOOL_SCOPE']).token
    headers['Authorization'] = 'Bearer ' + token""", "lang": "python"},
                 "The synthetic header is only ever injected for loopback, and the cloud path asserts HTTPS "
                 "before attaching a token."],
                ["Now run the agent, which ties Exercise 05's loop to this separate host:",
                 {"code": "python src/agent.py", "lang": "powershell"},
                 {"bullets": [
                     "The first Responses request offers exactly one function and forces its selection.",
                     "The application asserts the returned call name matches what it exposes, then makes the "
                     "HTTP call itself.",
                     "The second request supplies the result as a `function_call_output`.",
                 ]},
                 {"note": "The model never executes Python and never sees the bearer token. It receives a "
                          "schema and returns a request; your application holds the credential."}],
                ["Note the deliberate narrowness: only the fixed synthetic order is exposed. Extending this to "
                 "arbitrary customer IDs would require object-level access checks, not just the role check."],
                [{"warn": "Never expose Core Tools or the local MCP server to a shared or public network."}],
            ],
        },
        {
            "h2": "Deploy and test real authentication (instructor-supported)",
            "steps": [
                ["Create or select a dedicated Python Function app. Under **Authentication**, add Microsoft "
                 "Entra with a single-tenant registration, require authentication, and return HTTP 401 for "
                 "unauthenticated API requests. Set the exact intended audience, issuer and caller restrictions."],
                ["In the API registration, define the app role `Orders.Read` for **Users/Groups and "
                 "Applications**. Assign the learner through Enterprise Applications, and assign the calling "
                 "service principal or managed identity the same role."],
                ["For delegated local calls, expose a scope such as `Orders.Access` and authorise the developer "
                 "client with the required consent.",
                 {"note": "`TOOL_SCOPE=api://<API-client-id>/.default` requests **your API**, not Microsoft "
                          "Graph and not the model API. An app role assignment and a delegated scope solve "
                          "different problems; you generally need both."}],
                ["Publish and repoint:",
                 {"code": "func azure functionapp publish YOUR-FUNCTION-APP", "lang": "powershell"},
                 "Set `ORDER_TOOL_URL` to the HTTPS function URL and `TOOL_SCOPE` correctly, then run "
                 "`python src/call_tool.py` again. `DefaultAzureCredential` now uses your developer identity, "
                 "or a managed identity when hosted."],
                ["Test the deployed security properly and record the **status codes**, not the tokens:",
                 {"bullets": [
                     "Unsigned request → must fail.",
                     "Authenticated caller without `Orders.Read` → must fail.",
                     "Correctly assigned caller → must succeed.",
                     "A fabricated `X-MS-CLIENT-PRINCIPAL` header **with no bearer token** → the platform must "
                     "reject it before your code runs.",
                 ]},
                 {"warn": "If that last fabricated header reaches your handler, stop. It means Easy Auth is not "
                          "actually enforcing, and the entire authorisation model is bypassed."}],
                [{"tip": "Role changes usually require a fresh token. Sign out and back in rather than "
                         "concluding the assignment failed."}],
            ],
        },
        {
            "h2": "Expose the same tool over MCP",
            "steps": [
                ["Look at how little it takes to publish the tool over MCP:",
                 {"code": """mcp = FastMCP('Council orders', host='127.0.0.1', port=8000)
mcp.tool()(get_order_status)""", "lang": "python"},
                 "The docstring and type hints on `get_order_status` become the tool's description and schema."],
                ["Start the server in **terminal C**:",
                 {"code": "python src/mcp_server.py", "lang": "powershell"}],
                ["Discover and invoke it from **terminal B**:",
                 {"code": "python src/mcp_client.py", "lang": "powershell"},
                 {"ok": "`list_tools()` should return `get_order_status` with its description, and "
                        "`call_tool()` should return the ACME-204 record."}],
                ["Three limitations to record, because they decide whether this pattern is deployable:",
                 {"bullets": [
                     "The MCP server calls the Function with **its own** configured credential. The end user's "
                     "identity does not flow through.",
                     "It binds to loopback. A cloud-hosted agent cannot reach your laptop.",
                     "A remotely hosted MCP service needs its own HTTPS, authentication and network controls — "
                     "it does not inherit the Function's.",
                 ]},
                 {"note": "Exercise 10 was the client side of MCP against a public server. This is the server "
                          "side, wrapping an internal authenticated API."}],
            ],
        },
        {
            "h2": "Compare the integration paths",
            "steps": [
                ["Open `data/openapi.json`. Find the `operationId`, the route, the parameter and the bearer "
                 "security scheme:",
                 {"code": '"security": [{"bearerAuth": []}]', "lang": "json"},
                 {"warn": "A schema *declares* that a token is required. It does not obtain one and does not "
                          "validate one. Declaration and enforcement are different things."}],
                [{"table": (["Path", "Discovery", "Best suited to"], [
                    ["Function calling", "You declare the schema in code", "Tools your own application owns"],
                    ["MCP", "Runtime `tools/list` discovery", "Evolving tool sets across several agents"],
                    ["OpenAPI", "Explicit, versioned contract", "Existing REST APIs with a published spec"],
                    ["Toolbox", "Register once, discover at runtime", "Reuse of one tool across many agents"],
                    ["Logic Apps", "Connector-based", "Workflows across SaaS and line-of-business systems"],
                    ["A2A", "Agent card and task protocol", "Delegating a whole task to another agent"],
                ])}],
                ["**Guided Toolbox extension.** In the Foundry Toolkit, expand project Tools, add a toolbox and "
                 "add your instructor's reachable authenticated MCP connection. Publish a version, copy the "
                 "consumer endpoint, authenticate to it and list tools. Then create a *second* agent using the "
                 "same endpoint to demonstrate reuse. Record the version, tool and result.",
                 {"warn": "Do not register localhost as a cloud endpoint. Also note that tool *search* is a "
                          "separate optional routing feature — ordinary `tools/list` discovery does not "
                          "demonstrate intent-based search."}],
                ["**Guided Logic Apps extension.** Create a dedicated workflow with an approved request trigger, "
                 "an authenticated HTTP action calling this Function, and a Response action. Give its managed "
                 "identity the API role and set the action's audience. Run it with ACME-204 and inspect the run "
                 "history. Record the workflow execution separately from the agent integration."],
                ["**Guided A2A extension.** Using an instructor-provided authenticated A2A endpoint, inspect its "
                 "agent card and declared skills, connect through the documented Foundry A2A tool, submit one "
                 "synthetic enquiry, and inspect the task state and final artifact.",
                 {"warn": "An HTTP JSON endpoint is not A2A, and neither are two local agents talking to each "
                          "other. Without real agent-card and task evidence, record this as a walkthrough only."}],
                ["If an integration cannot use the required authentication, record the blocker and keep the "
                 "authenticated function-calling path.",
                 {"warn": "Never weaken the API to make an import succeed."}],
            ],
        },
    ],
    "knowledge_check": [
        {"q": "Does declaring a function schema host the tool?",
         "options": ["A. Yes, the model runs it", "B. No — the application or a separate service executes it",
                     "C. Only for OpenAPI"],
         "answer": "B",
         "why": "A schema describes an interface. Execution happens at the tool's own service boundary, under "
                "its own identity."},
        {"q": "Why can the local principal fixture not prove authentication?",
         "options": ["A. Core Tools accepts whatever header you supply; only deployed Easy Auth validates a token",
                     "B. Because it uses JSON", "C. It can, if the role name is correct"],
         "answer": "A",
         "why": "The local test proves your authorisation *logic*. It says nothing about token validation."},
        {"q": "Does registering a tool in a Toolbox move the tool's code into the model?",
         "options": ["A. Yes", "B. No — it centralises configuration and discovery; execution stays at the tool",
                     "C. Only for MCP tools"],
         "answer": "B",
         "why": "Toolboxes solve reuse and discovery, not hosting."},
    ],
    "summary": [
        "You built an HTTP tool that returns 401, 403, 404 and 200 correctly, ran it locally, called it from an "
        "agent's function-calling loop without the model ever seeing a token, exposed the same function over "
        "MCP, and compared six integration paths.",
        "You also established the rule that governs all of them: declaring an interface is not hosting, and a "
        "local fixture is not authentication.",
    ],
    "cleanup": [
        "Stop both local servers with Ctrl+C, then:",
        {"code": "python cleanup.py", "lang": "powershell"},
        "The instructor removes only the dedicated Function app, hosting and storage resources, any optional "
        "workflow, Toolbox versions and connections, and lab-only identity assignments. No script deletes "
        "shared resources.",
        {"warn": "Before sharing anything, remove `.env`, `local.settings.json` and any diagnostic file that "
                 "might contain a token. Never paste bearer tokens or full principal headers into your evidence."},
    ],
    "refs": [
        ("Functions Python model", "https://learn.microsoft.com/azure/azure-functions/functions-reference-python"),
        ("Configure Entra authentication",
         "https://learn.microsoft.com/azure/app-service/configure-authentication-provider-aad"),
        ("Platform principal headers",
         "https://learn.microsoft.com/azure/app-service/configure-authentication-user-identities"),
        ("Create and consume Toolboxes",
         "https://learn.microsoft.com/azure/foundry/agents/how-to/tools/toolbox"),
        ("Foundry OpenAPI tools", "https://learn.microsoft.com/azure/foundry/agents/how-to/tools/openapi"),
        ("Foundry A2A tools", "https://learn.microsoft.com/azure/foundry/agents/how-to/tools/agent-to-agent"),
    ],
}

LABS = [LAB17, LAB18, LAB19, LAB20]
