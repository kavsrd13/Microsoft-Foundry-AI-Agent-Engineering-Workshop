"""Structured content for the self-paced exercise pages.

Every code block shown on a page is sliced out of the matching file in
`labs/<lab>/solution/`, which is syntax-checked, import-checked against the
real pinned SDKs, and unit-tested for its pure logic. See `_code.py`.
"""

from . import labs_01_04, labs_05_09, labs_10_14

LABS = labs_01_04.LABS + labs_05_09.LABS + labs_10_14.LABS

GROUPS = [
    ("Day 1 — Foundations and your first agent",
     "Connect to Foundry, work out which model to use and what it costs, then build an agent that looks "
     "things up instead of guessing."),
    ("Day 2 — Retrieval and grounding",
     "The highest-value part of the workshop: turn documents into something searchable, answer from them "
     "with citations, show people only what they may see, and keep it all current."),
    ("Day 3 — Memory, tools and orchestration",
     "Give the agent memory that survives a restart, move tools into their own services, and get several "
     "agents working on one job."),
    ("Day 4 — Running it for real",
     "Measure whether it is any good, see what it is doing and what it costs, put a real user interface in "
     "front of it, and decide whether it is safe to ship."),
]

MODULE_MAP = [
    ("**1. Platform foundations** — components, projects and RBAC, bring-your-own Storage / Search / Cosmos, "
     "residency, pricing",
     "[01](Instructions/Exercises/01-get-started.html), "
     "[02](Instructions/Exercises/02-choose-a-model.html), "
     "[08](Instructions/Exercises/08-agent-memory.html), "
     "[14](Instructions/Exercises/14-secure-and-govern.html)"),

    ("**2. Models and the catalogue** — model families, deployment options, Responses inference, multimodal, "
     "embeddings",
     "[01](Instructions/Exercises/01-get-started.html), "
     "[02](Instructions/Exercises/02-choose-a-model.html)"),

    ("**3. Building an agent end to end** — instructions, versions, tools, lifecycle, Agent Framework",
     "[03](Instructions/Exercises/03-first-agent.html), "
     "[10](Instructions/Exercises/10-agent-framework.html), "
     "[13](Instructions/Exercises/13-chat-app.html)"),

    ("**4. RAG and grounding** — ingestion, chunking, vector indexing, hybrid and semantic retrieval, OCR, "
     "incremental re-indexing, security trimming, retrieval quality",
     "[04](Instructions/Exercises/04-prepare-documents.html)–"
     "[07](Instructions/Exercises/07-keep-the-index-fresh.html), "
     "[11](Instructions/Exercises/11-measure-quality.html), "
     "[13](Instructions/Exercises/13-chat-app.html)"),

    ("**5. State, memory and data stores** — where conversations live, TTL, Cosmos vs Search, short and "
     "long-term memory",
     "[08](Instructions/Exercises/08-agent-memory.html), "
     "[10](Instructions/Exercises/10-agent-framework.html)"),

    ("**6. Tools, functions and multi-agent orchestration** — function calling, Azure Functions hosting, MCP, "
     "OpenAPI, workflows",
     "[03](Instructions/Exercises/03-first-agent.html), "
     "[09](Instructions/Exercises/09-external-tools.html), "
     "[10](Instructions/Exercises/10-agent-framework.html)"),

    ("**7. Deployment and DevOps** — a custom app with streaming, managed identity, infrastructure as code, "
     "evaluation gates in a pipeline",
     "[09](Instructions/Exercises/09-external-tools.html), "
     "[13](Instructions/Exercises/13-chat-app.html)"),

    ("**8. Production** — evaluation and release gates, OpenTelemetry and Application Insights, token and "
     "cost telemetry, content safety, red teaming, readiness",
     "[11](Instructions/Exercises/11-measure-quality.html), "
     "[12](Instructions/Exercises/12-observe-and-cost.html), "
     "[14](Instructions/Exercises/14-secure-and-govern.html)"),
]

__all__ = ["LABS", "GROUPS", "MODULE_MAP"]
