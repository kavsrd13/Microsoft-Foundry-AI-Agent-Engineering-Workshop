# Lab 08 — Secure RAG · 45 minutes

## Status badges (GA/Preview/Prerelease)
Azure AI Search security-string filters — GA; Responses API — GA; native ACL/RBAC (2026-08-01-preview in supplied brief) — PREVIEW, disabled.

## Learning objectives
- Apply trusted group membership to retrieval
- Compare two synthetic identities
- Prove leakage when a filter is omitted
- Ground a response only in authorised context

## Prerequisites (roles, resources, quota)
Python 3.11+, Azure CLI login and this lab’s own supplied data. Existing Search service. Participant requires Search Service Contributor and Search Index Data Contributor. Optional --answer requires project access and a chat deployment. The two end users are synthetic personas, not impersonated Entra accounts.

## Australian/residency note
Australia East supports Foundry projects. Verify model, tool and evaluator availability individually before delivery. Deployment type (Global / Data Zone / Regional), rather than resource location, determines processing geography. Confirm Search, Blob and Document Intelligence locations independently; do not assume a globally deployed model processes in Australia.

## Setup steps
From this lab directory, use the workshop virtual environment, then run:

```powershell
python -m pip install -r requirements.txt
# Use the shared foundry-agent-workshop/.env file
az login
python -m compileall .
```

Replace endpoint and deployment placeholders in `.env`. Authentication uses `DefaultAzureCredential`; select the intended tenant with `az login --tenant <tenant-id>`. No keys are needed.

## Guided walkthrough with numbered steps and code explanation
1. Inspect independent synthetic chunks; leave-policy chunks are HR-only and other policies are shared.
2. Run the demo to create a separate simple Search index and upload the fixture.
3. Compare citizen-service and hr-internal results. The application applies allowed_groups/any before any context reaches a model.
4. Inspect the deliberately unfiltered negative control. HR-only IDs must appear; this is the expected evidence of a missing authorisation boundary.
5. Optionally run --answer. Only each persona’s authorised context enters Responses. Inspect --preview for the disabled native ACL design boundary.

Membership comes from fixed server-side synthetic identities. In production validate Entra tokens and resolve group membership, including overage, before constructing filters. Never accept group claims supplied as a browser form field. Security-string filters do not become service-enforced end-user ACLs. The unfiltered negative control is a teaching script, not a deployable route.

## Run & expected output
```powershell
python demo.py
python demo.py --answer
```
Expected: Different authorised ID sets and an EXPECTED NEGATIVE CONTROL leakage message. Optional grounded summaries cite sources. Exact model wording varies. No live Azure run was performed while authoring these files.

## Validation (compileall usage + pass criteria)
`python -m compileall .` checks source syntax and input fixtures locally, with explicit OFFLINE labels. `python -m compileall .` performs the documented read checks after the demo; Lab 6 checks saved extraction output rather than making a fresh analysis request. A passing local check is not proof of Azure RBAC, quota or model availability. Checks print ✅/❌ and failures exit 1. Run the main demo to verify the complete learning outcome.

## Troubleshooting table
| Symptom | Action |
|---|---|
| KeyError for an environment name | Populate every required placeholder in this lab’s .env. |
| 401 or credential unavailable | Run az login in the correct tenant and check DefaultAzureCredential’s selected identity. |
| 403 Forbidden | Check the participant and service managed-identity roles listed above; allow RBAC propagation. |
| 404 resource or deployment not found | Use the deployment name, not a model family name; check the service-specific endpoint. |
| 429 throttling or quota exhausted | Wait, reduce the classroom concurrency and check deployment/service quota. |
| Network timeout or DNS failure | Check private endpoint DNS and service firewall access from the participant machine. |
| Search results empty or indexer fails | Wait for indexing, then inspect indexer execution errors, identity access and embedding dimensions. |

## Cleanup
Run `remove generated local files manually` and type `yes` when asked. It removes only this lab’s recorded resources (or Lab 6’s generated local files). Repeated cleanup is safe. Existing shared Foundry, Search, Storage, model deployments and Document Intelligence services are retained. Resource names use a stable random suffix in `resource-state.json`; retain that file until cleanup.

## Knowledge check
1. Where must filtering happen? A. After answer B. In retrieval C. In CSS

2. Who supplies trusted groups? A. Validated identity backend B. Prompt C. Browser textbox

3. What proves the negative control? A. Empty set B. Same answer C. Restricted IDs appear

Answer key: 1 B; 2 A; 3 C.

## Stretch challenge
Change one input and predict the result before rerunning. Explain which service executes each step and which identity authorises it.

## References
- [Primary Microsoft Learn guide](https://learn.microsoft.com/azure/search/search-document-level-access-overview)
- [Official GitHub sample path](https://github.com/Azure/azure-search-vector-samples/tree/main/demo-python/)
