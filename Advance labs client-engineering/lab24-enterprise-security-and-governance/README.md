# Lab 24 — Enterprise identity, networking and governance (120 minutes; split into short exercises)

## Status badges (GA/Preview/Prerelease)

Content Safety text API: GA. Agent ID, Conditional Access, Control Plane and security integrations: availability/licensing and status are checked per feature in the tenant; guided exercises, not preconfigured controls.

## Learning objectives

- Inspect identity and network boundaries.
- Run benign content-safety and synthetic injection probes.
- Exercise tenant governance integrations with evidence.
- Produce a readiness report that leaves unverified controls pending.

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

Populate `.env` with endpoints and actual deployment names. No service keys are used. OpenAI client `api_key=token` in the embedding example is an Entra token callback, not a stored API key.

## Guided walkthrough with numbered steps and code explanation

1. Open `data/enterprise-exercises.md`. Select a disposable lab environment and assign an evidence owner to each exercise. Never apply tenant-wide blocking policies as a classroom shortcut.
2. Run `python src/network_check.py YOUR-SEARCH.search.windows.net YOUR-COSMOS.documents.azure.com` from the deployed runtime or its network. Compare DNS inside/outside the private network, resource public access settings and an unauthorised request. Private DNS alone is not proof of private-only access.
3. Run `python src/content_safety.py` against a supported Content Safety resource with Entra Cognitive Services User permissions. Inspect category scores for the benign input. This confirms API mechanics, not harmful-content coverage.
4. Run `python src/redteam.py` against your synthetic candidate. Review the normal, direct-injection, retrieved-record injection and unsupported-question answers. Record canary exposures and factual mistakes. The exact-string probe is deliberately small and not equivalent to the managed Red Teaming Agent; the guide includes a separate managed scan exercise.
5. Complete Entra Agent ID, Conditional Access report-only, Defender, Purview, guardrails and Control Plane exercises in the guide when the tenant and permissions support them. Each requires an observed event or control result, not a checkbox that the feature exists.
6. Copy `data/control-evidence.json` to a private local working file, add verified status plus owner/evidence/date only after observing each result, then run `python src/readiness.py --evidence YOUR-EVIDENCE.json`. The bundled template intentionally fails readiness. Document unresolved actions rather than inventing evidence.

## Run & expected output

```powershell
python src/content_safety.py
python src/redteam.py
python src/readiness.py
```

DNS evidence, category scores, a synthetic probe report and pending readiness controls. Tenant exercises produce their own evidence; this repository contains no claimed Defender/Purview/Conditional Access activation.

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

1. Does a sensitivity label itself enforce this Search filter?

   A. No; enforcement must be wired and tested B. Always C. Only on PDFs

   Answer: A.

2. Where should new Conditional Access rules be tried first?

   A. A scoped report-only exercise B. All users with Block C. Production without exclusions

   Answer: A.

3. What proves readiness?

   A. Reviewed evidence for controls B. A syntactically valid checklist C. A model claiming it is secure

   Answer: A.

## Stretch challenge

Change one variable, predict the result, run the experiment and attach observed evidence to your decision. Explain which conclusion the evidence does not support.

## References

- [Primary Microsoft Learn](https://learn.microsoft.com/azure/foundry/control-plane/how-to-manage-compliance-security)
- [Official sample repository](https://github.com/Azure-Samples/Agentic-Evaluations)
