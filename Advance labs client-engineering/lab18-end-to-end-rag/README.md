# Lab 18 — Build and measure a connected RAG pipeline

**150 minutes, in three parts.** Build with short Python scripts: source PDF → extracted text → chunks → embeddings → Search → retrieved passages → cited answer. Existing Lab07 separately implements the **managed indexer + Text Split skill + embedding skill** alternative. Here every intermediate artifact is visible, and updates/deletions follow the same pipeline.

## Outcomes and prerequisites

- Inspect real PDF text and compare fixed overlap with paragraph-preserving chunks.
- Generate real 1,536-dimensional embeddings; store vectors alongside text, source, page and ACL metadata.
- Compare keyword, vector, hybrid and semantic retrieval against labelled questions.
- Add, change and remove a source; verify stale chunks disappear.
- Exercise an image-only document with Document Intelligence OCR (optional Azure service).

Use Python 3.11+, `az login`, a dedicated Search index name starting `lab18-`, Search semantic ranker enabled, an Azure OpenAI resource with `text-embedding-3-small` and a Responses-compatible model. Roles: Search Service Contributor for schema changes, Search Index Data Contributor for data/query access, and Cognitive Services OpenAI User on the model resource. Optional OCR needs Document Intelligence access. Resources must be reachable from the learner machine. These scripts create an index and issue billable embedding, retrieval, model and optional OCR requests when **you** run the cloud steps. No cloud resources were modified while authoring this lab.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Fill your resource values, then:
python validate.py
```

The embedding endpoint is the Azure OpenAI **resource** URL. It is not the Foundry project endpoint. Text and query vectors must use the same model and dimensions. When changing the embedding deployment/model or dimensions, build a fresh compatible index and checkpoint; the incremental manifest detects source changes, not model changes. [Embedding API](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/embeddings), [SDK endpoints](https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/sdk-overview).

## Part A — Extraction, chunking, indexing (50 minutes)

1. Inspect `data/sources.json`: this is the authoritative source list and its ACL metadata. Open a supplied PDF and locate the answers in `data/questions.json`. All documents are synthetic ACME training policies; no resident data is present.
2. Extract and inspect `data/chunks.json`:

   ```powershell
   python src/ingest.py --strategy fixed
   python src/index.py
   python src/sync.py
   python src/query.py "How many annual leave days do full-time staff receive?" --answer
   ```

   Each chunk has a stable ID based on source/page/ordinal. The vector is generated during sync, not stored in the source file. A 1,536-float vector is a mathematical representation, not readable text. Source/page fields make citations possible; `allowed_groups` makes filtering possible. Search results can take a short time to become queryable after writes; rerun the query after the service has indexed the changes.
3. Run `python src/measure.py`. Save the printed baseline or copy its JSON report outside the report's current filename. Re-run `ingest.py --strategy paragraph`, then `sync.py` and `measure.py`. Compare chunk count, precision, recall and reciprocal rank.

The fixed strategy uses 500 **characters** with 80-character overlap, not tokens. The paragraph strategy groups PDF text blocks and preserves whole blocks, so a long block can exceed the target. Neither is semantic/heading-aware chunking; discuss a heading-aware extension that carries the current section title into each chunk. On this tiny corpus the strategies may tie. Do not invent improvement. [Chunking guidance](https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-chunk-documents), [vector index schema](https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-create-index).

**Managed comparison:** complete existing [Lab07 integrated vectorisation](../../day2-foundry-sdk-tools-and-rag/lab07-search-integrated-vectorization/README.md) using its own fixture. To pass your extracted output into that managed pipeline, copy this lab's `data/chunks.json` to Lab07's `data/chunks.json` before running its `src/demo.py` (back up its original fixture first); it uploads these records as JSON blobs. The field names are compatible. Use a fresh Lab07 resource name for this comparison so its earlier uploaded blobs cannot mix with this corpus. Restore its fixture when finished. The managed skillset may split the already small chunks again; compare this double-split boundary with passing full extracted pages. Lab07's managed index is separate from this lab's push index. [Integrated vectorization](https://learn.microsoft.com/en-us/azure/search/vector-search-integrated-vectorization).

## Part B — Freshness and scanned records (40 minutes)

```powershell
python src/freshness.py add
python src/ingest.py
python src/sync.py
python src/query.py "When does the service desk close on Fridays?" --answer
python src/freshness.py update
python src/ingest.py
python src/sync.py
python src/query.py "When does the service desk close on Fridays?" --answer
python src/freshness.py delete
python src/ingest.py
python src/sync.py
python src/query.py "When does the service desk close on Fridays?" --answer
```

Expected: add gives **4 pm**, update gives **6 pm**, delete leaves no source supporting an answer. Inspect result sources, not just generated prose. Run sync again: zero uploads and zero deletes. Reduce a source's chunk count: obsolete ordinal IDs are deleted as well. Changing `allowed_groups` is a content-manifest change and causes a document update. The local `<index>-manifest.json` is a teaching checkpoint for **one writer**, not a distributed scheduler or transaction log; keep it with the index and rerun safely after an interrupted sync. If the index is recreated, remove its old local manifest before sync. [Indexing and deletion](https://learn.microsoft.com/en-us/azure/search/search-howto-reindex).

**OCR extension:** run `python src/scanned.py`. It rasterises the existing synthetic PDF into `data/scanned-conduct.pdf`; it contains images and no embedded text. Add it to `sources.json` with `allowed_groups: ["staff"]`. Normal ingestion deliberately reports missing text. Run `python src/ingest.py --ocr`, then sync. Document Intelligence `prebuilt-read` processes the actual PDF bytes and retains page numbers. Remove the extra source from the manifest and ingest/sync before comparing the original benchmark again. Use only PDF sources for this OCR extension: remove `service-hours.txt` via `freshness.py delete` first. Local PyMuPDF extraction is **not OCR**. OCR line grouping is also not layout-aware paragraph segmentation. [Document Intelligence Python SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-documentintelligence-readme?view=azure-python).

## Part C — Retrieval quality and security boundaries (60 minutes)

`measure.py` queries the actual index four times per question: keyword, vector, hybrid and semantic. Only the question and groups enter Search. Relevant source labels are used **after retrieval**, never inserted into model context. Reports record the dataset SHA-256 and expected/retrieved source IDs. `data/retrieval-report.json` records the semantic retrieval experiment. It is not a Lab23 release report: Lab23 requires its own 20-case corpus, answer judgments and revision metadata.

We measure at the **unique source-document level**, deduplicating chunks:

- Precision@5 = relevant retrieved sources / 5. Missing result slots count as misses.
- Recall@5 = relevant retrieved sources / all labelled relevant sources.
- MRR = mean reciprocal position of the first relevant source (within the first five).

There are only three source documents, with one relevant source per question: maximum precision@5 here is **0.2**. This is a formula lesson and integration check, not a representative quality benchmark. Add many distractors, multi-document questions and a held-out labelled set before making production claims. Rerank improvements are not guaranteed. Groundedness is a **separate answer metric**: compare the generated answer's claims with the actual retrieved passages, then extend the existing evaluation lab. A correct retrieval score does not prove a grounded answer. [Hybrid search](https://learn.microsoft.com/en-us/azure/search/hybrid-search-overview), [semantic ranking](https://learn.microsoft.com/en-us/azure/search/semantic-search-overview).

The CLI intentionally uses synthetic `staff` groups. It authenticates the **application's Search access** using Entra; it does not sign in a resident. Change a source to `hr`, ingest/sync, and verify `staff` queries exclude it. Call `retrieve(question, [], 'hybrid')` in a short script: expect no results. Restore original ACLs and ingest/sync afterward.

For an actual web application, the authenticated backend must validate token signature, issuer, audience and lifetime, resolve group overage using the approved identity path, then pass trusted memberships to `retrieve`. An unverified decoded JWT or a browser-supplied group list is not sufficient. Do not deploy this CLI as a user-facing security boundary. Combine with [Lab08 secure retrieval](../../day2-foundry-sdk-tools-and-rag/lab08-secure-rag/README.md); [Lab21](../lab21-agent-web-application/README.md) supplies a signed-token web application with a separate GUID-based index. Mapping this pipeline to that schema remains an integration exercise. [Security filters](https://learn.microsoft.com/en-us/azure/search/search-security-trimming-for-azure-search).

## Evidence, cleanup and knowledge check

Keep a chunk comparison, add/update/delete console results, authorised/denied query results and the actual retrieval reports. Offline validation proves the Python data mechanics only; live OCR, indexing, retrieval quality and answer behaviour require Azure rehearsal.

Run `python cleanup.py` to delete only the named `lab18-` Search index and its checkpoint. Shared services and deployments remain. Delete generated reports locally when no longer needed; do not commit live text or credentials.

1. Why must an updated document with fewer chunks remove old IDs? **Otherwise stale passages remain retrievable.**
2. Does high recall prove the generated answer is grounded? **No; retrieval and answer quality are different measurements.**
3. Can a client supply its own `allowed_groups` query parameter? **No; permissions must come from trusted, validated identity.**


