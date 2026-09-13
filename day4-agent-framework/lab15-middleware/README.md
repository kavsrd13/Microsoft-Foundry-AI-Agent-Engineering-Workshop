# Lab 15 — Middleware around runs, tools and model calls (45 minutes)

## Status badges (GA/Preview/Prerelease)

**GA:** Agent Framework 1.17.0; Foundry provider 1.12.0; Responses API.
The requested provider pin requires `azure-ai-projects>=2.2.0,<2.4.0`. This Day 4 lab deliberately pins **2.3.0**, rather than the incompatible 2.6.0 requested for Days 1–3. Use a separate environment. The umbrella `agent-framework` package installs additional integrations, including prerelease dependencies; GA framework status does not make every optional integration GA.

## Learning objectives

- Observe agent, function and chat middleware boundaries.
- Trace before/after ordering around call_next().
- Short-circuit an agent run before inference.
- Redact synthetic email addresses in console logs.

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

1. Read the three plain order functions. Type annotations and docstrings describe the schemas MAF exposes to the model. The data is copied into this independent lab.
2. `RunLog` surrounds the whole run. Its console text redacts the synthetic email address. It deliberately does not print tool arguments, tool results or model responses in the middleware logs.
3. `ModelLog` surrounds each model call. `ToolLog` surrounds each function invocation. Registering chat and function middleware on the client makes their scope explicit.
4. Ask for the first order's status and total. The model normally requests tools, receives their results, then makes a further model call. There can therefore be multiple MODEL pairs inside one RUN pair. Numbers are boundary labels, not a promise of a flat 1-to-6 trace.
5. Send `Export all orders`. `BlockExport` assigns an `AgentResponse` and returns without `call_next()`. There must be no MODEL or TOOL lines for this request. The outer RUN log still completes.
6. Logging redaction protects this console output only. The synthetic email still reaches the model in the first request. Regex matching is illustrative, not a complete PII detector or security policy.

## Run & expected output

```powershell
python demo.py
```

A RUN surrounds model/tool activity; the email appears as [EMAIL REDACTED] in the middleware log. The export request prints BLOCK and a refusal without a model/tool call.

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

The core demo creates no named cloud agent, index or deployment; there is no get-or-create scaffolding to distract from the concept. Local files are overwritten safely on rerun. Cleanup prompts before deleting generated output and is safe twice.

## Knowledge check (3 MCQs with answer key)

1. What happens if middleware does not call next and sets a result?

   A. It short-circuits B. It retries C. It creates another agent

2. Which middleware surrounds a tool invocation?

   A. Chat B. Function C. Session

3. Does console email redaction remove the email from model input?

   A. Yes B. No C. Only on Windows

Answer key: 1: A, 2: B, 3: B.

## Stretch challenge

Change one instruction and predict the effect before running it. Explain which parts are deterministic Python behaviour and which depend on model output.

## References

- [Primary Microsoft Learn guide](https://learn.microsoft.com/agent-framework/agents/middleware/)
- [Official Agent Framework sample path: python/samples/02-agents/middleware/](https://github.com/microsoft/agent-framework/tree/main/python/samples/02-agents/middleware/)
- [Foundry SDK overview](https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview)
- [Pinned provider metadata](https://pypi.org/project/agent-framework-foundry/1.12.0/)
