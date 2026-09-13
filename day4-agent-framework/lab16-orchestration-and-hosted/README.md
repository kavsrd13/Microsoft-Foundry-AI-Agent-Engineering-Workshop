# Lab 16 — Sequential, concurrent and hosted agents (90 minutes)

## Status badges (GA/Preview/Prerelease)

**GA:** Agent Framework 1.17.0; Foundry provider 1.12.0; Responses API. **GA:** Foundry Hosted Agents service. **PRERELEASE:** agent-framework-foundry-hosting 1.0.0b260903.
The requested provider pin requires `azure-ai-projects>=2.2.0,<2.4.0`. This Day 4 lab deliberately pins **2.3.0**, rather than the incompatible 2.6.0 requested for Days 1–3. Use a separate environment. The umbrella `agent-framework` package installs additional integrations, including prerelease dependencies; GA framework status does not make every optional integration GA.

## Learning objectives

- Build actual MAF sequential and concurrent workflows.
- Compare elapsed time and information flow.
- Run a local ResponsesHostServer.
- Prepare a Python 3.13 hosted deployment and invoke it.

## Prerequisites (roles, resources, quota)

Python 3.11 or newer for the local lab; Azure CLI with `az login`; an existing Foundry project and chat deployment; Foundry User/inference access to the project/model and sufficient model quota. Confirm the deployment name, not just the model catalogue name. Lab 16 hosted deployment requires **Python 3.13**, azd and its Azure AI Agents extension, Docker only for optional container builds, and instructor-approved provisioning permissions plus Foundry Project Manager access. No earlier lab output is required.

## Australian/residency note

Australia East supports Foundry projects. Verify the chosen model, each tool, evaluator and hosting feature individually. **Deployment type (Global / Data Zone / Regional), not resource location, determines processing geography.** Use synthetic Acme Public Sector Pty Ltd data only. A local agent still transmits prompts to the configured model service.

## Setup steps

Run these commands from this lab folder in PowerShell:

```powershell
py -3.11 -m venv .venv
.venv/Scripts/Activate.ps1
python -m pip install -r requirements.txt
# Use the shared foundry-agent-workshop/.env file
az login
```

Set `PROJECT_ENDPOINT` and `MODEL_DEPLOYMENT_NAME` in `.env`. Entra authentication uses `DefaultAzureCredential`; no API key is needed. For Lab 16B create a Python 3.13 environment. Do not install `requirements-base.txt` into this environment because its projects 2.6.0 pin conflicts with the provider.

## Guided walkthrough with numbered steps and code explanation

1. Run `workflows.py`. Both builders create real framework workflow graphs over retriever, analyst and writer agents. All three receive the synthetic order dataset.
2. In the sequential graph, each later participant sees earlier messages. The writer can use the analyst's conclusions. In the concurrent graph, the three agents work independently on the same initial input; its combined output is not the same dependency pipeline.
3. Inspect `timings.json`. Compare measured elapsed seconds and output usefulness. Concurrency can improve latency, but throttling and network variability can reverse the result. A single run is not a benchmark.
4. Start `host.py`, then invoke it from a second terminal with `invoke_local.py`. The local Responses adapter is an HTTP server, while inference still calls Azure with Entra credentials.
5. Read `DEPLOY.md` and inspect `deploy/azure.yaml` before any cloud action. The deployment uses a separate lab environment, Python 3.13, the official Foundry azd provider and Responses protocol.
6. Only after an instructor verifies region, model/SKU availability, costs and roles, follow `azd provision` → `azd deploy` → `azd ai agent invoke`. Missing Project Manager access makes this an instructor demonstration; all participants can complete local work.
7. Stop the local server and remove its lab-owned state. For deployed resources, review the dedicated environment and use `azd down` as described in the deployment guide. No deployment has been executed during repository authoring.

## Run & expected output

```powershell
python workflows.py
python host.py
# In a second terminal in this lab:
python invoke_local.py
```

Actual workflow output and measured seconds are printed. The server listens on port 8088; the local invocation returns Responses JSON. These are expected behaviours, not recorded cloud evidence.

## Validation (compileall usage + pass criteria)

```powershell
python -m compileall .
python -m compileall .
```

Offline mode checks syntax and installed provider presence; every check must print ✅ and exit 0. Live mode additionally verifies the configured deployment is visible using Entra authentication. It does not substitute for running the concept demo and checking the expected behaviour above. No live tenant execution was performed while authoring this repository.

## Troubleshooting table

| Symptom | Likely cause | Action |
|---|---|---|
| pip ResolutionImpossible mentioning projects | Day 1–3 environment reused | Create the separate Day 4 environment and use this lab's requirements |
| KeyError PROJECT_ENDPOINT | Missing .env field | Copy the shared workshop .env and populate the actual endpoint |
| CredentialUnavailableError / 401 | No usable Entra login | Run az login in the intended tenant and retry |
| 403 PermissionDenied | Project or inference role missing | Activate/assign the required scope, allow propagation, then retry |
| 404 deployment not found | Catalogue model name used as deployment name | Copy the deployed model's deployment name from Foundry |
| 429 TooManyRequests | Quota or rate limit exhausted | Wait and reduce concurrent calls; ask the instructor to check quota |
| Connection error or request timeout | Endpoint/network or overloaded model | Check endpoint and firewall, then rerun with a shorter prompt |
| Port 8088 already in use (Lab 16) | Another local server is running | Stop that lab server before starting another |

## Cleanup

```powershell
remove generated local files manually
```

The core demo creates no named cloud agent, index or deployment; there is no get-or-create scaffolding to distract from the concept. Local files are overwritten safely on rerun. Cleanup prompts before deleting generated output and is safe twice. Lab 16 hosting has separate state and deployment cleanup in `DEPLOY.md`; never delete a shared classroom project.

## Knowledge check (3 MCQs with answer key)

1. Which graph lets the writer use the analyst output?

   A. Sequential B. Independent concurrent C. Neither

2. What Python version is required for this hosted deployment?

   A. 3.9 B. 3.11 C. 3.13

3. Does Australia East resource location guarantee Australian model processing?

   A. Yes B. No C. Only for JSON

Answer key: 1: A, 2: C, 3: B.

## Stretch challenge

Change one instruction and predict the effect before running it. Explain which parts are deterministic Python behaviour and which depend on model output.

## References

- [Primary Microsoft Learn guide](https://learn.microsoft.com/agent-framework/workflows/orchestrations/)
- [Official Agent Framework sample path: python/samples/03-workflows/](https://github.com/microsoft/agent-framework/tree/main/python/samples/03-workflows/)
- [Foundry SDK overview](https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview)
- [Pinned provider metadata](https://pypi.org/project/agent-framework-foundry/1.12.0/)
- [Hosted agents guide](https://learn.microsoft.com/azure/foundry/how-to/develop/framework-hosted-agents)
- [Official hosted sample](https://github.com/microsoft-foundry/foundry-samples/tree/main/samples/python/hosted-agents/agent-framework/responses/01-basic/)
