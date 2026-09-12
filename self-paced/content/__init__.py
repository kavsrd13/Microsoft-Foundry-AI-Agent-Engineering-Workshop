"""Structured content for the self-paced exercise pages."""

from . import advanced1, advanced2, day1, day2, day3, day4

LABS = day1.LABS + day2.LABS + day3.LABS + day4.LABS + advanced1.LABS + advanced2.LABS

GROUPS = [
    ("Day 1 — Foundry foundations",
     "Connect to a project, deploy a model and choose its type, create a versioned agent, and call models "
     "directly with the Responses API."),
    ("Day 2 — Tools and retrieval",
     "Give an agent tools, extract documents, build a managed vectorisation pipeline, and trim retrieval by "
     "permission."),
    ("Day 3 — Enterprise capabilities",
     "Retrieve with Foundry IQ, connect MCP tools under explicit approval, evaluate answers, and trace runs "
     "into Application Insights."),
    ("Day 4 — Microsoft Agent Framework",
     "Compare the framework with the direct SDK, persist sessions, intercept calls with middleware, and "
     "orchestrate multi-agent workflows. *These exercises use a separate, incompatible package set.*"),
    ("Advanced — client engineering",
     "Model and cost decisions, a full RAG pipeline with measured retrieval quality, Cosmos state and vectors, "
     "hosted tools, an authenticated streaming application, deployment with CI gates, and production "
     "governance."),
]

MODULE_MAP = [
    ("**1. Platform foundations** — component services, project and RBAC model, bring-your-own Storage / "
     "Search / Cosmos, AU residency, pricing",
     "[01](Instructions/Exercises/01-foundry-setup.html), "
     "[17](Instructions/Exercises/17-models-embeddings-and-architecture.html), "
     "[19](Instructions/Exercises/19-cosmos-state-and-vectors.html), "
     "[22](Instructions/Exercises/22-deployment-and-devops.html), "
     "[24](Instructions/Exercises/24-enterprise-security-and-governance.html)"),

    ("**2. Models and the catalogue** — families, deployment options, Responses inference, multimodal, "
     "embeddings, Foundry Local",
     "[02](Instructions/Exercises/02-model-deployment.html), "
     "[04](Instructions/Exercises/04-responses-api.html), "
     "[17](Instructions/Exercises/17-models-embeddings-and-architecture.html)"),

    ("**3. Building an agent end to end** — anatomy, lifecycle, authoring surfaces, Agent Framework",
     "[03](Instructions/Exercises/03-prompt-agent.html), "
     "[05](Instructions/Exercises/05-function-tools.html), "
     "[13](Instructions/Exercises/13-maf-transition.html)–"
     "[16](Instructions/Exercises/16-orchestration-and-hosted.html), "
     "[21](Instructions/Exercises/21-agent-web-application.html)"),

    ("**4. RAG and grounding** — ingestion, chunking, integrated vectorisation, index design, hybrid and "
     "semantic retrieval, OCR, incremental re-indexing, security trimming, retrieval quality",
     "[06](Instructions/Exercises/06-document-intelligence.html)–"
     "[09](Instructions/Exercises/09-foundry-iq.html), "
     "[18](Instructions/Exercises/18-end-to-end-rag.html), "
     "[21](Instructions/Exercises/21-agent-web-application.html), "
     "[23](Instructions/Exercises/23-evaluation-and-operations.html)"),

    ("**5. State, memory and data stores** — thread storage, RU/s, BYO split, Cosmos vectors, short and "
     "long-term memory",
     "[14](Instructions/Exercises/14-session-and-context.html), "
     "[19](Instructions/Exercises/19-cosmos-state-and-vectors.html)"),

    ("**6. Tools, functions and multi-agent orchestration** — function calling, Azure Functions hosting, MCP, "
     "OpenAPI, Toolboxes, Logic Apps, A2A, workflows",
     "[05](Instructions/Exercises/05-function-tools.html), "
     "[10](Instructions/Exercises/10-mcp-tools.html), "
     "[16](Instructions/Exercises/16-orchestration-and-hosted.html), "
     "[20](Instructions/Exercises/20-hosted-tools-and-integrations.html)"),

    ("**7. Deployment, publishing and DevOps** — managed endpoints, Teams and M365 Copilot, Functions, "
     "containers and autoscaling, custom app with streaming, CI/CD, IaC, environment promotion",
     "[16](Instructions/Exercises/16-orchestration-and-hosted.html), "
     "[21](Instructions/Exercises/21-agent-web-application.html), "
     "[22](Instructions/Exercises/22-deployment-and-devops.html)"),

    ("**8. Production** — offline and CI evaluation, OpenTelemetry and Application Insights, token and cost "
     "telemetry, Entra Agent ID and Conditional Access, Defender and Purview, content safety, red teaming, "
     "readiness and cost management",
     "[11](Instructions/Exercises/11-evaluation.html), "
     "[12](Instructions/Exercises/12-tracing-and-governance.html), "
     "[22](Instructions/Exercises/22-deployment-and-devops.html), "
     "[23](Instructions/Exercises/23-evaluation-and-operations.html), "
     "[24](Instructions/Exercises/24-enterprise-security-and-governance.html)"),
]

__all__ = ["LABS", "GROUPS", "MODULE_MAP"]
