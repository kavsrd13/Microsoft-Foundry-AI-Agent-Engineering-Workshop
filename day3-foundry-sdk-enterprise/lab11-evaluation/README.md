# Evaluate answers against a rubric — 90 minutes

## Status badges (GA/Preview/Prerelease)

Foundry SDK and evaluation package: GA. ContentSafetyEvaluator class: EXPERIMENTAL. Individual evaluator availability is regional.

## Learning objectives

- Generate candidate answers for 20 labelled examples
- Apply an explicit rubric before secondary metrics
- Interpret judge limitations and regional restrictions

## Prerequisites

Foundry project and candidate/rubric deployments; Foundry User plus evaluator permissions for the service; Cognitive Services OpenAI User on the judge account. Reserve quota for 20 candidate calls, 20 rubric calls and 80 secondary evaluator invocations (composites may use more). Python 3.11, a fresh virtual environment, Azure CLI sign-in and generated synthetic assets. No API keys. Infrastructure is supplied by the instructor; this lab owns only the objects explicitly recorded in its data directory.

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

1. Open the 20 rows in `data/qa_dataset.jsonl`. Each has a question, reference answer, context and expected source.
2. Read `src/evaluate.py`. It generates an actual candidate answer from context; it does not copy the ground truth into the response field.
3. Read the primary 1–5 rubric. A separate model call judges factual accuracy, completeness, citations and unsupported claims. Keep the rubric deployment distinct from the candidate when quota permits.
4. Groundedness checks claims against context; relevance checks the question; fluency checks language; content safety uses the real service evaluator.
5. Run all 20 rows and inspect both `data/scores.json` and `data/score-report.md`. A failure preserves the completed rows but the report is incomplete until 20 rows exist.
6. Manually review the lowest scores and disagree with a judge where source evidence warrants it. No automatic production release threshold is claimed.

## Run & expected output

```powershell
python src/evaluate.py
```

Expect `Evaluated 1/20` through `Evaluated 20/20`, then review the saved Markdown report. Scores are observations, not guaranteed values. Safety service unavailability is a failed live evaluation, never a fabricated passing score.

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

1. Which judgement is primary? A. Fluency B. Explicit task rubric C. Response length
2. What does groundedness compare? A. Claims and supplied context B. Token count and cost C. Region and tenant
3. Does an unavailable safety service count as a pass? A. Yes B. Only for synthetic data C. No

Answer key: **1 B**, **2 A**, **3 C**.

## Stretch challenge

Change the candidate prompt to omit citations and compare rubric scores while preserving the same dataset and judge deployment.

## References

- [Primary Microsoft Learn article](https://learn.microsoft.com/azure/foundry/observability/how-to/evaluate-agent)
- [Required GitHub sample path](https://github.com/Azure-Samples/Agentic-Evaluations)
- [Australian considerations](../../AUSTRALIA-RESIDENCY.md)
