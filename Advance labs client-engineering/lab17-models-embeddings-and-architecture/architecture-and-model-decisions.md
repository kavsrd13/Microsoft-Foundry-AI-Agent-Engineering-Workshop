# Architecture and model decision exercise

Use one sheet per team. Deliver a diagram annotated with actual resource IDs, service identities, processing region and measured evidence. This is an inspection/design exercise; it does not automatically provision services.

| Component | Responsibility | Evidence to collect |
|---|---|---|
| Foundry account and projects | Administrative boundary, deployments, project assets and access | Account/project IDs; project role versus account role |
| Models/catalogue | Available model families and their model cards | Model/version, capability, supported input/output and deployment types |
| Agent Service | Versioned prompt assets and managed execution | Agent name/version, endpoint and runtime type |
| Tools/Toolboxes | External actions and reusable tool registration | Tool URL, execution host, identity and approval rule |
| Foundry IQ | Knowledge-source retrieval/planning capabilities | Source connection, query evidence and feature status |
| Control Plane | Inventory, governance and operational views | An asset's owner, compliance view and telemetry link |
| Foundry Local | Local model inference | Hardware/runtime, cached model and offline inference result |
| Storage | Original files and ingestion artefacts | Blob object path and upload/update time |
| Azure AI Search | Searchable content, embeddings and permission fields | Index schema, vector dimensions and example filter |
| Cosmos DB | Runtime state or application-owned data, depending on setup | Database/container and partition/retention settings |

Foundry's consolidated account/project model does not mean Storage, Search, Cosmos and compute cease to be separately billed Azure resources or use the same resource provider. Inspect resource `type` values in Azure Resource Explorer. Distinguish management-plane RBAC from data-plane access. Never equate a project role with permission to read all data stores.

1. Trace one request: browser identity → API → authorised Search query → model → response. Trace ingestion separately: original document → extraction → chunks → embeddings → index.
2. Place conversation storage on the diagram. For basic managed setup, do not claim state is in your own Cosmos account; for standard BYO, inspect the actual configured connections.
3. Mark every crossing of a process, network, identity and data-residency boundary. Compare a private runtime with a developer laptop outside the network.
4. Inspect three catalogue cards: a compact general model, a reasoning-capable model and an embedding model. Record modality, context limits, model licence/terms and task suitability. Model family alone is not a compliance decision.
5. Complete the deployment comparison below using current portal availability, then run the short scripts. Do not provision all options.

| Option to inspect | Decision to justify |
|---|---|
| Global Standard | Whether globally processed requests are approved; token consumption and capacity |
| Regional Standard | Exact region/model availability and processing requirements |
| Provisioned throughput (PTU) | Reserved capacity, expected utilisation, throughput testing and commitment cost |
| Serverless/API offering | Whether this model offers the option, provider terms and consumption meter |
| Managed compute | Whether this model supports a managed deployment, instance/GPU sizing and scaling responsibility |
| Local | Device resources, supported model, initial downloads and any remote tools/telemetry |

The options are not mutually available for every catalogue model; do not treat PTU, managed compute and serverless as interchangeable SKU names. Document the selected product and actual deployment option.

## Cost worksheet

Record current currency, pricing date, region, model/version and pricing source. Estimate model input/output/embedding tokens separately. Then add Search tier/replicas/partitions, Blob capacity/operations, Cosmos throughput/storage, Functions/hosting, evaluation judge tokens, telemetry ingestion/retention and any security/licensing charges. Use a low/expected/high traffic scenario. Do not label sample rates as current Azure prices.

Deliver: model comparison output, embedding ranking/dimensions, architecture diagram, deployment decision and a cost worksheet with assumptions. Instructor checks that residency is based on deployment type and service terms rather than resource location alone.

Sources: [SDK/resource access](https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview), [deployment types](https://learn.microsoft.com/azure/ai-foundry/openai/how-to/deployment-types), [standard BYO](https://learn.microsoft.com/azure/foundry/agents/concepts/standard-agent-setup), [Local](https://learn.microsoft.com/azure/foundry-local/get-started), [pricing calculator](https://azure.microsoft.com/pricing/calculator/).

## Authoring surfaces inspection

Using a workshop-owned agent, locate its version in the portal and compare the model/instructions/tool fields with Lab03 SDK source. Open the same source in VS Code; record the installed Foundry extension version and which create/run/debug features it actually exposes. In the official REST reference, locate the corresponding agent create/version and inference operations; record endpoint, API version, Entra scope and request fields. Compare the REST JSON with the SDK objects without printing bearer tokens. Do not assume the portal, extension and SDK expose every preview simultaneously. Evidence: a four-column portal/SDK/REST/VS Code comparison with one confirmed capability and one limitation per surface. The SDK build is the mandatory hands-on path; duplicating it in every surface is optional.

[Foundry documentation and API references](https://learn.microsoft.com/azure/foundry/)
