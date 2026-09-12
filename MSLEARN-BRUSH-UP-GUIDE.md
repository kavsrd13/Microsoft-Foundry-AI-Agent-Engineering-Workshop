# Microsoft Learn brush-up guide

Prepared for the eight-module Microsoft Foundry Agent Engineering course. Links were checked against Microsoft Learn on 11 September 2026. Foundry is changing quickly, so check the status and region tables again before delivery.

## How to use this guide

- **Core**: read before teaching the module.
- **Deep dive**: use while rehearsing its labs.
- **Training**: a structured Microsoft Learn module or learning path when you want guided study.

If time is limited, complete these four learning paths first:

1. [Develop AI agents on Azure](https://learn.microsoft.com/training/paths/develop-ai-agents-azure/) — Agent Service, Agent Framework, tools, Foundry IQ, workflows, A2A and Microsoft 365 integration.
2. [Training for Azure AI Search](https://learn.microsoft.com/azure/search/resource-training) — the Search learning paths and RAG-focused modules in one index.
3. [Operationalize generative AI applications](https://learn.microsoft.com/training/paths/operationalize-gen-ai-apps/) — versioning, evaluation automation, GitHub Actions, monitoring and tracing.
4. [Build production-grade multi-agent capabilities](https://learn.microsoft.com/training/paths/aaai-2-build-production-grade-multi-agent-capabilities-microsoft-foundry/) — advanced RAG, Cosmos memory and multi-agent engineering.

Before rehearsing deployment labs, install the [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli-windows), [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd) and [Microsoft Foundry Toolkit for Visual Studio Code](https://learn.microsoft.com/azure/foundry/how-to/develop/get-started-projects-visual-studio-code). The current authoring computer has Azure CLI but does not yet have `azd`, so hosted deployment commands need that prerequisite before they can be rehearsed.

## 1. Foundry platform foundations and architecture

### Platform and component services

- **Core:** [What is Microsoft Foundry?](https://learn.microsoft.com/azure/ai-foundry/azure-openai-in-azure-ai-foundry) — current platform positioning, one management plane, models, agents, observability and governance.
- **Core:** [What is Microsoft Foundry Agent Service?](https://learn.microsoft.com/azure/ai-foundry/agents/overview) — runtime, toolboxes, models, identity, publishing and observability.
- **Core:** [What is Foundry IQ?](https://learn.microsoft.com/azure/ai-foundry/agents/concepts/what-is-foundry-iq?preserve-view=true&view=foundry) — knowledge bases, knowledge sources, agentic retrieval and permission-aware grounding.
- **Core:** [What is Microsoft Foundry Control Plane?](https://learn.microsoft.com/azure/foundry/control-plane/overview) — fleet inventory, governance, compliance, security and cost oversight.
- **Deep dive:** [Foundry Local documentation](https://learn.microsoft.com/azure/foundry-local/) — on-device architecture, SDK, CLI and tutorials.
- **Deep dive:** [Microsoft Foundry general availability overview](https://learn.microsoft.com/azure/foundry/concepts/general-availability) — distinguish GA, preview and classic experiences.

### Resource model, projects and RBAC

- **Core:** [Role-based access control for Microsoft Foundry](https://learn.microsoft.com/azure/foundry/concepts/rbac-foundry) — account, project and agent scopes; Foundry roles and least privilege.
- **Core:** [Agent identity concepts in Microsoft Foundry](https://learn.microsoft.com/azure/foundry/agents/concepts/agent-identity) — project identity, per-agent identity and permissions after publishing.
- **Deep dive:** [Foundry Agent Service limits, quotas and regions](https://learn.microsoft.com/azure/foundry/agents/concepts/limits-quotas-regions) — region and tool availability, including Australia East.

### Bring your own resources and networking

- **Core:** [Set up standard Agent Service resources](https://learn.microsoft.com/azure/foundry/agents/concepts/standard-agent-setup) — Storage, Search, Cosmos DB, `enterprise_memory`, containers and throughput prerequisites.
- **Core:** [Use your own resources in Foundry Agent Service](https://learn.microsoft.com/azure/foundry/agents/how-to/use-your-own-resources) — resource IDs, capability-host connections and ownership boundaries.
- **Core:** [Networking options for Foundry Agent Service](https://learn.microsoft.com/azure/foundry/agents/concepts/networking-options) — public, private and BYO data-resource choices.
- **Deep dive:** [Set up private networking for Foundry Agent Service](https://learn.microsoft.com/azure/ai-foundry/agents/how-to/virtual-networks) — private endpoints, DNS, VNet and standard setup.

### Australia, residency and cost

- **Core:** [Data, privacy and security for models in Foundry](https://learn.microsoft.com/azure/foundry/responsible-ai/openai/data-privacy) — processing versus storage, Global/Data Zone/regional deployments and Responses API persistence.
- **Core:** [Foundry Agent Service regions and tool support](https://learn.microsoft.com/azure/foundry/agents/concepts/limits-quotas-regions) — verify every model, agent and tool needed in Australia East.
- **Deep dive:** [List of Azure regions](https://learn.microsoft.com/azure/reliability/regions-list) and [Azure region pairs](https://learn.microsoft.com/azure/reliability/regions-paired) — Australia East and Australia Southeast geography context.
- **Deep dive:** [Microsoft Entra ID data residency](https://learn.microsoft.com/entra/fundamentals/data-residency) — identity data has its own residency model.
- **Core:** [Plan and manage Foundry costs](https://learn.microsoft.com/azure/foundry/concepts/manage-costs) — estimates, meters, budgets, alerts, chargeback and supporting-service costs.

## 2. Models and the model catalogue

### Model selection

- **Core:** [Microsoft Foundry Models overview](https://learn.microsoft.com/azure/foundry/concepts/foundry-models-overview) — catalog filters, providers, lifecycle, model cards and deployment options.
- **Core:** [Model benchmarks and leaderboards](https://learn.microsoft.com/azure/foundry/concepts/model-benchmarks) — quality, safety, cost, latency, throughput and embedding benchmarks.
- **Training:** [Select, deploy and evaluate Foundry models](https://learn.microsoft.com/training/modules/model-catalog-evaluate/) — guided comparison workflow.
- **Deep dive:** [Model migration and switching](https://learn.microsoft.com/azure/foundry/foundry-models/concepts/model-migration) — evaluate on your workload before changing production models.

### Deployment options

- **Core:** [Model deployment overview](https://learn.microsoft.com/azure/foundry/concepts/deployments-overview) — serverless API, instant access and managed compute.
- **Core:** [Deployment types for Foundry Models](https://learn.microsoft.com/azure/ai-foundry/foundry-models/concepts/deployment-types?view=foundry-classic) — Global Standard, Data Zone, regional, provisioned and batch processing.
- **Deep dive:** [Provisioned throughput](https://learn.microsoft.com/azure/foundry/openai/concepts/provisioned-throughput) — PTUs, predictable throughput and geography choices.
- **Deep dive:** [Managed compute](https://learn.microsoft.com/azure/foundry/concepts/managed-compute-overview) — dedicated managed GPU hosting for open/custom models and its preview limitations.

### Inference, multimodal and embeddings

- **Core:** [Use the Azure OpenAI Responses API](https://learn.microsoft.com/azure/foundry/openai/how-to/responses) — OpenAI-compatible request, streaming, state, tools, image and file inputs.
- **Deep dive:** [Responses API REST reference](https://learn.microsoft.com/rest/api/aifoundry/azureopenai/responses) — exact request and response contract.
- **Core:** [Embeddings and document search tutorial](https://learn.microsoft.com/azure/foundry/openai/tutorials/embeddings) — embedding models, cosine similarity and document retrieval.
- **Deep dive:** [Embeddings REST reference](https://learn.microsoft.com/rest/api/aifoundry/azureopenai/embeddings) — dimensions parameter, input constraints and endpoint.
- **Deep dive:** [Choose an Azure vector-search service](https://learn.microsoft.com/azure/architecture/guide/technology-choices/vector-search) — dimensions and store trade-offs across Search, Cosmos DB and other Azure databases.
- **Optional:** [Get started with Foundry Local](https://learn.microsoft.com/azure/foundry-local/get-started) — supported-device setup and local model execution.

## 3. Building an agent end to end

### Agent anatomy and lifecycle

- **Core:** [Agent development lifecycle](https://learn.microsoft.com/azure/foundry/agents/concepts/development-lifecycle) — choose, create, add tools/data, version, trace, evaluate, publish and monitor.
- **Core:** [Agent runtime components](https://learn.microsoft.com/azure/foundry/agents/concepts/runtime-components) — agents, conversations, responses and managed memory.
- **Hands-on:** [Get started with the Microsoft Foundry SDK](https://learn.microsoft.com/azure/foundry/quickstarts/get-started-code?tabs=portal&view=foundry) — model response, agent and multi-turn conversation.
- **Hands-on:** [Build agents using the Responses API](https://learn.microsoft.com/azure/foundry/agents/quickstarts/responses-api) — ephemeral agent, tools and streaming.
- **Reference:** [Microsoft Foundry REST API](https://learn.microsoft.com/rest/api/aifoundry/project/responses) — project-level Responses and agent-reference contract.

### Authoring surfaces

- **Core:** [Foundry Toolkit for Visual Studio Code](https://learn.microsoft.com/azure/foundry/how-to/develop/get-started-projects-visual-studio-code) — models, Agent Builder, Tool Catalog, Agent Inspector, deployment and monitoring.
- **Deep dive:** [Create hosted-agent workflows in Foundry Toolkit](https://learn.microsoft.com/azure/foundry/agents/how-to/vs-code-agents-workflow-pro-code?view=foundry) — local test and hosted deployment flow.
- **Index:** [Microsoft Foundry quickstarts](https://learn.microsoft.com/azure/foundry/quickstarts/quickstarts) — portal and code routes for agents, toolboxes, deployment, tracing and evaluation.

### Microsoft Agent Framework

- **Core:** [Microsoft Agent Framework documentation](https://learn.microsoft.com/agent-framework/) — central index for agents, workflows, memory, middleware, RAG, security and hosting.
- **Core:** [Agent capabilities](https://learn.microsoft.com/agent-framework/agents/) — context, knowledge, tools, observability and safety capabilities.
- **Deep dive:** [Agent pipeline architecture](https://learn.microsoft.com/agent-framework/agents/agent-pipeline) — history providers, context providers, middleware, tool invocation and telemetry.
- **Hands-on:** [Agent Framework workflow builder and execution](https://learn.microsoft.com/agent-framework/workflows/workflows) — executors, edges, validation, streaming and parallel supersteps.

## 4. RAG and grounding on enterprise data

### End-to-end RAG design and chunking

- **Core:** [Design and develop a RAG solution](https://learn.microsoft.com/azure/architecture/ai-ml/guide/rag/rag-solution-design-and-evaluation-guide) — the complete design and evaluation series.
- **Core:** [Chunk documents for RAG and vector search](https://learn.microsoft.com/azure/search/vector-search-how-to-chunk-documents) — chunk sizes, overlap, Text Split and custom strategies.
- **Core:** [Integrated vectorization](https://learn.microsoft.com/azure/search/vector-search-integrated-vectorization) — data source, indexer, skillset, Text Split, embedding skill, index and query vectorizer.
- **Deep dive:** [Vector search overview](https://learn.microsoft.com/azure/search/vector-search-overview) — index architecture, algorithms, vectorizers and ingestion choices.

### Indexing and freshness

- **Core:** [Create a Search index](https://learn.microsoft.com/azure/search/search-how-to-create-search-index) — field types, keys, searchable/filterable/retrievable settings.
- **Core:** [Run or reset Search indexers](https://learn.microsoft.com/azure/search/search-howto-run-reset-indexers) — incremental indexing, high-water marks, scheduling and resets.
- **Deep dive:** [Azure SQL indexer change and deletion detection](https://learn.microsoft.com/azure/search/search-howto-connecting-azure-sql-database-to-azure-search-using-indexers) — concrete update/delete tracking patterns.

### Retrieval and reranking

- **Core:** [Hybrid search overview](https://learn.microsoft.com/azure/search/hybrid-search-overview) and [create a hybrid query](https://learn.microsoft.com/azure/search/hybrid-search-how-to-query) — BM25 plus vector retrieval.
- **Core:** [Semantic ranking overview](https://learn.microsoft.com/azure/search/semantic-search-overview) — semantic reranking, captions and answers.
- **Deep dive:** [Hybrid scoring with reciprocal rank fusion](https://learn.microsoft.com/azure/search/hybrid-search-ranking) — RRF score composition and query weighting.
- **Deep dive:** [RAG information-retrieval phase](https://learn.microsoft.com/azure/architecture/ai-ml/guide/rag/rag-information-retrieval) — query strategies, reranking, Precision@K, Recall@K and MRR.

### OCR and scanned documents

- **Core:** [Document Intelligence Read OCR model](https://learn.microsoft.com/azure/ai-services/document-intelligence/prebuilt/read?view=doc-intel-4.0.0) — scanned-document extraction and searchable PDFs.
- **Deep dive:** [Multimodal indexing with Document Layout](https://learn.microsoft.com/azure/search/tutorial-multimodal) — extract, chunk and vectorize text and image content.

### Identity-aware retrieval

- **Core:** [Document-level access control in Azure AI Search](https://learn.microsoft.com/azure/search/search-document-level-access-overview) — native permission approaches and filter-based security trimming.
- **Core:** [Azure AI Search security best practices](https://learn.microsoft.com/azure/search/search-security-best-practices) — identities, network controls, encryption and document-level access.
- **Deep dive:** [Foundry IQ](https://learn.microsoft.com/azure/ai-foundry/agents/concepts/what-is-foundry-iq?preserve-view=true&view=foundry) — shared permission-aware knowledge bases, ACL synchronization and Entra user identity.

### RAG measurement

- **Core:** [RAG retrieval evaluation](https://learn.microsoft.com/azure/architecture/ai-ml/guide/rag/rag-information-retrieval#evaluate-your-search-results) — Precision@K, Recall@K, MRR and negative tests.
- **Core:** [RAG end-to-end LLM evaluation](https://learn.microsoft.com/azure/architecture/ai-ml/guide/rag/rag-llm-evaluation-phase) — groundedness, completeness, utilization, relevance and correctness.
- **Deep dive:** [Foundry RAG evaluators](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/rag-evaluators) — groundedness, retrieval and document-retrieval evaluators.

## 5. State, memory and data stores

### Where state is stored

- **Core:** [Agent runtime components](https://learn.microsoft.com/azure/foundry/agents/concepts/runtime-components) — conversations, responses and managed memory.
- **Core:** [Foundry Agent Service FAQ](https://learn.microsoft.com/azure/foundry/agents/faq) — what is retained under Basic versus Standard setup.
- **Core:** [Standard Agent Service setup](https://learn.microsoft.com/azure/foundry/agents/concepts/standard-agent-setup) — `enterprise_memory`, runtime-specific containers and Cosmos throughput prerequisites.
- **Deep dive:** [Use your own resources](https://learn.microsoft.com/azure/foundry/agents/how-to/use-your-own-resources) — Storage for files, Cosmos DB for state and Search for vector stores.

### Cosmos DB and vector-store choice

- **Hands-on:** [Index and query vectors in Cosmos DB using Python](https://learn.microsoft.com/azure/cosmos-db/nosql/how-to-python-vector-index-query) — embedding policy, vector index and vector query.
- **Hands-on:** [Cosmos DB vector-store Python quickstart](https://learn.microsoft.com/azure/cosmos-db/quickstart-vector-store-python) — complete runnable application pattern.
- **Core:** [Agent memory in Cosmos DB](https://learn.microsoft.com/azure/cosmos-db/gen-ai/agentic-memories) — semantic and keyword memory patterns.
- **Core:** [Choose an Azure vector-search service](https://learn.microsoft.com/azure/architecture/guide/technology-choices/vector-search) — use Cosmos for frequently changing operational data; use Search for first-class enterprise indexing, hybrid search and semantic ranking.

### Framework-managed and application-managed memory

- **Core:** [Agent Framework pipeline architecture](https://learn.microsoft.com/agent-framework/agents/agent-pipeline) — chat-history providers versus context providers for memory and RAG.
- **Deep dive:** [Self-host Agent Framework applications](https://learn.microsoft.com/agent-framework/hosting/self-hosting) — production session-store responsibility when self-hosting.
- **Deep dive:** [Agent Framework Durable Extension](https://learn.microsoft.com/agent-framework/integrations/azure-functions) — persistent sessions, workflow checkpoints and Azure Functions hosting.

## 6. Tools, functions and multi-agent orchestration

### Toolboxes and function calling

- **Core:** [Toolbox overview](https://learn.microsoft.com/azure/foundry/agents/concepts/toolbox-overview) — one managed MCP endpoint, discovery, versioning and supported tool types.
- **Hands-on:** [Create and manage a toolbox](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/toolbox) — SDK and `azd` configurations.
- **Hands-on:** [Toolbox with a hosted agent quickstart](https://learn.microsoft.com/azure/foundry/agents/quickstarts/quickstart-toolbox-agent) — complete hosted-agent example.
- **Core:** [Function calling with Foundry agents](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/function-calling) — function schema, execution loop and security considerations.
- **Framework:** [Function tools in Agent Framework](https://learn.microsoft.com/agent-framework/agents/tools/function-tools) — application-owned function tools and runtime control.

### Azure Functions, MCP, OpenAPI and Logic Apps

- **Core:** [Use Azure Functions with Foundry agents](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/azure-functions) — Functions versus in-process functions, queues, MCP and HTTP/OpenAPI options.
- **Core:** [Connect agents to MCP server endpoints](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/model-context-protocol) — remote MCP tools, authentication and toolbox integration.
- **Core:** [Connect OpenAPI tools](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/openapi) — required OpenAPI contract and anonymous, connection or managed-identity authentication.
- **Core:** [Automate Foundry agents with Logic Apps](https://learn.microsoft.com/azure/logic-apps/automate-foundry-agents-with-workflows) — triggers, connectors, webhooks and exposing connector actions as tools.
- **Deep dive:** [Logic Apps custom connectors](https://learn.microsoft.com/azure/logic-apps/custom-connector-overview) — wrapping an API and choosing least-privilege authentication.

### Multi-agent and A2A

- **Core:** [Multi-agent patterns](https://learn.microsoft.com/agents/architecture/multi-agent-patterns) — sequential, concurrent and human-review patterns.
- **Hands-on:** [Agents in Agent Framework workflows](https://learn.microsoft.com/agent-framework/workflows/agents-in-workflows) — specialized agents inside a graph workflow.
- **Core:** [Connect to an A2A endpoint](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/agent-to-agent) — outgoing A2A integration and its preview boundary.
- **Deep dive:** [Enable incoming A2A on a Foundry agent](https://learn.microsoft.com/azure/foundry/agents/how-to/enable-agent-to-agent-endpoint) — agent card, protocol endpoint, version and RBAC.
- **Security:** [A2A authentication](https://learn.microsoft.com/azure/foundry/agents/concepts/agent-to-agent-authentication) — OBO and application-only identity choices.

## 7. Deployment, publishing and DevOps

### Hosted agents and stable endpoints

- **Core:** [Deploy a hosted agent](https://learn.microsoft.com/azure/foundry/agents/how-to/deploy-hosted-agent) — code/container packaging, local testing, deployment and lifecycle.
- **Hands-on:** [Deploy your own code as a hosted agent](https://learn.microsoft.com/azure/foundry/agents/quickstarts/quickstart-deploy-own-code?tabs=responses) — `azd` initialization, provision, run, deploy and invoke.
- **Framework:** [Host Agent Framework agents in Foundry](https://learn.microsoft.com/azure/foundry/how-to/develop/framework-hosted-agents) — Responses and Invocations protocols.
- **Current model:** [Migrate to the new Foundry agent model](https://learn.microsoft.com/azure/foundry/agents/how-to/migrate-agent-applications) — stable endpoints and unique identities now attached directly to new agents.
- **Legacy context:** [Agent applications](https://learn.microsoft.com/azure/foundry/agents/how-to/agent-applications) — useful for existing tenants still using the earlier application/deployment model.

### Teams and Microsoft 365 Copilot

- **Core:** [Publish agents to Microsoft 365 Copilot and Teams](https://learn.microsoft.com/azure/foundry/agents/how-to/publish-copilot) — portal publishing, versions and permissions.
- **Deep dive:** [Publish through REST with private-network considerations](https://learn.microsoft.com/azure/foundry/agents/how-to/publish-copilot-virtual-network) — Activity Protocol route, authentication and data-flow limitations.
- **Training:** [Integrate a Foundry agent with Microsoft 365](https://learn.microsoft.com/training/modules/integrate-foundry-agent-with-m365/) — publishing and testing workflow.

### Functions, containers, web app and streaming

- **Core:** [Agent Framework hosting choices](https://learn.microsoft.com/agent-framework/get-started/hosting) — A2A, OpenAI-compatible endpoints, durable Functions and web UI protocols.
- **Deep dive:** [Agent Framework Durable Extension](https://learn.microsoft.com/agent-framework/integrations/azure-functions) — durable agents and workflows on Functions or self-hosted compute.
- **Hands-on:** [Deploy a Python web app to App Service](https://learn.microsoft.com/azure/app-service/quickstart-python) — Flask, Django or FastAPI deployment.
- **Core:** [Container service architectural considerations](https://learn.microsoft.com/azure/architecture/guide/container-service-general-considerations) — Container Apps, App Service containers and AKS trade-offs.
- **Hands-on:** [Configure Container Apps scaling](https://learn.microsoft.com/azure/container-apps/scale-app) — HTTP, TCP and event-driven KEDA rules.

### CI/CD, Bicep and environment promotion

- **Core:** [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/) and [azd template structure](https://learn.microsoft.com/azure/developer/azure-developer-cli/azd-templates) — application, infrastructure and pipeline layout.
- **Core:** [What is Bicep?](https://learn.microsoft.com/azure/azure-resource-manager/bicep/overview) — declarative, repeatable Azure infrastructure.
- **Training:** [Fundamentals of Bicep](https://learn.microsoft.com/training/paths/fundamentals-bicep/) — structured IaC preparation.
- **Security:** [Authenticate GitHub Actions to Azure using OIDC](https://learn.microsoft.com/azure/developer/github/connect-from-azure-openid-connect) — federated credentials without long-lived deployment secrets.
- **Core:** [Work with azd environments](https://learn.microsoft.com/azure/developer/azure-developer-cli/work-with-environments) — isolated dev, test and prod settings.
- **Deep dive:** [Manage azd environment variables](https://learn.microsoft.com/azure/developer/azure-developer-cli/manage-environment-variables) — configuration, IaC parameters and secret considerations.

## 8. Production: evaluation, observability, security and governance

### Evaluation and CI gates

- **Core:** [Observability in generative AI](https://learn.microsoft.com/azure/ai-foundry/concepts/evaluation-approach-gen-ai) — evaluation, monitoring and tracing across development and production.
- **Core:** [RAG evaluators](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/rag-evaluators) — groundedness, relevance, retrieval and document retrieval.
- **Core:** [Agent evaluators](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/agent-evaluators?preserve-view=true&view=foundry) — task completion, tool-call quality and workflow-level assessment.
- **Hands-on:** [Run evaluations and CI gates with azd](https://learn.microsoft.com/azure/foundry/observability/how-to/azure-developer-cli-evaluation) — versioned evaluation recipes, datasets, custom evaluators and `--fail-on`.
- **Deep dive:** [Agent monitoring dashboard](https://learn.microsoft.com/azure/foundry/observability/how-to/how-to-monitor-agents-dashboard?view=foundry) — continuous/scheduled evaluation, alerts and red-team scans.

### OpenTelemetry, Application Insights and cost telemetry

- **Core:** [Agent tracing overview](https://learn.microsoft.com/azure/foundry/observability/concepts/trace-agent-concept) — spans, tool calls, token use, latency and multi-agent conventions.
- **Hands-on:** [Set up Foundry agent tracing](https://learn.microsoft.com/azure/foundry/observability/how-to/trace-agent-setup) — OpenTelemetry export and Application Insights inspection.
- **Operations:** [Monitor agents with the dashboard](https://learn.microsoft.com/azure/foundry/observability/how-to/how-to-monitor-agents-dashboard?view=foundry) — performance, token usage, quality and safety signals.
- **Cost:** [Plan and manage Foundry costs](https://learn.microsoft.com/azure/foundry/concepts/manage-costs) — estimates, actual meters, budgets, alerts and chargeback.
- **Training:** [Monitor, evaluate and operate multi-agent solutions](https://learn.microsoft.com/training/paths/aaai-4-monitor-evaluate-operate-multi-agent-ai-solutions-azure/) — distributed tracing, LLM-as-judge evaluation and production incident work.

### Identity and Conditional Access

- **Core:** [Microsoft Entra Agent ID key concepts](https://learn.microsoft.com/entra/agent-id/key-concepts) — agent identities, blueprints and credentials.
- **Core:** [Overview of agent identities](https://learn.microsoft.com/entra/agent-id/agent-identities) — identity inventory and policy inheritance.
- **Core:** [Conditional Access for agents](https://learn.microsoft.com/entra/identity/conditional-access/agent-id) — delegated, autonomous and agent-user flows plus current licensing and enforcement boundaries.
- **Deep dive:** [Security for AI overview](https://learn.microsoft.com/entra/agent-id/security-for-ai-overview) — Zero Trust, identity protection and governance.
- **Governance:** [Govern agent identities](https://learn.microsoft.com/entra/id-governance/agent-id-governance-overview) — sponsors, owners, lifecycle, access reviews and entitlement management.

### Defender, Purview and control plane

- **Core:** [Manage compliance and security in Foundry](https://learn.microsoft.com/azure/foundry/control-plane/how-to-manage-compliance-security) — guardrail policies, Defender findings and Purview integration.
- **Core:** [Use Microsoft Purview with Foundry](https://learn.microsoft.com/purview/ai-azure-foundry) — audit, DSPM for AI, classification and policy prerequisites.
- **Deep dive:** [Govern agent infrastructure as an Entra administrator](https://learn.microsoft.com/azure/foundry/control-plane/govern-agent-infrastructure-entra-admin) — discovery, ownership, access and response actions.

### Content safety and red teaming

- **Core:** [Azure AI Content Safety overview](https://learn.microsoft.com/azure/ai-services/content-safety/overview) — harm categories, Prompt Shields, protected material and groundedness.
- **Hands-on:** [Content Safety documentation and quickstarts](https://learn.microsoft.com/azure/ai-services/content-safety/) — text/image moderation and SDK links.
- **Deep dive:** [Groundedness detection](https://learn.microsoft.com/azure/ai-services/content-safety/concepts/groundedness) — detection modes, correction and limitations.
- **Core:** [AI Red Teaming Agent](https://learn.microsoft.com/azure/foundry/concepts/ai-red-teaming-agent) — automated adversarial scans, PyRIT foundation and human review.

### Production readiness

- **Core:** [Azure Well-Architected guidance for AI workloads](https://learn.microsoft.com/azure/well-architected/ai/) — reliability, security, cost, operations and performance decisions.
- **Core:** [App Service architecture best practices](https://learn.microsoft.com/azure/well-architected/service-guides/app-service-web-apps) — production reliability, security, scaling and cost considerations for the custom app.
- **Core:** [Autoscaling guidance](https://learn.microsoft.com/azure/architecture/best-practices/auto-scaling) — scaling signals, capacity and operational considerations.
- **Final check:** [Microsoft Foundry GA overview](https://learn.microsoft.com/azure/foundry/concepts/general-availability) and [Agent Service limits, quotas and regions](https://learn.microsoft.com/azure/foundry/agents/concepts/limits-quotas-regions) — repeat before every course delivery.

## Suggested preparation order

1. **Foundation:** Module 1 core pages, then Module 2 model selection and Responses API.
2. **Build:** Module 3 lifecycle/SDK pages and the Agent Framework documentation.
3. **Highest-value block:** Module 4 end-to-end RAG, then Module 5 state and vector-store choices.
4. **Extension:** Module 6 functions, MCP, OpenAPI, toolboxes and A2A.
5. **Delivery:** Module 7 hosted deployment, custom app, Bicep, CI/CD and publishing.
6. **Production:** Module 8 evaluation, telemetry, identity, governance, content safety and red teaming.

For each topic, write three teaching notes: **what the service owns**, **what the application owns**, and **what live evidence proves the feature works**. This prevents portal configuration, local validation and production readiness from being treated as the same thing.
