# Lab 20 — Host tools and connect integrations (120 minutes + 60 minutes optional)

## Status badges (GA/Preview/Prerelease)

Core: Azure Functions Python v2 programming model, authenticated HTTP calls and local MCP. A2A integration is preview; Toolboxes and individual tool types are feature-dependent extensions: check the linked documentation and selected project's availability before scheduling them. Local execution and deployment validation are separate. This lab adds client Modules 6 and 7; Lab 16 supplies sequential/concurrent orchestration.

## Learning objectives

- Explain where a tool executes: the model proposes a call; application code invokes a separate Function host.
- Deploy a small read-only HTTP tool, use Entra tokens and enforce an application role.
- Discover and call an MCP tool; compare MCP, OpenAPI, Toolbox reuse, Logic Apps and A2A.

## Prerequisites

Python 3.11+, Azure Functions Core Tools v4, an isolated virtual environment and an instructor-provided Python Function app with storage. Cloud exercise needs an API app registration, role-assignment administrator and a caller identity. Model exercise needs the existing chat deployment and Cognitive Services OpenAI User. Core Tools does not emulate Easy Auth. Use only the synthetic order. Optional integrations need prepared connections/endpoints and project permissions.

## Australian/residency note

Choose an approved Australian hosting region and verify Functions plan, storage, model deployment geography and outbound integration boundaries independently. An Australian Function does not constrain the model's processing location or a connector's downstream destination. Record host region and each destination in your lab evidence.

## Setup steps

1. Open this lab folder, create/activate a virtual environment, then run:

```powershell
pip install -r requirements.txt
Copy-Item .env.example .env
az login
python validate.py
```

2. Create local-only `local.settings.json` with the following content. Keep it untracked. This HTTP exercise has no storage binding; if your local host requires storage, run Azurite and set `AzureWebJobsStorage` to `UseDevelopmentStorage=true`.

```json
{"IsEncrypted":false,"Values":{"FUNCTIONS_WORKER_RUNTIME":"python"}}
```

3. Leave `ORDER_TOOL_URL` pointing at localhost initially. Fill the model endpoint/deployment only for `src/agent.py`. Dependencies are pinned; Azure live execution remains an instructor rehearsal requirement.

## Guided walkthrough with numbered steps and code explanation

1. Read `function_app.py`: a route looks up ACME-204 in `data/orders.json`. The `Orders.Read` app role authorises access. No principal returns 401; a principal without that role returns 403; an unknown order returns 404. These are necessary service boundaries, not general exception wrappers. The Function trigger is `ANONYMOUS` because **Easy Auth authenticates before the trigger**; this is not permission to expose it without platform authentication.
2. Start `func start` in terminal A. In terminal B run `python src/call_tool.py`. The loopback client injects a synthetic principal solely to exercise the local handler. This proves code behaviour, not identity security. Never expose Core Tools or the local MCP server to a shared/public network.
3. Run `python src/agent.py`: the first Responses request selects the one allowed function; the application calls HTTP; the second request supplies the result. The model never executes Python or receives the bearer token. Only the fixed synthetic order is exposed; extending to arbitrary customer IDs requires object-level access checks.
4. Instructor: create/select a dedicated Python Function app. In **Authentication**, add Microsoft Entra with a single-tenant registration, require authentication and return HTTP 401 for unauthenticated API requests. Set the exact intended token audience, issuer and caller restrictions. In the API registration define enabled app role `Orders.Read` for **Users/Groups and Applications**. Assign the learner through Enterprise Applications and assign the deployed caller service principal/managed identity the application role. For delegated local calls, expose a scope such as `Orders.Access`, authorise the chosen CLI/developer client and grant required consent. `TOOL_SCOPE=api://<API-client-id>/.default` requests that API, not Graph or the model API. A role assignment and a delegated scope solve different problems. Use the linked authentication guide to configure the tenant's exact audience/token version; verify the resulting role claim without logging the token.
5. Publish from this directory after authentication is configured:

```powershell
func azure functionapp publish YOUR-FUNCTION-APP
```

Set `ORDER_TOOL_URL=https://YOUR-FUNCTION-APP.azurewebsites.net/api/orders/ACME-204` and the correct `TOOL_SCOPE` in `.env`. Run `src/call_tool.py` again. `DefaultAzureCredential` uses developer credentials locally or the assigned managed identity when hosted. The service trusts the principal header only because Easy Auth validates tokens and supplies it. Direct backend access must not bypass Easy Auth.
6. Test deployed security: unsigned request must fail; authenticated caller without `Orders.Read` must fail; assigned caller must succeed. Also send a fabricated principal header **without a bearer token**: platform authentication must reject it. Do not proceed if this reaches the handler. Save status codes, not tokens. Role changes can require a fresh token.
7. Start `python src/mcp_server.py` in terminal C, then `python src/mcp_client.py` in terminal B. The client initialises, discovers tools and calls `get_order_status`. The MCP server uses its own configured credential to call the Function; this does not pass through the end user's identity. It binds to loopback. A cloud agent cannot call your laptop's localhost. A remotely hosted MCP service needs HTTPS, authentication and network controls of its own.
8. Open `data/openapi.json`; replace only the placeholder server URL in a local copy. Find operationId, route, parameter and bearer scheme. Compare this explicit contract with MCP runtime discovery. A schema declaration does not obtain or validate a token. In a prepared Foundry OpenAPI connection, configure supported managed-identity authentication for the API audience and assign that identity `Orders.Read`; import the schema, ask for ACME-204 and capture the actual HTTP invocation. If the selected integration cannot use the required authentication, record the blocker and retain the authenticated application function-calling path. Do not weaken the API to make an import work.
9. **Guided Toolbox extension:** in Foundry Toolkit, expand project Tools, add a toolbox and add the instructor's reachable, authenticated MCP connection. Publish a version and copy its consumer endpoint. Using the official consumer example in References, authenticate to that endpoint, initialise MCP and list tools. Invoke the expected tool from an agent and record version/tool/result. Create a second agent using that same endpoint to demonstrate reuse. Tool search is a separate optional routing feature; ordinary `tools/list` discovery does not prove intent-based search. Do not register localhost as a cloud endpoint.
10. **Guided Logic Apps extension:** create a dedicated workflow with an instructor-approved request trigger, authenticated HTTP action calling this Function, and Response action returning status. Give its managed identity the API role and set the HTTP action's audience. Run the workflow with ACME-204; inspect trigger/action/output in run history. Register it through the project's supported Logic Apps connector surface if available, then invoke from the agent. Record workflow execution separately from agent integration. No emails or business writes are required.
11. **Guided A2A extension:** use an instructor-provided authenticated A2A agent endpoint, inspect its agent card and declared skills, then connect through the documented Foundry A2A tool. Submit one synthetic enquiry, inspect task state and final artifact, and compare it with the direct tool response. An HTTP JSON endpoint or two local agents is not automatically A2A. Record actual protocol/task evidence; otherwise mark this extension as a walkthrough only.

## Run & expected output

```powershell
# Terminal A
func start
# Terminal B
python src/call_tool.py
python src/agent.py
# Terminal C
python src/mcp_server.py
# Terminal B
python src/mcp_client.py
```

Expect status `Scheduled` for ACME-204 and MCP discovery containing `get_order_status`. Natural-language answers vary. The function host and MCP server must remain running. Core lab evidence: local output, cloud HTTP status matrix and one agent response. Optional evidence: imported operation, Toolbox version/discovery, workflow run and A2A task/artifact. Label each unexecuted extension explicitly.

## Validation

`python validate.py` invokes the real Function handler with synthetic requests: 401, missing/wrong-role 403, authorised 200, missing-order 404 and OpenAPI security declaration. `python validate_http.py` exercises the actual HTTP client against that handler through a loopback test server. Neither makes Azure calls or starts Core Tools. Repeat the deployed tests in step 6: local fixture headers cannot prove token validation, tenant restrictions or platform configuration. Record results in locally created `data/evidence.md`; never paste bearer tokens, secrets or full principal headers.

## Troubleshooting table

| Symptom | Check |
|---|---|
| Local connection refused | `func start` is running on port 7071; URL matches route. |
| Token acquisition fails | API scope, delegated consent, tenant and selected developer identity. |
| Cloud 401 | Easy Auth issuer/audience and actual caller token target. |
| Cloud 403 | App role assignment, fresh token and role claim mapping. |
| MCP connection refused | Server terminal active; client uses `/mcp` on port 8000. |
| Toolbox cannot reach tool | Cloud-reachable endpoint, connection authentication and outbound networking. |

## Cleanup

Stop both local servers with Ctrl+C. Run `python cleanup.py` for the cleanup checklist. Instructor reviews dependencies and removes only dedicated lab Function/hosting/storage resources, optional workflow, Toolbox versions/connections and lab-only identity assignments. No cleanup script deletes shared resources. Remove `.env`, local settings and any local token-bearing diagnostic files before distribution.

## Knowledge check

1. Does declaring a function schema host the tool? **Answer:** no; the application or service executes it.
2. Why can the local principal fixture not prove authentication? **Answer:** Core Tools accepts supplied headers; deployed Easy Auth must validate the token first.
3. Does Toolbox registration move tool code into the model? **Answer:** no; it centralises configuration/discovery while execution remains at the tool's service boundary.

## Stretch challenge

Add a second read-only synthetic operation. Update the handler, app authorisation decision, OpenAPI contract and MCP discovery; verify both authorised and denied behaviour. Compare it with Lab 16's local orchestration, explaining why A2A additionally requires a network protocol and task contract.

## References

- [Functions Python programming model](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- [Configure Entra authentication](https://learn.microsoft.com/en-us/azure/app-service/configure-authentication-provider-aad)
- [Platform principal headers](https://learn.microsoft.com/en-us/azure/app-service/configure-authentication-user-identities)
- [MCP Python SDK and transports](https://github.com/modelcontextprotocol/python-sdk)
- [Create and consume Toolboxes](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/toolbox)
- [Foundry OpenAPI tools](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/openapi)
- [Logic Apps managed identity authentication](https://learn.microsoft.com/en-us/azure/logic-apps/authenticate-with-managed-identity)
- [Foundry A2A tools](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/agent-to-agent)
