# Validation — 11 September 2026

Offline checks passed. No Azure resources were created or queried.

- `python -m compileall .`: chunk IDs and ACL inheritance, overlap, add/change/remove/no-op, unique-source metrics and empty-group denial. The real sync script runs against a recording fake: a rejected deletion preserves the old checkpoint; replay succeeds; the next run issues no writes. Checkpoints replace the old file only after all indexing results succeed.
- Executed ingestion on the supplied PDFs in a temporary copy: **9 fixed chunks, 7 paragraph chunks**. Executed the freshness script and re-ingestion for add (4 pm), update (6 pm) and removal. The extra source disappears after removal.
- Executed the scan generator and inspected every output page: images present, embedded text absent. This validates the OCR input, not the cloud OCR response.
- Imported Azure Search SDK **12.0.0** and Document Intelligence **1.0.2**. Constructed real `VectorizedQuery` objects and executed query construction against a fake Search client for all four retrieval modes. Verified k=50, pre-filtering and the empty-membership filter. Checked the Document Intelligence binary body parameter against the installed SDK.
- Rechecked Microsoft Learn vector query and standard-setup references. The linked Lab07 folder and JSON field bridge were verified against the actual files.

Live rehearsal must still prove Entra permissions, index creation, embedding generation, OCR extraction, eventual indexing visibility, retrieval scores and generated citations. No retrieval scores were fabricated. The CLI's synthetic groups are not end-user authentication.
