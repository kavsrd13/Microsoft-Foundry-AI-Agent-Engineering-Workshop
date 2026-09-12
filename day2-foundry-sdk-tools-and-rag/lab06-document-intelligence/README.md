# Lab 06 — Document Intelligence · 45 minutes

## Status badges (GA/Preview/Prerelease)
Document Intelligence v4.0 (2024-11-30) — GA.

## Learning objectives
- Extract layout as Markdown
- Preserve original PDF page references
- Create a simple overlapping chunk dataset

## Prerequisites (roles, resources, quota)
Python 3.11+, Azure CLI login and this lab’s own supplied data. Cognitive Services User on an existing Document Intelligence resource, with a custom subdomain endpoint configured for Entra authentication. Sufficient analysis quota for three short PDFs.

## Australian/residency note
Australia East supports Foundry projects. Verify model, tool and evaluator availability individually before delivery. Deployment type (Global / Data Zone / Regional), rather than resource location, determines processing geography. Confirm Search, Blob and Document Intelligence locations independently; do not assume a globally deployed model processes in Australia.

## Setup steps
From this lab directory, use the workshop virtual environment, then run:

```powershell
python -m pip install -r requirements.txt
Copy-Item .env.example .env
az login
python validate.py
```

Replace endpoint and deployment placeholders in `.env`. Authentication uses `DefaultAzureCredential`; select the intended tenant with `az login --tenant <tenant-id>`. No keys are needed.

## Guided walkthrough with numbered steps and code explanation
1. Open the supplied synthetic PDFs. They belong to this lab and require no previous exercise.
2. Run `prebuilt-layout` using the GA API date and Markdown output.
3. Compare the saved Markdown headings and table markup with the PDF. Page spans associate returned Markdown with physical page numbers.
4. Inspect `data/chunks.json`: 1,800-character windows overlap by 300 characters. This intentionally simple chunker can split a table; the full Markdown remains intact.

No service is provisioned. Cleanup removes local analysis outputs only. Lab 7 ships independent input data; optionally copy this JSON there to compare real extraction with its supplied fixture.

## Run & expected output
```powershell
python src/demo.py
```
Expected: PDF page counts, saved Markdown files and the number of output chunks. Exact model wording varies. No live Azure run was performed while authoring these files.

## Validation (validate.py usage + pass criteria)
`python validate.py` checks source syntax and input fixtures locally, with explicit OFFLINE labels. `python validate.py --live` performs the documented read checks after the demo; Lab 6 checks saved extraction output rather than making a fresh analysis request. A passing local check is not proof of Azure RBAC, quota or model availability. Checks print ✅/❌ and failures exit 1. Run the main demo to verify the complete learning outcome.

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
Run `python cleanup.py` and type `yes` when asked. It removes only this lab’s recorded resources (or Lab 6’s generated local files). Repeated cleanup is safe. Existing shared Foundry, Search, Storage, model deployments and Document Intelligence services are retained. Resource names use a stable random suffix in `data/resource-state.json`; retain that file until cleanup.

## Knowledge check
1. Which model extracts layout? A. prebuilt-layout B. Chat C. HNSW

2. What preserves table markup? A. IDs B. Markdown C. Quota

3. Why retain page numbers? A. Authentication B. Billing C. Citations

Answer key: 1 A; 2 B; 3 C.

## Stretch challenge
Change one input and predict the result before rerunning. Explain which service executes each step and which identity authorises it.

## References
- [Primary Microsoft Learn guide](https://learn.microsoft.com/azure/ai-services/document-intelligence/prebuilt/layout?view=doc-intel-4.0.0)
- [Official GitHub sample path](https://github.com/Azure-Samples/document-intelligence-code-samples/tree/main/Python%20(v4.0))
