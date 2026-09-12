# Synthetic training data

All Acme organisation names, policies, people, orders and email addresses are fictional. The policy values are teaching fixtures, not statements of Australian employment law. Monetary values are AUD and timestamps use AEST (+10:00).

Run `python shared/generate_assets.py` from the repository root to recreate 25 orders, 5 profiles, 3 PDFs, 20 text chunks and 20 evaluation questions. The lab folders contain their own copies, so no previous lab execution is required. Source content, JSON and PDF generation use fixed inputs; optional Microsoft downloads are excluded from the deterministic corpus.

Microsoft samples are optional references, not relicensed by this workshop. Review the original repository licence and any file-specific terms before reuse or redistribution. `shared/download_ms_samples.py` gracefully retains the bundled synthetic alternatives if a download fails.
