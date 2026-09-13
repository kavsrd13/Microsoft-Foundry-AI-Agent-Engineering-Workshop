# Tracing and Australian governance — 45 minutes

## Status badges (GA/Preview/Prerelease)

Azure Monitor distro and tracing service: GA. azure-core-tracing-opentelemetry 1.0.0b13: PRERELEASE.

## Learning objectives

- Create a real trace with nested spans
- Find the trace in Application Insights
- Document Australian deployment and data controls

## Prerequisites

Foundry project and model inference permission; Application Insights linked to the project, Monitoring Metrics Publisher for ingestion and Monitoring Reader to inspect traces. Python 3.11, a fresh virtual environment, Azure CLI sign-in and generated synthetic assets. No API keys. Infrastructure is supplied by the instructor; this lab owns only the objects explicitly recorded in its data directory.

## Australian/residency note

Australia East supports Foundry projects. Verify model, tool and evaluator availability individually. Deployment type (Global / Data Zone / Regional), not resource location, determines processing geography. Use only synthetic Acme Public Sector Pty Ltd data. An overseas judge or external MCP endpoint needs a separately approved data boundary.

## Setup steps

1. Open a terminal in this lab folder.
2. Create the environment and install the pinned dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Use the shared foundry-agent-workshop/.env file
az login
```

3. Replace the placeholders in `.env`. A deployment name is not a model family name. Never commit `.env`.
4. Run `python -m compileall .` before any service call.

## Guided walkthrough with numbered steps and code explanation

1. Assign Monitoring Metrics Publisher on the specific Application Insights resource to the signed-in identity. Configure ingestion to require Entra authentication.
2. Read `demo.py`: configure the exporter before spans, open a parent span, make the real model request inside a child span and flush on exit.
3. Note that spans store operation metadata, not the prompt or answer. Keep sensitive content recording disabled.
4. Open Application Insights Logs and run `trace-query.kql` using the printed trace ID. Inspect parent/child relationships with transaction diagnostics.
5. Complete every row of `au-governance-checklist.md`. Evidence links and owners are required; a checkbox alone proves no control.

## Run & expected output

```powershell
python demo.py
```

Expect a short answer and a 32-character trace ID. Exporter flush is not ingestion proof: find the same trace ID in Application Insights after ingestion delay.

## Validation

`python -m compileall .` checks local syntax and assets without Azure. `python -m compileall .` checks the saved live artefact after running the demo; it is not a new cloud call. Pass criteria: no local failures, and the explicit live evidence check passes. For Lab 12, the instructor must also verify the trace in Application Insights. No tenant execution was performed while building this repository.

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

Run `remove generated local files manually`. It lists only known lab artefacts and prompts before deleting them. Repeating cleanup is safe. Shared Azure infrastructure is not deleted. Follow the additional ownership notes in `cleanup-notes.md`.

## Knowledge check

1. What proves ingestion? A. A printed trace ID B. The matching trace in Application Insights C. An installed package
2. What determines model processing geography? A. Deployment type and its commitment B. Laptop timezone C. Python version
3. What should this lab record in spans? A. Citizen data B. Secrets C. Operation metadata

Answer key: **1 B**, **2 A**, **3 C**.

## Stretch challenge

Add a third child span for a local policy check. Confirm its parent ID and avoid logging policy contents.

## References

- [Primary Microsoft Learn article](https://learn.microsoft.com/azure/foundry/observability/how-to/enable-tracing)
- [Required GitHub sample path](https://github.com/microsoft-foundry/foundry-samples/tree/main/samples/python/external-agents/observability/)
- [Australian considerations](../../AUSTRALIA-RESIDENCY.md)
