# Lab 01 — Foundry setup (45 minutes)

## Status badges (GA/Preview/Prerelease)

Foundry project access: **GA** | Responses API: **GA** | Prompt Agents: **GA** where used.
Package: azure-ai-projects **2.6.0**. Service status and SDK feature headers are different concepts.

## Learning objectives

- Connect a project client using Entra ID.
- List deployed models.
- Distinguish configured location from verified resource metadata.

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
2. Run `src/main.py`: `AIProjectClient` selects the project; `DefaultAzureCredential` uses your signed-in identity. `deployments.list()` reads deployments without provisioning anything. Compare each deployment name with the portal. The tenant and location printed are configured labels; the CLI commands below verify the actual resource.
3. Change one input or instruction, rerun, and explain the observed difference to another participant.

## Run & expected output

```powershell
python src/main.py
```

A project endpoint, a configured tenant/location label and one or more deployment names. Output wording varies with the deployed model. 

## Validation

`python validate.py` checks syntax offline. `python validate.py --live` checks real deployment access. PASS means only the named checks passed. Cloud failures exit 1 and retain the original exception type. A local PASS does not prove regional availability or successful inference.

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

Run `python cleanup.py` from this folder. The Python example is read-only. Lab 02 portal cleanup is described in data/portal-deployment.md. Shared project/account resources remain instructor-owned.

## Knowledge check (3 MCQs with answer key)

1. **What authenticates this client?** A. Entra ID B. An embedded key C. A PDF

   Answer: **A**. Entra ID.

2. **What does deployments.list do?** A. Reads deployments B. Creates a model C. Deletes quota

   Answer: **A**. Reads deployments.

3. **What proves a deployment is accessible?** A. A successful live list B. A syntax check C. A configured region string

   Answer: **A**. A successful live list.

## Stretch challenge

Explain what evidence would distinguish correct local code from a working live Azure configuration.

## References

- [Primary Microsoft Learn source](https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview)
- [Foundry SDK sample: samples/python/quickstart/create-agent/](https://github.com/microsoft-foundry/foundry-samples/tree/main/samples/python/quickstart/create-agent)
- [Standard agent setup](https://learn.microsoft.com/azure/foundry/agents/concepts/standard-agent-setup)
