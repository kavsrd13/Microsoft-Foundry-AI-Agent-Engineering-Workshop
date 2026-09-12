# Lab 13 — MAF transition: one task, two clients (45 minutes)

## Status badges (GA/Preview/Prerelease)

**GA:** Agent Framework 1.17.0; Foundry provider 1.12.0; Responses API. 
The requested provider pin requires `azure-ai-projects>=2.2.0,<2.4.0`. This Day 4 lab deliberately pins **2.3.0**, rather than the incompatible 2.6.0 requested for Days 1–3. Use a separate environment. The umbrella `agent-framework` package installs additional integrations, including prerelease dependencies; GA framework status does not make every optional integration GA.

## Learning objectives

- Run the identical task with direct SDK and MAF.
- Identify where the Foundry SDK remains in the MAF call path.
- Compare code size and control without assuming fewer lines always means clearer teaching.

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
Copy-Item .env.example .env
az login
```

Set `PROJECT_ENDPOINT` and `MODEL_DEPLOYMENT_NAME` in `.env`. Entra authentication uses `DefaultAzureCredential`; no API key is needed. For Lab 16B create a Python 3.13 environment. Do not install `requirements-base.txt` into this environment because its projects 2.6.0 pin conflicts with the provider.

## Guided walkthrough with numbered steps and code explanation

1. Open `src/a_foundry_sdk.py`. `AIProjectClient` provides project access, `get_openai_client()` exposes Responses, and the application supplies the task directly. `store=False` avoids a retained response resource.
2. Run the script and read its two-sentence answer. The model wording is nondeterministic; do not compare exact text.
3. Open `src/b_agent_framework.py`. The same project client is passed to `FoundryChatClient`. `Agent.run()` wraps the same task. The asynchronous `main()` supports the framework's asynchronous execution model.
4. Compare the shared instruction and input strings. Neither example creates a persisted agent. The abstraction becomes useful when adding sessions, tools or workflows, not because a one-call example necessarily becomes shorter.

| Dimension | Direct SDK | MAF |
|---|---|---|
| Nonblank Python lines | 14 | 17 |
| Main concepts beyond auth/config | Project client, Responses request, output text (3) | Project client, chat client, Agent, asynchronous run (4) |
| Control surface | Explicit Responses request fields | Agent lifecycle, tools, providers, middleware |
| Dependency | azure-ai-projects | Foundry provider itself depends on azure-ai-projects |
| Task/instructions | Identical | Identical |

## Run & expected output

```powershell
python src/a_foundry_sdk.py
python src/b_agent_framework.py
```

Both scripts print a short explanation of source citation. Wording can differ; both use the same instruction and task.

## Validation (validate.py usage + pass criteria)

```powershell
python validate.py
python validate.py --live
```

Offline mode checks syntax and installed provider presence; every check must print ✅ and exit 0. Live mode additionally verifies the configured deployment is visible using Entra authentication. It does not substitute for running the concept demo and checking the expected behaviour above. No live tenant execution was performed while authoring this repository.

## Troubleshooting table

| Symptom | Likely cause | Action |
|---|---|---|
| pip ResolutionImpossible mentioning projects | Day 1–3 environment reused | Create the separate Day 4 environment and use this lab's requirements |
| KeyError PROJECT_ENDPOINT | Missing .env field | Copy .env.example and populate the actual endpoint |
| CredentialUnavailableError / 401 | No usable Entra login | Run az login in the intended tenant and retry |
| 403 PermissionDenied | Project or inference role missing | Activate/assign the required scope, allow propagation, then retry |
| 404 deployment not found | Catalogue model name used as deployment name | Copy the deployed model's deployment name from Foundry |
| 429 TooManyRequests | Quota or rate limit exhausted | Wait and reduce concurrent calls; ask the instructor to check quota |
| Connection error or request timeout | Endpoint/network or overloaded model | Check endpoint and firewall, then rerun with a shorter prompt |
| Port 8088 already in use (Lab 16) | Another local server is running | Stop that lab server before starting another |

## Cleanup

```powershell
python cleanup.py
```

The core demo creates no named cloud agent, index or deployment; there is no get-or-create scaffolding to distract from the concept. Local files are overwritten safely on rerun. Cleanup prompts before deleting generated output and is safe twice.

## Knowledge check (3 MCQs with answer key)

1. Which provides project access under the MAF provider?

   A. Browser storage B. Foundry SDK C. SQL

2. Does MAF always reduce a single-call script?

   A. Yes B. No C. Only with API keys

3. Which part is identical in the two examples?

   A. Task and instructions B. Output wording C. Number of imports

Answer key: 1: B, 2: B, 3: A.

## Stretch challenge

Change one instruction and predict the effect before running it. Explain which parts are deterministic Python behaviour and which depend on model output.

## References

- [Primary Microsoft Learn guide](https://learn.microsoft.com/agent-framework/integrations/by-component/model-providers/microsoft-foundry)
- [Official Agent Framework sample path: python/samples/02-agents/providers/foundry/](https://github.com/microsoft/agent-framework/tree/main/python/samples/02-agents/providers/foundry/)
- [Foundry SDK overview](https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview)
- [Pinned provider metadata](https://pypi.org/project/agent-framework-foundry/1.12.0/)
