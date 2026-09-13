# Lab 14 — Session memory and personalisation (45 minutes)

## Status badges (GA/Preview/Prerelease)

**GA:** Agent Framework 1.17.0; Foundry provider 1.12.0; Responses API.
The requested provider pin requires `azure-ai-projects>=2.2.0,<2.4.0`. This Day 4 lab deliberately pins **2.3.0**, rather than the incompatible 2.6.0 requested for Days 1–3. Use a separate environment. The umbrella `agent-framework` package installs additional integrations, including prerelease dependencies; GA framework status does not make every optional integration GA.

## Learning objectives

- Keep a conversation in AgentSession.
- Serialise and restore local history.
- Inject a synthetic user preference through ContextProvider.
- Keep distinct users in separate sessions.

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

1. Read the first two records in `user_preferences.json`. These are synthetic profiles, not authenticated identities.
2. Inspect `Preferences.before_run()`. The provider chooses a profile using `session.state['user_id']` and contributes language, tone and channel instructions. Only the hook needed for this lesson is implemented.
3. The first run supplies `ACME-204`. `InMemoryHistoryProvider` puts messages inside session state. `store=False` keeps model history local to this demo.
4. Serialise the session to `session.json`, reconstruct it with `AgentSession.from_dict()`, and ask for the case reference. This explicitly demonstrates persistence across a save/load boundary.
5. A new session selects the second user. It receives that profile's preferences but must not know the first user's reference. In a real application, derive the user identity from a trusted sign-in; a request-supplied user ID is not authorisation.
6. Inspect the saved JSON. It contains synthetic conversation content and should be treated as sensitive if replaced with real data. This is a small classroom file, not a production session database.

## Run & expected output

```powershell
python demo.py
```

The restored session should answer ACME-204. The second user should not know that reference. Style follows each profile; exact wording varies.

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

1. What preserves local conversational messages?

   A. InMemoryHistoryProvider and session state B. Profile tone C. Model name

2. Is a user ID from the request trusted authorisation?

   A. Yes B. No C. Only if short

3. How should two users be isolated?

   A. Share all history B. Use separate sessions C. Change only the prompt

Answer key: 1: A, 2: B, 3: B.

## Stretch challenge

Change one instruction and predict the effect before running it. Add a third user and verify that no previous case reference appears in that new session.

## References

- [Primary Microsoft Learn guide](https://learn.microsoft.com/agent-framework/concepts/agents/conversations/context-providers)
- [Official Agent Framework sample path: python/samples/02-agents/context_providers/](https://github.com/microsoft/agent-framework/tree/main/python/samples/02-agents/context_providers/)
- [Foundry SDK overview](https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview)
- [Pinned provider metadata](https://pypi.org/project/agent-framework-foundry/1.12.0/)
