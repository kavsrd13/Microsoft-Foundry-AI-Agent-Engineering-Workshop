# Lab 05 — Function Calling · 45 minutes

## Status badges (GA/Preview/Prerelease)
Foundry Prompt Agents — GA; Responses API — GA; function tools — GA.

## Learning objectives
- Create strict tool schemas
- Dispatch function calls to ordinary Python functions
- Return call IDs and tool results to the model

## Prerequisites (roles, resources, quota)
Python 3.11+, Azure CLI login and this lab’s own supplied data. Foundry User on the project; an existing chat deployment and model inference access. No extra Azure resource is provisioned.

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
1. Read the three short functions over `orders.json`.
2. Read each `FunctionTool` JSON schema: the model receives names and argument types, not executable Python.
3. Run the demo. The application matches the returned function name, invokes it, then returns a `function_call_output` with the original call ID.
4. Observe the final answer after the tool loop completes. Repeat execution reuses the recorded agent version.

The ten-minute run expiry applies to classic thread/run APIs. This lab uses Responses, so it does not claim a universal ten-minute Responses expiry. A nine-minute application guard keeps the teaching loop bounded; SDK requests may take additional time.

## Run & expected output
```powershell
python demo.py
```
Expected: Tool names and synthetic order facts, followed by a natural-language answer. Exact model wording varies. No live Azure run was performed while authoring these files.

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
1. Who executes a Python tool? A. Model B. Application C. Search

2. What correlates an output? A. call_id B. Customer name C. Region

3. What contains accepted arguments? A. Vector B. Schema C. PDF

Answer key: 1 B; 2 A; 3 B.

## Stretch challenge
Change one input and predict the result before rerunning. Explain which service executes each step and which identity authorises it.

## References
- [Primary Microsoft Learn guide](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/function-calling)
- [Official GitHub sample path](https://github.com/microsoft-foundry/foundry-samples/tree/main/samples/python/quickstart/create-agent/)
- [SDK function sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/tools/sample_agent_function_tool.py)
