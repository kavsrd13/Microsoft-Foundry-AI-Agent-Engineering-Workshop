# Instructor portal walkthrough (preview)

Use a fresh lab09 suffix such as `acme-lab09-knowledge-a1b2c3`. Record exact object names and owner before creating anything. Never reuse another group's index.

1. Open the Foundry project in the Foundry portal and locate Knowledge / Foundry IQ. Confirm that the project and Search connection are the intended tenant resources.
2. Select a new knowledge source. Use the synthetic PDFs in this lab's data directory, uploaded to a dedicated lab09 Blob container, or a dedicated lab09 Search index. The portal's supported source choices differ by region and release.
3. For the independent text-index fallback, create fields `id` (Edm.String key), `content` (searchable Edm.String), `source` (Edm.String retrievable), and `allowed_groups` (Collection(Edm.String), filterable). Load `chunks.json` using the supplied upload script. Give this disposable synthetic corpus `citizen-service` access; do not use confidential files.
4. Add a semantic configuration with `content` as the content field. Select that index as a search-index knowledge source.
5. Create a knowledge base using only the new knowledge source. For the GA path choose minimal/extractive settings without a planning model. For the preview demo select an approved supported planning model and answer synthesis. Record the knowledge base name in `.env`.
6. Ask: “What leave and travel rules apply to an Acme employee?” Inspect retrieval references, query activity, and the difference between extracted evidence and a synthesised answer.
7. Run the Python retrieval script against the same knowledge base. It uses the published Search REST endpoint rather than assuming a Foundry project knowledge method exists.
8. Save a sanitised live capture. Until this rehearsal happens, use the explicitly illustrative fallback, never describe it as recorded evidence.
9. Delete only the recorded lab09 knowledge base, knowledge source, index and optional Blob container in reverse order through the portal. Recheck each exact name before deletion. The Python scripts do not create these portal resources, so `manual cleanup instructions` only removes Python-owned outputs. Retain shared services and project connections.

Source: [Retrieve API status and examples](https://learn.microsoft.com/azure/search/agentic-retrieval-how-to-retrieve), [live-source sample repository](https://github.com/microsoft/azure-ai-search-foundry-iq-live-knowledge-sources).
