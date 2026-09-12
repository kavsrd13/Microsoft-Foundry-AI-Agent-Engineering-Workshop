# Australian governance evidence checklist

For every row record an owner, evidence link, date checked and approved exception if applicable. Synthetic workshop data is not a production authorisation.

| Control | Evidence to obtain | Owner / evidence / date |
|---|---|---|
| Region | Project, Search, Storage, Cosmos DB and telemetry region separately verified; Australia East availability checked per feature | Pending |
| Deployment type | Record model SKU: Global / Data Zone / Regional and the actual processing commitment; resource location alone is insufficient | Pending |
| Managed VNet | Identify which managed network isolation options are supported for this deployment and verify effective outbound rules | Pending |
| Private endpoints | Resolve private DNS from the runtime and verify public network access settings for each service | Pending |
| Entra-only auth | Roles scoped to required resources, managed identities for workloads, local authentication disabled where supported | Pending |
| Purview sensitivity labels | Identify label policies and enforcement integration; attaching a label alone does not guarantee retrieval security | Pending |
| BYO Cosmos DB | For standard agent setup, verify current supported account configuration and the documented 3000 RU/s minimum before provisioning; obtain cost approval | Pending |
| Tenant-owned Storage and Search | Record subscription, tenant, encryption, access controls, retention and the standard-setup connections | Pending |
| Foundry User | Check least-privilege invocation and agent-development permissions against current role definition | Pending |
| Foundry Project Manager | Check current role name/definition, assignment scope and PIM activation for project operations | Pending |
| Foundry Account Owner | Check current role name/definition and limit privileged assignments | Pending |
| MCP egress | Approve endpoint, allowed tools and data sent in tool arguments; read-only does not mean data stays in Australia | Pending |
| Evaluation | Verify each judge and safety service region; record any cross-region processing approval | Pending |
| Tracing | Keep prompts/answers out of telemetry; verify workspace location, retention, RBAC and actual ingestion | Pending |

The workshop brief calls the roles “Foundry User, Project Manager, Account Owner”. Verify the full names and permissions in the live tenant rather than assigning a guessed role. This checklist never assigns roles or provisions infrastructure.

Sources: [standard setup](https://learn.microsoft.com/azure/foundry/agents/concepts/standard-agent-setup), [tracing](https://learn.microsoft.com/azure/foundry/observability/how-to/enable-tracing), [Entra telemetry ingestion](https://learn.microsoft.com/azure/azure-monitor/app/azure-ad-authentication).
