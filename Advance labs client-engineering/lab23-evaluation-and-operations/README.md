# Lab 23 — Retrieval evaluation, release gates and operations (120 minutes; split into short exercises)

## Status badges (GA/Preview/Prerelease)

Responses, Search core and Azure Monitor: GA paths. Model judges are probabilistic; service regions and optional managed evaluators must be verified separately.

## Learning objectives

- Evaluate answers using retrieved rather than supplied golden context.
- Separate retrieval recall, answer correctness and groundedness.
- Reject failing or stale release evidence.
- Inspect latency, token usage and failures in telemetry.

## Prerequisites (roles, resources, quota)

Python3.11+, Azure CLI login, the service endpoints named in `.env.example`, supported model quota and least-privilege data-plane access. Use an independent instructor-supplied environment. Cloud setup and tenant integrations are separate from offline validation. 

## Australian/residency note

Verify Australia East separately for project, model, tool, evaluator and telemetry. Model deployment type determines processing geography; account location is insufficient. Only synthetic data is bundled. Cross-region models/judges require explicit organisational approval. Tenant governance demonstrations may export interaction data: review their data destinations.

## Setup steps

From this lab directory:

```powershell
py -3.11 -m venv .venv
.venv/Scripts/Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
az login
python validate.py
```

Populate `.env` with endpoints and actual deployment names. No service keys are used.

## Guided walkthrough with numbered steps and code explanation

1. Supply an independent Search index with the bundled Acme corpus, fields `content`, `source`, `allowed_groups`, and both `hr-internal` and `citizen-service` permissions. Use the documented Lab08 preparation as a reusable prerequisite (not Lab18, whose groups and corpus differ); this lab bundles its own 20-row evaluation set.
2. Run `python src/evaluate.py --revision classroom-v1`. The candidate receives Search results, not the reference answer. The judge sees both for scoring. Recall@5 is source-document recall with one expected source per question; it is not chunk-level recall. The safety check measures returned document memberships for two synthetic identities. Lab21 separately tests signed user claims.
3. Run `python src/gate.py --report data/evaluation-report.json --revision classroom-v1`. Thresholds are teaching defaults: recall>=0.8, mean groundedness>=4, mean correctness>=4 and zero retrieval membership violations across at least20 cases. Calibrate with subject experts before production. Averages can hide severe individual failures; manually review case results too.
4. Copy the report to a local test file and change one metric, revision or evidence kind; confirm the gate exits1. `validate.py` exercises these cases offline, including NaN metrics. A fixture can test gate logic but never approve a release. A report is not tamper-proof; CI must protect workflow/code and generate it in the trusted job.
5. Run `python src/observe.py`, find its printed trace ID in Application Insights, then run `data/operations.kql`. Compare tokens and latency across runs. Deliberately use an invalid deployment name once and inspect the failed span; restore configuration afterwards. The observed call is an inference telemetry example, not the full Lab21 request tree.
6. Follow `data/production-operations.md` to define an alert, a release gate, production sampling and cost attribution. The CI example in Lab22 also runs app tests; this reference pipeline evaluation alone does not certify the deployed application's JWT, tool or network behaviour.

## Run & expected output

```powershell
python src/evaluate.py --revision classroom-v1
python src/gate.py --report data/evaluation-report.json --revision classroom-v1
python src/observe.py
```

A live report with20 cases; a gate exit0 for satisfactory current evidence or exit1 for failure. Trace/token fields appear only after successful ingestion; local tests cannot prove that.

## Validation

`python validate.py` checks local source and the named deterministic mechanics. It prints PASS/FAIL and exits nonzero on failure. Follow the walkthrough for live evidence; offline validation does not contact Azure or certify production controls.

## Troubleshooting

| Symptom | Action |
|---|---|
| KeyError for configuration | Populate this lab's .env; check actual deployment names. |
| 401 or unavailable credential | Sign in to the intended Entra tenant. |
| 403 | Verify service role, scope, propagation and private-network path. |
| 404 model/index | Copy the deployed name and endpoint from the supplied environment. |
| 429 | Lower classroom concurrency and check per-deployment quota. |
| Unsupported feature/package | Use the documented compatible environment and record the limitation; do not mark an unrun step passed. |

## Cleanup

Run `python cleanup.py` for this lab's generated local reports. It prompts and is safe to repeat. Shared services are instructor-owned. Reverse any scoped tenant changes you created using the recorded resource names; no blanket subscription or tenant deletion. Optional local model caches are managed through the Local SDK rather than deleting unrelated cache folders.

## Knowledge check (3 MCQs with answer key)

1. Does the candidate get the reference answer?

   A. No; it receives retrieved context B. Yes C. Only when scores fail

   Answer: A.

2. Can a fixture approve production?

   A. No B. Yes if all scores are5 C. Yes after renaming it

   Answer: A.

3. What is groundedness?

   A. Support in supplied evidence B. Retrieval recall C. Latency

   Answer: A.

## Stretch challenge

Change one variable, predict the result, run the experiment and attach observed evidence to your decision. Explain which conclusion the evidence does not support.

## References

- [Primary Microsoft Learn](https://learn.microsoft.com/azure/foundry/observability/how-to/evaluate-agent)
- [Official sample repository](https://github.com/Azure-Samples/Agentic-Evaluations)
