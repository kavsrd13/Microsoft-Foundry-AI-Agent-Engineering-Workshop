# Validation and delivery boundaries

## Completed locally

- All24 lab folders have their seven required items. The original16 and six new labs use13 ordered sections; Labs18–19 use checked guided-part layouts.
- Python sources parse; Days1–3 contain no Agent Framework imports.
- All24 per-lab offline validators pass using the appropriate local environment (rechecked11 September2026). Console PASS/FAIL text also works with Windows non-UTF-8 redirected output.
- The shared dataset contains 25 unique orders with recomputed totals, 5 profiles, 3 synthetic PDFs, 20 permission-labelled chunks and 20 source-backed evaluation rows. Independent copies are bundled with the labs.
- The PDF generator ran successfully. Policy pages were rendered for visual inspection and text was checked against the evaluation corpus.
- Day2 imports and real Search SDK model construction/serialisation passed with Search12.0.0 and Document Intelligence1.0.2. The service clients were substituted for these checks; no indexing service execution is claimed.
- Day4 imports passed using projects2.3.0, framework-core1.17.0, Foundry provider1.12.0 and orchestration1.1.1. Local checks exercised session serialisation, preference injection, middleware denial and email redaction, workflow graph construction and ResponsesHostServer construction.
- The complete Lab16 requirements resolved with the requested umbrella framework package. The hosting adapter also requires the explicitly pinned prerelease `azure-ai-agentserver-responses==2.2.0b1`.
- Pinned evaluation1.18.5 constructor/call signatures were checked against its published wheel.

See [COMPLETION-MATRIX.md](COMPLETION-MATRIX.md) and [DIRECTORY-TREE.txt](DIRECTORY-TREE.txt). Run `python check_workshop.py` from the repository root to repeat the structural/link checks. Run each lab's `compileall` in its own installed environment for its documented offline checks.

## Not executed against Azure

No successful live model inference, agent creation, document analysis, Search indexing, IQ retrieval, MCP tool execution, managed evaluator run, Application Insights ingestion or hosted deployment was performed during authoring. The host construction check triggered the SDK's metadata discovery probe, which failed locally; that is not Azure tenant validation. The local HTTP host was constructed but no end-to-end HTTP/inference request was rehearsed.

Local checks used Python3.12 on Windows. The Python3.11 participant baseline and Python3.13 hosted runtime need instructor rehearsal. `azd` was absent from the authoring machine. Hosted YAML follows the official sample, but provisioning, its substituted model values, extension compatibility and permissions have not been tenant-tested.

The instructor must run each live walkthrough with the configured services before delivery. A syntax pass or a model-construction test does not prove regional availability, quotas, RBAC, network access or model output quality.

## Deliberate teaching simplifications and corrections

- User-requested simplicity takes priority over boilerplate in the source brief. Ordinary errors surface directly; README troubleshooting replaces repeated exception wrappers. Validation and cleanup contain the few checks needed for their purpose.
- Prerequisite services are supplied independently. Lab02 provisioning and Lab09 knowledge-source creation/cleanup are guided portal exercises, not claimed automated Python provisioning.
- Day4 uses projects2.3.0 because provider1.12.0 explicitly excludes projects2.6.0. Each track/lab has an isolated environment.
- Core tracing package1.0.0b13 and hosted response adapter dependencies are prerelease even when their services are GA.
- IQ planning/synthesis and native ACL features are labelled separately from the GA paths. Lab08 intentionally keeps the native-ACL preview design disabled rather than shipping speculative API calls.
- IQ/MCP fallback output is labelled illustrative, not fabricated “recorded” service output. There are no unresolved `# VERIFY:` code blocks; documented tenant checks remain necessary.
- Optional Invoice_1.pdf downloads the official maintained invoice.pdf under that local alias because the original requested binary is absent upstream.

## Client expansion verification — 11 September 2026

- Labs17–24: local validators passed. Their exact scope is described in each validator/README; many checks are structural or deterministic, not SDK integration tests.
- Lab18: extraction/chunk strategies, freshness edits/deletion, image-only scan fixture and Search query construction exercised. Mocked sync checks cover failure/checkpoint/replay/no-op. See [RAG validation](Advance labs client-engineering/lab18-end-to-end-rag/VALIDATION.md).
- Lab19: Cosmos SDK query surface and mocked current-identity partition save/read/vector/cleanup checked. See [Cosmos validation](Advance labs client-engineering/lab19-cosmos-state-and-vectors/VALIDATION.md). There is no live cross-process persistence or RU measurement claimed.
- Lab20: actual Function handler tested for missing principal, wrong/missing role, success and missing record; local HTTP client → test host → actual handler passed. Local MCP discovery was exercised during authoring. This does not validate Azure Functions Core Tools, deployed Easy Auth or an Entra-issued token.
- Lab21: locally signed JWT and mocked request tests cover token failures, identity filters and SSE. The new seed script constructs/serialises actual Search11.x index models and writes distinct user ACLs through mocked clients. No real sign-in or live Search/inference completed.
- Lab22: Bicep0.47.16 compiled `infra/main.bicep` without diagnostics. Per-lab checks and the app tests passed. No azd deployment, GitHub Actions execution, environment promotion or channel publishing occurred. See [deployment evidence](Advance labs client-engineering/lab22-deployment-and-devops/validation-evidence.md).
- Lab23: gate checks reject invalid/stale/revision-mismatched evidence and non-finite metrics. These are fabricated test inputs for gate logic only; no passing release report is bundled. Live evaluator, telemetry SDK imports/ingestion and model output need rehearsal in the pinned lab environment.
- Lab24: readiness template, synthetic probe inputs and Python syntax checked. Content Safety execution, native/managed red teaming, policy enforcement, Defender/Purview and Entra Agent ID are not live-validated.
- Lab17: local cosine/dimension/example inputs and syntax checked. Model/embedding/multimodal calls and optional Foundry Local native SDK must be rehearsed. No price, performance or residency conclusions are claimed from local tests.

The final packaging check parses all Python sources, validates local Markdown links and datasets, checks ZIP CRC integrity and compares every packaged file byte-for-byte with the source folder. Generated caches and environments are excluded; no `.env` or `local.settings.json` is shipped.

The [client requirements matrix](CLIENT-REQUIREMENTS-MATRIX.md) records remaining tenant dependencies and integration boundaries. No claim of complete production implementation follows from topic coverage.
