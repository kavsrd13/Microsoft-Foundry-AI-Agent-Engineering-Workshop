# Lab 03 — Prompt agents and versions (45 minutes)

## Status badges (GA/Preview/Prerelease)

Foundry project access: **GA** | Responses API: **GA** | Prompt Agents: **GA** where used.
Package: azure-ai-projects **2.6.0**. Service status and SDK feature headers are different concepts.

## Learning objectives

- Create a named Prompt Agent.
- Invoke its stored instructions.
- Compare two immutable instruction versions.

## Prerequisites (roles, resources, quota)

Python 3.11+, Azure CLI signed in, an independently supplied Foundry project and a supported chat deployment with available quota. Request the least-privilege project role for model inference/agent creation (Foundry User as applicable). Lab 02 deployment requires account-scoped model deployment permission; a project-only role is insufficient. Ask the instructor to provision these prerequisites for each lab; do not depend on a previous lab.

## Australian/residency note

Australia East project availability does not prove model/tool/evaluator availability. Verify each separately. Deployment type (Global / Data Zone / Regional), rather than project location alone, determines model processing geography. Only use synthetic data here. See [residency checklist](../../AUSTRALIA-RESIDENCY.md).

## Setup steps

From this lab folder in PowerShell:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
az login
```

Edit `.env` with your project endpoint and actual deployment name. Keep `AZURE_TENANT_ID` aligned with your signed-in tenant. `AZURE_LOCATION` is a configured label; verify it using the Azure portal resource Overview. To verify tenant: `az account show --query tenantId -o tsv`. To verify account region: `az cognitiveservices account show --name YOUR-ACCOUNT --resource-group YOUR-RG --query location -o tsv`.

## Guided walkthrough with numbered steps and code explanation

1. Open `src/main.py` and identify authentication, project access and the single concept being taught.
2. Run `src/main.py`. First the script saves a unique agent name locally, then `create_version()` creates an instruction version. The second version changes response style. `list_versions()` makes the version boundary visible. `get_openai_client(agent_name=...)` binds inference to that named agent. Rerunning adds versions to the same lab-owned agent.
3. Change one input or instruction, rerun, and explain the observed difference to another participant.

## Run & expected output

```powershell
python src/main.py
```

One agent name, two new version numbers and a brief Australian English response. Output wording varies with the deployed model. 

## Validation

`python validate.py` checks syntax offline. `python validate.py --live` checks real deployment access and lab-created resource existence. PASS means only the named checks passed. Cloud failures exit 1 and retain the original exception type. A local PASS does not prove regional availability or successful inference.

## Troubleshooting

| Error/symptom | Action |
|---|---|
| KeyError for PROJECT_ENDPOINT | Copy and populate this lab's .env; run from this folder. |
| CredentialUnavailableError / 401 | Run az login in the intended tenant; check token audience/project endpoint. |
| 403 Forbidden | Check project/account RBAC, propagation and network reachability; do not broaden scope blindly. |
| 404 deployment or agent | Copy the deployment name, not catalogue model name; check project and recorded state. |
| 429 throttling/quota | Reduce classroom concurrency or request quota; retry after the service's indicated delay. |
| Empty deployment list | Instructor must supply a supported deployed model; an account alone is insufficient. |

## Cleanup

Run `python cleanup.py` from this folder. It prompts before removing the recorded lab resources and tolerates resources already removed. Shared project/account resources remain instructor-owned.

## Knowledge check (3 MCQs with answer key)

1. **What is a Prompt Agent?** A. A named versioned definition B. A virtual machine C. A PDF

   Answer: **A**. A named versioned definition.

2. **What changes when instructions change?** A. Create a new version B. Edit the PDF C. Rotate the tenant

   Answer: **A**. Create a new version.

3. **What does cleanup remove?** A. This lab-owned agent B. The resource group C. All project deployments

   Answer: **A**. This lab-owned agent.

## Stretch challenge

Create a third instruction version and compare response style.

## References

- [Primary Microsoft Learn source](https://learn.microsoft.com/azure/foundry/agents/quickstarts/prompt-agent)
- [Foundry SDK sample: samples/python/quickstart/create-agent/](https://github.com/microsoft-foundry/foundry-samples/tree/main/samples/python/quickstart/create-agent)
- [Standard agent setup](https://learn.microsoft.com/azure/foundry/agents/concepts/standard-agent-setup)
