# Lab analysis and test report

Independent review of all 24 labs against the client's eight-module requirement, plus an offline test pass
over every lab. Dated 12 September 2026.

Scope reviewed: 117 Python files, 34 READMEs, 25 validators, the Bicep footprint, the GitHub Actions
workflow, the OpenAPI contract and every bundled dataset.

---

## 1. Verdict

**Yes — the lab set can impart the required knowledge.** Every one of the eight client modules has a concrete
teaching destination, and Module 4 (RAG and grounding, named as the highest-value use case) is the strongest
part of the pack by a clear margin.

Three qualifications, in order of importance:

1. **A folder rename has broken the repository's own integrity checking.** `check_workshop.py` no longer runs,
   96 internal links are dead, and the CI workflow references paths that do not exist. None of this affects
   the teaching content, but it means the pack's validation claims are currently unverifiable as shipped.
2. **The content volume exceeds the delivery window.** 31 hours of exercise time against a four-day workshop.
   A route must be selected, not merely acknowledged.
3. **Eight requirement items are guided tenant exercises with no runnable code.** This is defensible — you
   cannot ship code that demonstrates Purview enforcement — but the client should agree the depth explicitly
   rather than discover it in the room.

---

## 2. What was actually tested

Everything below was executed, not inspected. No Azure resources were contacted; no live inference,
indexing, deployment or tenant operation is claimed.

| # | Test | Result |
|---|---|---|
| 1 | All 27 distinct pinned package versions exist on PyPI | **Pass** — all resolve |
| 2 | Five real virtual environments built from the labs' own `requirements.txt` files | **Pass** |
| 3 | `pip check` on the Day 4 environment (the deliberately constrained one) | **Pass** — no broken requirements |
| 4 | All 24 offline validators run in their correct environment | **Pass** — 24/24 exit 0 |
| 5 | Every `import` in all 62 lab source files executed against the real pinned SDKs | **Pass** — all resolve |
| 6 | Foundry / Search / evaluation / Document Intelligence / Content Safety model objects constructed and serialised | **Pass** — 12/12 surfaces |
| 7 | Agent Framework API surfaces used by Exercises 13–16 constructed | **Pass** — 7/7 surfaces |
| 8 | Lab 20 MCP chain end-to-end: real MCP client → real MCP server → real Function handler over HTTP | **Pass** — returned the real ACME-204 record |
| 9 | Lab 22 Bicep compiled with `az bicep build` (Bicep CLI 0.46.1) | **Pass** — zero diagnostics |
| 10 | Repository structural checker (`check_workshop.py`) | **FAIL** — see finding 1 |
| 11 | Internal markdown link integrity | **FAIL** — 96 broken links, see finding 2 |
| 12 | Secret hygiene: stray `.env`, `local.settings.json`, keys, leftover lab state | **Pass** — none present |
| 13 | Dataset integrity: 25 orders with recomputed totals, 5 profiles, 20 eval rows, 20 labelled chunks, 3 PDFs | **Pass** |

### Notable positives

- **Import resolution is clean across all four package worlds.** The Day 4 constraint (`agent-framework-foundry
  1.12` requiring `azure-ai-projects < 2.4`, hence 2.3.0 against Days 1–3's 2.6.0) is correctly handled and the
  resolver is satisfied. This is the highest-risk pin in the pack and it holds.
- **Labs 18, 19, 20 and 21 have genuinely good validators.** Lab 18 executes the real `sync.py` against an
  in-memory fake including a rejected-write path, and asserts the checkpoint did not advance. Lab 21 signs real
  RS256 tokens and proves a token signed with a different key is rejected. Lab 20 tests 401/403/404/200 on the
  real handler and then again over real HTTP. These are the standard the rest of the pack should be held to.
- **The Bicep compiles clean**, and expresses the security posture the labs teach: `disableLocalAuth: true` on
  Search, Cosmos and the Foundry account, scoped role assignments to a managed identity, no public blob access.
- **The honesty discipline throughout is unusually good.** Illustrative outputs are labelled as illustrations,
  offline passes explicitly disclaim live proof, and `readiness.py` refuses to pass a control lacking owner,
  evidence and date. This is the right posture for public-sector delivery and should be preserved.

---

## 3. Defects found

### Finding 1 — P1 — The repository's own structural checker does not run

`check_workshop.py` line 10 globs `Advance labs client-engineering/lab*`. The folder is named
`Advance labs client-engineering`. It therefore finds 16 labs, not 24, and fails immediately:

```
AssertionError: Expected 24 labs
```

**Consequence.** The master check has not run since the rename. `COMPLETION-MATRIX.md` and
`DIRECTORY-TREE.txt` are stale artefacts generated before it, and `VALIDATION.md`'s structural claims cannot
currently be reproduced by the command it tells you to run.

**Verified.** Patching the glob to `*Advance labs client-engineering/lab*` makes all 24 labs pass every structural check —
7/7 required items, correct section ordering, valid Python, no framework leakage into Days 1–3, and all
dataset assertions. The content is sound; only the checker's path is wrong.

**Fix.** One line:

```python
labs = sorted([*root.glob('day*/lab*'), *root.glob('*Advance labs client-engineering/lab*')], key=lambda p: p.name)
```

### Finding 2 — P1 — 96 broken internal links

Same root cause. Affected files:

| File | Broken links |
|---|---|
| `CLIENT-REQUIREMENTS-MATRIX.md` | 64 |
| `CLIENT-COURSE-MAP.md` | 21 |
| `PACKAGE-MATRIX.md` | 8 |
| `VALIDATION.md` | 3 |

All point at `Advance labs client-engineering/...`. Every one resolves if the prefix becomes
`Advance labs client-engineering/` (URL-encode the spaces for web hosting).

### Finding 3 — P1 — The CI workflow references paths that do not exist

`Advance labs client-engineering/lab22-deployment-and-devops/workflow.yml` references seven paths under
`foundry-agent-workshop/Advance labs client-engineering/`:

```
foundry-agent-workshop/Advance labs client-engineering/lab21-agent-web-application/requirements.txt
foundry-agent-workshop/Advance labs client-engineering/lab21-agent-web-application/compileall
foundry-agent-workshop/Advance labs client-engineering/lab23-evaluation-and-operations/requirements.txt
foundry-agent-workshop/Advance labs client-engineering/lab23-evaluation-and-operations/evaluate.py
foundry-agent-workshop/Advance labs client-engineering/lab23-evaluation-and-operations/gate.py
foundry-agent-workshop/Advance labs client-engineering/lab21-agent-web-application          (deploy package)
foundry-agent-workshop/Advance labs client-engineering/lab22-deployment-and-devops/function
```

The workflow would fail at its first step. `CI-CD.md` tells the reader to remove the
`foundry-agent-workshop/` prefix if the workshop is the repository root — but it does not mention the
`Advance labs ` prefix, and the folder name contains a space that would need quoting in a shell step.

**Secondary issue: the validator does not catch this.** `lab22/compileall` asserts only that the deploy steps
come after the gate step, and that the substring `lab23-evaluation-and-operations/evaluate.py` appears in
the gate command. That substring is present inside the broken path, so the check passes. Recommend adding a
path-existence assertion for each referenced file.

### Finding 4 — P2 — Lab 01 and Lab 02 ship identical code

`day1-foundry-sdk-foundations/lab01-foundry-setup/main.py` and
`day1-foundry-sdk-foundations/lab02-model-deployment/main.py` are byte-identical apart from the docstring
URL. Lab 02 is budgeted at 90 minutes with no new code at all.

This is defensible — Lab 02 is deliberately a portal and decision exercise — but it should be a conscious
teaching choice rather than a surprise. The self-paced rewrite (see §5) restructures Lab 02 around the
decision and the quota check so the 90 minutes is spent on the deployment-type justification, which is the
part the client actually asked for.

### Finding 5 — P2 — Environment variable names are inconsistent across labs

| Concept | Names in use | Labs |
|---|---|---|
| Chat deployment | `MODEL_DEPLOYMENT` / `MODEL_DEPLOYMENT_NAME` | 01–08, 18, 23, 24 / 09–16, 20, 21 |
| Search index | `SEARCH_INDEX` / `SEARCH_INDEX_NAME` | 18, 23 / 09, 21 |
| Embedding deployment | `EMBEDDING_DEPLOYMENT` / `EMBEDDING_DEPLOYMENT_NAME` | 07, 17, 18 / 19 |
| Azure OpenAI endpoint | `AZURE_OPENAI_ENDPOINT` / `AZURE_OPENAI_BASE_URL` | 07, 17, 18 / 19, 20 |

Each lab is internally consistent, and the divergence mirrors the SDK sample each lab was based on. But a
self-paced learner who copies one `.env` forward will hit a bare `KeyError`. Either normalise the names, or
state the rule prominently. The self-paced pages take the second approach and warn explicitly at each
transition.

### Finding 6 — P2 — Day 4 validators test nothing behavioural

`compileall` for Labs 13–16 checks only three things: that the source parses, that
`agent_framework_foundry` is importable, and that a `data` folder exists. No API surface, no session
round-trip, no middleware ordering, no workflow construction.

Compare Lab 18, which exercises real sync logic including failure recovery, or Lab 21, which verifies JWT
signature rejection. Day 4 is the pack's most version-fragile area and has its weakest checks.

**Recommended addition** (all verified working against the pinned versions during this review):
`AgentSession.to_dict()/from_dict()` round-trip preserving state; `ContextProvider.before_run` keyword
signature and `SessionContext.extend_instructions`; subclassing of all three middleware bases;
`AgentResponse(messages=[Message('assistant', [str])])` construction; and
`SequentialBuilder(participants=...).build()` / `ConcurrentBuilder(...)`. All are cheap, offline and would
have caught API drift.

### Finding 7 — P3 — Copy-paste leakage in three READMEs

- Lab 23 and Lab 24 clean-up sections both end with *"Optional local model caches are managed through the
  Local SDK rather than deleting unrelated cache folders."* Neither lab has a local model.
- Lab 24's setup section refers to *"OpenAI client `api_key=token` in the embedding example"*. Lab 24 has no
  embedding example; this is Lab 17's text.
- `lab09/compileall` contains dead `if root.name.startswith('lab11')` and `'lab12'` branches — a shared
  validator that was copied rather than specialised.

### Finding 8 — P3 — Bicep uses a storage account key, contradicting the posture it teaches

`resources.bicep` sets `disableLocalAuth: true` on Search, Cosmos and the Foundry account, then configures the
Function app with:

```bicep
{ name: 'AzureWebJobsStorage', value: 'DefaultEndpointsProtocol=https;AccountName=${storage.name};AccountKey=${storage.listKeys().keys[0].value};...' }
```

This works, and a key-based `AzureWebJobsStorage` is common. But it sits awkwardly in a pack whose entire
teaching line is "never use a key". Either switch to the identity-based form
(`AzureWebJobsStorage__accountName` plus a Storage Blob Data Owner assignment) or add a comment explaining the
exception, so a learner does not conclude the rule is optional.

### Finding 9 — Note — Autoscaling is a guided portal exercise, not infrastructure

The requirement names "containerised hosting (Container Apps / App Service) with autoscaling". The Bicep
provisions a fixed `P1v3` plan at `capacity: 1` with no `Microsoft.Insights/autoscalesettings` resource.
Autoscaling and Container Apps are covered in `PUBLISHING.md` as guided configuration exercises (add an
autoscale rule min 1 / max 2, generate load, observe, remove).

This is legitimate and is labelled as such, but it should be confirmed with the client that guided
configuration meets the requirement, rather than infrastructure-as-code.

---

## 4. Coverage against the eight client modules

**Build** = runnable source supplied and verified to import and construct. **Guided** = portal, tenant, licence
or administrator work with no runnable code. **Decision** = a reasoned architecture output.

| # | Client requirement | Depth | Where | Assessment |
|---|---|---|---|---|
| 1 | Component services: Models, Agent Service, Tools/Toolboxes, IQ, Control Plane, Local | Decision + guided | 17 worksheet, 09, 20, 24 | **Adequate.** All seven components appear as rows in Lab 17's architecture worksheet with required evidence. Control Plane is thinnest. |
| 1 | Projects, RBAC, single resource provider, BYO Storage/Search/Cosmos | Build + guided | 01, 17, 19, 22 | **Strong.** Lab 19's `inspect_byo.py` reads real `enterprise_memory` metadata; Lab 22's Bicep shows the account/project model. |
| 1 | AU identity, networking, regions, residency | Decision + guided | 02, 17, 24, `AUSTRALIA-RESIDENCY.md` | **Strong.** The "deployment type, not account region" point is made consistently and repeatedly. |
| 1 | Pricing and consumption | Build + decision | 17, 19, 23 | **Adequate.** `estimate_cost.py` is simple arithmetic over measured tokens; the worksheet adds Search/Cosmos/hosting/telemetry. No PTU or reserved-capacity modelling. |
| 2 | Model families: capability, latency, cost, compliance | Build + decision | 02, 17 | **Strong.** `compare_models.py` measures two real deployments on one task with a deliberate "unknown answer" trap. |
| 2 | Global Standard, PTU, serverless, managed compute | Decision | 17 worksheet | **Covered.** All five options plus Local appear in the worksheet's deployment comparison table, with what must be justified for each. Note this is *not* in `lab02/deployment-options.yaml`, which covers residency only. |
| 2 | OpenAI-compatible Responses inference | Build | 04, 17 | **Strong.** Includes conversations and streaming. |
| 2 | Multimodal | Build | 17 | **Adequate.** One vision call, with a good discussion of when to prefer extraction plus retrieval. |
| 2 | Embeddings: model, dimensions, cost, latency | Build | 17, 18, 19 | **Strong.** 256 vs 1536 measured for ranking, tokens, latency and bytes per vector. |
| 2 | Foundry Local | Optional build + decision | 17 | **Adequate.** Real SDK sample; correctly notes local inference does not make a connected app sovereign. |
| 3 | Agent anatomy, hands-on build | Build | 03, 05, 08, 13, 21 | **Strong.** |
| 3 | Lifecycle: create → version → trace → evaluate → publish → monitor | Build + guided | 03, 11, 12, 16, 22, 23 | **Strong except publish**, which is guided only (tenant/licence dependent). |
| 3 | Portal, SDK, REST, VS Code authoring surfaces | Guided + build | 01, 02, 09, 17 worksheet | **Covered.** Lab 09 uses raw REST with `urllib`; Lab 17's worksheet requires a four-column portal/SDK/REST/VS Code comparison. VS Code is inspection only. |
| 3 | Microsoft Agent Framework v1 | Build | 13–16 | **Strong.** Pinned 1.17.0; all APIs verified. The pack correctly does not promise the exact v1.0.0 binary. |
| 4 | Document ingestion and chunking strategies | Build | 06, 18 | **Strong.** Fixed vs paragraph, measured. |
| 4 | Integrated vectorization: indexer, Text Split, embedding skill | Build | 07 | **Strong.** Complete managed pipeline including index projections. |
| 4 | Index design, hybrid, semantic, reranking | Build | 07, 18 | **Strong.** Four retrieval modes compared on the same corpus. |
| 4 | Document Intelligence / OCR for scanned records | Build | 06, 18 | **Strong.** Lab 18 rasterises a PDF to create a genuine image-only fixture, and normal ingestion fails deliberately. |
| 4 | Incremental re-indexing for freshness | Build | 18 | **Strong.** Manifest checkpoint with atomic replace, tested failure recovery and no-op detection. Best-engineered code in the pack. |
| 4 | Security-trimmed / identity-aware retrieval | Build | 08, 18, 21 | **Strong.** Three escalating layers: synthetic groups → deny-by-default filter → real validated JWT claims. |
| 4 | Retrieval quality: groundedness, recall, precision | Build | 11, 18, 23 | **Strong**, with limits stated explicitly (three documents cap precision@5 at 0.2). |
| 5 | Thread persistence: `enterprise_memory`, containers, RU/s | Guided | 19 | **Strong.** Read-only metadata inspection; honestly surfaces the documented 3,000 RU/s vs 5×1,000 RU/s discrepancy and asks the learner to reconcile it against their actual account. |
| 5 | Storage vs Search vs Cosmos responsibilities | Decision + build | 18, 19, 22 | **Strong.** |
| 5 | Cosmos as vector store; when to choose Search | Build + decision | 19 | **Strong.** |
| 5 | Managed memory vs custom RAG; short vs long-term | Build + decision | 14, 19 | **Strong.** TTL 3600 vs 86400 makes the distinction concrete and testable. |
| 6 | Toolboxes: register once, discover at runtime | **Guided only** | 20 step 9 | **Gap.** No runnable code. Needs a prepared tenant Toolbox and an authenticated MCP connection. |
| 6 | Custom functions; Azure Functions hosting | Build + guided deploy | 05, 20, 22 | **Strong.** Verified end-to-end offline. |
| 6 | MCP servers | Build | 10, 20 | **Strong.** Both client and server sides; the full chain was verified working during this review. |
| 6 | OpenAPI and Logic Apps connectors | Contract + guided | 20 | **Partial.** A real OpenAPI contract is supplied and inspected; Logic Apps is guided only. |
| 6 | Multi-agent workflows and A2A | Build + guided | 16, 20 step 11 | **Workflows strong; A2A guided only.** |
| 7 | Managed agent endpoints | Build + guided deploy | 16, 22 | **Adequate.** Local host runs; azd deployment is a real recipe, unrehearsed. |
| 7 | Teams / M365 Copilot publishing | **Guided only** | 22 `PUBLISHING.md` | **Gap by necessity.** Tenant and licence dependent. Good coverage of rollback and excluded-user testing. |
| 7 | Agents and tools on Functions | Build + decision | 20, 22 | **Strong.** |
| 7 | Container Apps / App Service with autoscaling | Scaffold + guided | 22 | **Partial.** App Service in Bicep; Container Apps and autoscaling are guided configuration. See finding 9. |
| 7 | Custom app: API, chat UI, streaming | Build | 21 | **Strong.** Full JWT validation, identity-derived filters, SSE. |
| 7 | CI/CD | Build scaffold | 22, 23 | **Strong design, broken paths.** See finding 3. |
| 7 | IaC: azd / Bicep full footprint | Build scaffold | 22 | **Strong.** Compiles clean. |
| 7 | Dev → test → prod promotion | Guided + workflow | 22 | **Adequate.** Per-environment OIDC federation and approvals; correctly notes the workflow does not itself prove a SHA passed an earlier environment. |
| 8 | Built-in, agent, RAG and custom evaluators | Build | 11, 23 | **Strong.** Managed evaluators plus a custom judge with structured-output validation. |
| 8 | Production evaluation and CI gates | Build + guided | 22, 23 | **Strong.** The gate checks evidence provenance, freshness, revision match and completeness — not just scores. |
| 8 | OpenTelemetry and Application Insights | Build | 12, 23 | **Strong.** Correct exporter-before-spans ordering and an explicit "flush is not ingestion proof" point. |
| 8 | Token and cost telemetry | Build + decision | 17, 23 | **Strong.** `gen_ai.usage.*` span attributes plus a KQL query giving volume, failures, p95 and tokens per hour. |
| 8 | Entra Agent ID, Conditional Access | **Guided only** | 24 | **Gap by necessity.** Correctly insists on scoped report-only experiments. |
| 8 | Defender, Purview | **Guided only** | 24 | **Gap by necessity.** Licensing dependent. |
| 8 | Content safety and red teaming | Build + guided | 24 | **Adequate.** A real Content Safety call and four synthetic probes, including a retrieved-record injection — the attack path that actually matters given Labs 08/18/21. Honest that an exact-string canary is narrow. |
| 8 | Production checklist and cost management | Build + guided | 23, 24 | **Strong.** `readiness.py` fails by default and refuses controls lacking owner, evidence and date. |

### Summary of the eight guided-only items

Toolboxes · Logic Apps connectors · A2A · Teams/M365 publishing · Entra Agent ID · Conditional Access ·
Defender · Purview.

All eight are tenant-, licence- or administrator-dependent, and all are labelled as guided in
`CLIENT-REQUIREMENTS-MATRIX.md`. That is the right call — shipping simulated Purview enforcement would be
worse than shipping nothing. **Recommendation:** confirm this depth with the client in writing before
delivery, and pre-provision whichever of the eight they most want demonstrated.

---

## 5. Self-paced conversion

The exercises have been converted to Microsoft Learn-style self-paced HTML in [`self-paced/`](self-paced/).
Open [`self-paced/index.html`](self-paced/index.html).

**Why a rewrite rather than a Markdown-to-HTML conversion.** The Day 1–4 READMEs use a rigid 13-section
template in which the guided walkthrough is typically three numbered steps, two of which are generic filler
("Open `main.py` and identify authentication…", "Change one input and explain the difference to another
participant"). They are written for an instructor to expand in the room. The advanced labs 17–24 are the
opposite — detailed, bespoke and genuinely self-paced; Lab 18's README in particular is the model.

Converting the thin READMEs verbatim would have produced pages a learner could not complete unaided. Each
exercise was therefore rewritten to the standard the advanced labs already set: what to look for in the code
before running it, what the expected output means, what to change to prove the mechanism, and what the result
does *not* prove.

**What the pages add:**

- Expected output stated for every command, so a learner knows whether they succeeded.
- Deliberate-break experiments — remove the `conversation` argument and watch recall vanish; invert
  `else 'false'` to `else ''` and watch the deny-by-default filter become a total leak; change the API audience
  and meet the 401 you will otherwise meet at the worst moment.
- The environment-variable divergence from finding 5 called out at each transition.
- Cross-references made explicit, so the escalating story is visible: 05 → 20 for tool execution boundaries,
  08 → 18 → 21 for retrieval security, 14 → 19 for memory, 11 → 23 for evaluation.
- Knowledge checks as collapsible `<details>` elements with the reasoning, not just the letter.
- Clean-up written as an instruction with its safety rails explained.

**Verification of the generated site:**

| Check | Result |
|---|---|
| 24 exercise pages plus index generated | Pass |
| HTML tag balance across all 25 pages | Pass — 0 problems |
| 153 relative links resolve | Pass |
| Every lab folder referenced exists | Pass — 24/24 |
| Every `python …` command referenced points at a real script | Pass |

**Regenerating.** Content lives as structured Python in `self-paced/content/`; `python build.py` re-renders all
25 pages. Editing the content modules rather than the HTML keeps the pages consistent.

---

## 6. Recommended actions

**Before any delivery**

1. Fix the `check_workshop.py` glob and re-run it; regenerate `COMPLETION-MATRIX.md` and `DIRECTORY-TREE.txt`
   (finding 1).
2. Repair the 96 broken markdown links (finding 2).
3. Repair the seven workflow paths and add a path-existence assertion to `lab22/compileall` (finding 3).
4. Agree the guided-only depth with the client in writing, and pre-provision whichever integrations they most
   want demonstrated.
5. **Rehearse every live path in the target tenant.** Nothing in this report — or in the repository's own
   validation — substitutes for that. The offline evidence is strong on code correctness and package
   compatibility, and silent on regional availability, quota, RBAC propagation, network reachability and model
   output quality.

**Before the next revision**

6. Strengthen the Day 4 validators (finding 6) — the specific checks are listed and were verified working.
7. Normalise environment variable names, or document the rule prominently (finding 5).
8. Remove the copy-pasted paragraphs from the Lab 23 and Lab 24 READMEs and the dead branches in
   `lab09/compileall` (finding 7).
9. Decide on the `AzureWebJobsStorage` key versus managed identity question and comment the choice
   (finding 8).
10. Confirm whether guided autoscaling meets the requirement, or add
    `Microsoft.Insights/autoscalesettings` to the Bicep (finding 9).

**Scheduling**

11. 31 hours of exercises will not fit four days. Use `CLIENT-COURSE-MAP.md` to select a route. Given the
    client named RAG as their highest-value use case, the defensible core is
    **01 → 03 → 05 → 06 → 07 → 08 → 18 → 21 → 23 → 24**, with 17 as pre-reading, 19 and 22 as demonstrations,
    and Day 4 (13–16) offered as an optional track for teams that will actually adopt the framework.

---

## 7. What this report does not establish

No live Azure execution was performed. Specifically unproven: model inference, agent creation, document
analysis, Search indexing, Foundry IQ retrieval, remote MCP execution, managed evaluator runs, Application
Insights ingestion, `azd` provisioning, GitHub Actions execution, channel publishing, and every tenant
governance integration.

Package pins resolving and SDK objects constructing do not prove regional availability, quota, RBAC, network
access or output quality. A passing offline validator means exactly what its own PASS line says it means —
the repository is consistently careful about this, and this report is too.
