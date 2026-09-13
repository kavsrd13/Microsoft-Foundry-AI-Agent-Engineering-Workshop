# Client course route

Use one synthetic public-service scenario and short, inspectable scripts. Preserve the original 16-lab route; the eight client additions deepen the mechanics. All eight client modules are addressed, with tenant-heavy topics taught as guided exercises rather than claimed turnkey implementations.

| Module | Teaching route | Visible outcome |
|---|---|---|
| 1. Foundations and architecture | [Lab 01](day1-foundry-sdk-foundations/lab01-foundry-setup/README.md) → [Lab 17](Advance labs client-engineering/lab17-models-embeddings-and-architecture/README.md) → [Lab 22](Advance labs client-engineering/lab22-deployment-and-devops/README.md) → [Lab 24](Advance labs client-engineering/lab24-enterprise-security-and-governance/README.md) | Resource/data-flow map and identity/residency decisions |
| 2. Models and embeddings | [Lab 02](day1-foundry-sdk-foundations/lab02-model-deployment/README.md) → [Lab 04](day1-foundry-sdk-foundations/lab04-responses-api/README.md) → [Lab 17](Advance labs client-engineering/lab17-models-embeddings-and-architecture/README.md) | Model comparison and measured embedding trade-offs |
| 3. Build an agent | [Lab 03](day1-foundry-sdk-foundations/lab03-prompt-agent/README.md) → [Lab 05](day2-foundry-sdk-tools-and-rag/lab05-function-tools/README.md) → [Lab 13](day4-agent-framework/lab13-maf-transition/README.md) → [Lab 11](day3-foundry-sdk-enterprise/lab11-evaluation/README.md) → [Lab 12](day3-foundry-sdk-enterprise/lab12-tracing-and-governance/README.md) | Participant creates and runs an agent, then inspects evaluation/trace lifecycle |
| 4. RAG engineering | [Lab 06](day2-foundry-sdk-tools-and-rag/lab06-document-intelligence/README.md) → [Lab 07](day2-foundry-sdk-tools-and-rag/lab07-search-integrated-vectorization/README.md) → [Lab 08](day2-foundry-sdk-tools-and-rag/lab08-secure-rag/README.md) → [Lab 18](Advance labs client-engineering/lab18-end-to-end-rag/README.md) → [Lab 21](Advance labs client-engineering/lab21-agent-web-application/README.md) | Ingestion to cited answer, freshness experiment and authorised-user retrieval |
| 5. State and memory | [Lab 14](day4-agent-framework/lab14-session-and-context/README.md) → [Lab 19](Advance labs client-engineering/lab19-cosmos-state-and-vectors/README.md) | Persistent cross-process state, TTL and vector-store comparison |
| 6. Tools and orchestration | [Lab 10](day3-foundry-sdk-enterprise/lab10-mcp-tools/README.md) → [Lab 20](Advance labs client-engineering/lab20-hosted-tools-and-integrations/README.md) → [Lab 16](day4-agent-framework/lab16-orchestration-and-hosted/README.md) | Callable Function, MCP discovery and workflow |
| 7. Deployment and DevOps | [Lab 21](Advance labs client-engineering/lab21-agent-web-application/README.md) → [Lab 22](Advance labs client-engineering/lab22-deployment-and-devops/README.md) | Authenticated streaming app, Bicep and reviewable pipeline |
| 8. Production | [Lab 11](day3-foundry-sdk-enterprise/lab11-evaluation/README.md) → [Lab 12](day3-foundry-sdk-enterprise/lab12-tracing-and-governance/README.md) → [Lab 23](Advance labs client-engineering/lab23-evaluation-and-operations/README.md) → [Lab 24](Advance labs client-engineering/lab24-enterprise-security-and-governance/README.md) | Quality gate, telemetry queries and control evidence |

## New labs and time budget

| Lab | Core exercise time |
|---|---|
| [Lab 17](Advance labs client-engineering/lab17-models-embeddings-and-architecture/README.md) | 120 min |
| [Lab 18](Advance labs client-engineering/lab18-end-to-end-rag/README.md) | 150 min |
| [Lab 19](Advance labs client-engineering/lab19-cosmos-state-and-vectors/README.md) | 120 min |
| [Lab 20](Advance labs client-engineering/lab20-hosted-tools-and-integrations/README.md) | 120 min |
| [Lab 21](Advance labs client-engineering/lab21-agent-web-application/README.md) | 90 min |
| [Lab 22](Advance labs client-engineering/lab22-deployment-and-devops/README.md) | 120 min |
| [Lab 23](Advance labs client-engineering/lab23-evaluation-and-operations/README.md) | 120 min |
| [Lab 24](Advance labs client-engineering/lab24-enterprise-security-and-governance/README.md) | 120 min |

The additions total **16 hours** of core exercise time. The original route totals **15 hours**: teaching everything gives **31 hours of exercises**, before explanations, breaks, provisioning and optional extensions (Lab20 adds60 minutes; Lab22 adds45). This is not a realistic all-inclusive four-day timetable. Reuse introductory builds, pre-provision instructor resources and select optional tenant integrations to fit an agreed schedule. Do not count a guided discussion as a completed deployment.

## Instructor preparation

1. Read [SETUP](SETUP.md), [package compatibility](PACKAGE-MATRIX.md) and [validation](VALIDATION.md). Use a separate virtual environment for each lab; do not merge dependencies.
2. Rehearse regional quota/model availability and the target tenant. Prepare isolated workshop resources and two real test-user identities. Review feature status in each lab and its official references.
3. Prepare each lab independently. Lab21 includes `seed_index.py`; Lab23 needs the Lab08 corpus/schema. Labs18,19 and21 are not drop-in data schemas for one another.
4. Teach a script, run it, change one input and inspect the effect. Ask learners to retain the named evidence, not merely a PASS message.
5. Review and rehearse deployment identities, consent, channel licensing and governance controls before scheduling the guided extensions. Never test tenant-wide policy changes in a live classroom.

## Recommended demonstrations

Show embedding dimension versus payload size (17); add/update/delete a source (18); close Python then recover state (19); missing-role versus authorised tool call (20); two users see different source IDs (21); make a quality gate fail (23). Each demonstrates a single mechanism with the same code participants inspect.

Use the [requirement-by-requirement matrix](CLIENT-REQUIREMENTS-MATRIX.md) to agree the depth of coverage. The [enterprise exercises](Advance labs client-engineering/lab24-enterprise-security-and-governance/enterprise-exercises.md) are reviewable guided tasks; no real tenant controls are asserted as configured.
