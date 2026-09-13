# Exercise 15 — Host a tool on Azure Functions (queue-based)

A Foundry agent calls an Azure Function through Storage queues: the agent writes a
request to an input queue, a queue-triggered Function answers on an output queue,
and the agent picks the answer up. Requires the **standard** agent setup, which
`azd provision` creates from the vendored `infra/`.

- `infra/` — Bicep for the standard setup (Storage, Search, Cosmos, Foundry account,
  project, capability hosts, role assignments) plus a Flex Consumption Function app.
  Vendored from Microsoft's `azure-functions-ai-services-agent-python` template, which
  is now archived; the Bicep targets the current `2025-04-01-preview` API.
- `app/` — the queue-triggered Function. Deploy with `azd deploy`.
- `solution/ask_the_agent.py` — the agent-side script you build in the exercise.

Follow the exercise page for the step-by-step instructions.
