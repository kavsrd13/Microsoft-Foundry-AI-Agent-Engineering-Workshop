# Foundry IQ — 45 minutes

## Status badges (GA/Preview/Prerelease)

Search text and 2026-04-01 minimal extractive retrieval: GA. Portal, query planning and synthesis: PREVIEW.

## Learning objectives

- Distinguish knowledge sources from knowledge bases
- Compare extractive retrieval and planned retrieval
- Inspect returned references and access boundaries

## Prerequisites

Search service with semantic ranker and Entra auth; Search Service Contributor to create lab objects and Search Index Data Contributor to load synthetic content; Search Index Data Reader to query. Preview requires an available supported planning model. Use the standalone portal instructions. Python 3.11, a fresh virtual environment, Azure CLI sign-in and generated synthetic assets. No API keys. Infrastructure is supplied by the instructor; this lab owns only the objects explicitly recorded in its data directory.

## Australian/residency note

Australia East supports Foundry projects. Verify model, tool and evaluator availability individually. Deployment type (Global / Data Zone / Regional), not resource location, determines processing geography. Use only synthetic Acme Public Sector Pty Ltd data. An overseas judge or external MCP endpoint needs a separately approved data boundary.

## Setup steps

1. Open a terminal in this lab folder.
2. Create the environment and install the pinned dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
az login
```

3. Replace the placeholders in `.env`. A deployment name is not a model family name. Never commit `.env`.
4. Run `python validate.py` before any service call.

## Guided walkthrough with numbered steps and code explanation

1. Read `data/portal-walkthrough.md` and create an isolated knowledge source and knowledge base from the synthetic files in this lab. No other lab is required.
2. Read `src/retrieve.py`: one Entra token, one documented REST request, one JSON response. The GA request uses `intents` and returns extractive evidence.
3. Run with `--preview` only after checking permission to use preview planning and answer synthesis. Inspect references and activity in the returned JSON.
4. Run `src/search_fallback.py` against the independent lab index if IQ is unavailable. Its explicit group filter demonstrates application-enforced access; this is text retrieval, not agentic planning.
5. Compare the live response with `data/illustrative-output.md`. That file is a teaching illustration, never evidence of a successful service call.

## Run & expected output

```powershell
python src/retrieve.py
python src/retrieve.py --preview
python src/search_fallback.py
```

The retrieval script prints the genuine JSON response and saves `data/live-retrieval.json`; references identify retrieved evidence. The fallback prints source filenames and content. Preview behaviour depends on the configured knowledge base.

## Validation

`python validate.py` checks local syntax and assets without Azure. `python validate.py --live` checks the saved live artefact after running the demo; it is not a new cloud call. Pass criteria: no local failures, and the explicit live evidence check passes. For Lab 12, the instructor must also verify the trace in Application Insights. No tenant execution was performed while building this repository.

## Troubleshooting table

| Symptom | Likely cause and action |
|---|---|
| KeyError or placeholder endpoint | Fill the missing `.env` value and rerun from this lab. |
| 401 / credential unavailable | Run `az login` in the correct tenant; check identity selection. |
| 403 | Check the resource-scoped role, PIM activation and propagation; for private endpoints use a connected network. |
| 404 | Verify project URL, deployment name and lab knowledge resource name. |
| 429 | Check deployment quota; wait for Retry-After or reduce simultaneous classroom calls. |
| Timeout / DNS failure | Check private DNS, firewall and endpoint egress; do not bypass network controls. |
| Evaluator or preview feature unavailable | Check feature/region support; use the documented fallback with an explicit limitation. |

## Cleanup

Run `python cleanup.py`. It lists only known lab artefacts and prompts before deleting them. Repeating cleanup is safe. Shared Azure infrastructure is not deleted. Follow the additional ownership notes in `data/cleanup-notes.md`.

## Knowledge check

1. Which GA retrieval input does this lab use? A. intents B. messages C. tool_calls
2. Which feature is preview here? A. Text search B. Query planning and synthesis C. Entra auth
3. What identifies supporting evidence? A. A generated answer alone B. Response length C. Source references

Answer key: **1 A**, **2 B**, **3 C**.

## Stretch challenge

Compare the GA extractive response with preview synthesis on the same question. Annotate which claims have references.

## References

- [Primary Microsoft Learn article](https://learn.microsoft.com/azure/foundry/agents/concepts/what-is-foundry-iq)
- [Required GitHub sample path](https://github.com/microsoft/azure-ai-search-foundry-iq-live-knowledge-sources)
- [Australian considerations](../../AUSTRALIA-RESIDENCY.md)
