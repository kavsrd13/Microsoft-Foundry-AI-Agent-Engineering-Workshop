# Read-only MCP and approval — 45 minutes

## Status badges (GA/Preview/Prerelease)

Responses API: GA. Remote MCP availability must be checked for the selected model and project.

## Learning objectives

- Explain the MCP client/server boundary
- Approve and reject an explicit tool call
- Restrict outbound queries to public documentation

## Prerequisites

Foundry project, deployed MCP-capable model, Foundry User access and model inference permission. Public egress to the Microsoft Learn MCP endpoint. Python 3.11, a fresh virtual environment, Azure CLI sign-in and generated synthetic assets. No API keys. Infrastructure is supplied by the instructor; this lab owns only the objects explicitly recorded in its data directory.

## Australian/residency note

Australia East supports Foundry projects. Verify model, tool and evaluator availability individually. Deployment type (Global / Data Zone / Regional), not resource location, determines processing geography. Use only synthetic Acme Public Sector Pty Ltd data. An overseas judge or external MCP endpoint needs a separately approved data boundary.

## Setup steps

1. Open a terminal in this lab folder.
2. Create the environment and install the pinned dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
az login
```

3. Replace the placeholders in `.env`. A deployment name is not a model family name. Never commit `.env`.
4. Run `python validate.py` before any service call.

## Guided walkthrough with numbered steps and code explanation

1. Read the five fields in the `tools` dictionary: MCP type, fixed endpoint, label, single allowed tool and mandatory approval.
2. Run the script. Review the server, tool and arguments in each approval request. Type `n` on the first run to demonstrate refusal.
3. Repeat and type `y` only for a public documentation query. The continuation sends the approval request ID with the decision.
4. Observe the final answer. The loop handles further approval requests; it never approves them silently.
5. Read `data/illustrative-output.md` during endpoint failure. Replace it with a genuine sanitised capture only after a successful instructor rehearsal.

## Run & expected output

```powershell
python src/demo.py
```

Expect an approval prompt showing `microsoft_learn`, `microsoft_docs_search` and public query arguments, followed by an answer if approved. A denied call must not execute. Real output is saved in `data/live-output.txt`.

## Validation

`python validate.py` checks local syntax and assets without Azure. `python validate.py --live` checks the saved live artefact after running the demo; it is not a new cloud call. Pass criteria: no local failures, and the explicit live evidence check passes. For Lab 12, the instructor must also verify the trace in Application Insights. No tenant execution was performed while building this repository.

## Troubleshooting table

| Symptom | Likely cause and action |
|---|---|
| KeyError or placeholder endpoint | Fill the missing `.env` value and rerun from this lab. |
| 401 / credential unavailable | Run `az login` in the correct tenant; check identity selection. |
| 403 | Check the resource-scoped role, PIM activation and propagation; for private endpoints use a connected network. |
| 404 | Verify project URL, deployment name and lab knowledge resource name. |
| 429 | Check deployment quota; wait for Retry-After or reduce simultaneous classroom calls. |
| Timeout / DNS failure | Check private DNS, firewall and endpoint egress; do not bypass network controls. |
| Evaluator or preview feature unavailable | Check feature/region support; use the documented fallback with an explicit limitation. |

## Cleanup

Run `python cleanup.py`. It lists only known lab artefacts and prompts before deleting them. Repeating cleanup is safe. Shared Azure infrastructure is not deleted. Follow the additional ownership notes in `data/cleanup-notes.md`.

## Knowledge check

1. What happens before an allowed MCP call executes? A. Automatic consent B. Explicit approval C. Role creation
2. Can a read-only tool disclose query data externally? A. Yes B. No C. Only with API keys
3. What links a decision to its request? A. Deployment name B. Page title C. approval_request_id

Answer key: **1 B**, **2 A**, **3 C**.

## Stretch challenge

Request a second public documentation topic and reject one approval; explain why read-only tools still disclose their arguments externally.

## References

- [Primary Microsoft Learn article](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/model-context-protocol)
- [Required GitHub sample path](https://github.com/microsoft-foundry/foundry-samples/tree/main/samples/python/quickstart/create-agent/)
- [Australian considerations](../../AUSTRALIA-RESIDENCY.md)
