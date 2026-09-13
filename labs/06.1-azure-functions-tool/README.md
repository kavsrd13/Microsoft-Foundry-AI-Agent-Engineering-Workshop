# Exercise 06.1 — Host an agent tool on Azure Functions (queue-based)

A Microsoft Foundry agent calls an Azure Function through Azure Storage queues: the agent writes a
request to an input queue, a queue-triggered Function answers on an output queue,
and the agent picks the answer up. Requires the **standard** agent setup, which
`azd provision` creates from the infrastructure templates in `infra/`.

- `azure.yaml` — azd project manifest mapping the `api` service to `./app/` (Python Azure Function).
- `infra/` — Bicep templates for the standard setup (Storage, Search, Cosmos DB, Foundry account,
  project, model deployment, capability hosts, and RBAC role assignments) plus a Flex Consumption Function app.
- `app/` — the queue-triggered Function app (`function_app.py`, `host.json`, `requirements.txt`). Deploy with `azd deploy`.
- `ask_the_agent.py` — the agent-side script using `azure-ai-projects` to define the tool, register the agent, and query it.
- `solution/` — reference completed solution files.

Follow the step-by-step instructions in the workshop documentation to complete this lab.
