# Instructor guide

Teach from the learner script, not the validation helper. Ask participants to identify the input, the service call and the result before introducing the next concept. Keep advanced production error-handling patterns as discussion, outside the core demo.

## Run sheet

| Day | Sequence | Mode | Lab time |
|---|---|---|---|
| 1 | 01 access → 02 deployment → 03 agent versions → 04 Responses | Hands-on; 02 portal exercise | 225 min |
| 2 | 05 tools → 06 extraction → 07 vectorisation → 08 security filter | Hands-on; pre-stage Search managed identity/RBAC | 225 min |
| 3 | 09 IQ → 10 MCP → 11 evaluation → 12 tracing | 09/10 demo-led; 11/12 hands-on when region/roles permit | 225 min |
| 4 | 13 framework comparison → 14 session/context → 15 middleware → 16 workflows/hosting | Hands-on; hosted part instructor-led if rights missing | 225 min |

For a 45-minute lab allow 5 minutes explanation, 10 minutes guided demo, 20 minutes participant exercise, 5 minutes validation and 5 minutes knowledge check/cleanup. Double practice and discussion time for 90-minute labs. Breaks and extra practice are additional to these lab timings.

## Pre-delivery checklist

- Three days before delivery, re-test pinned prerelease packages and the hosted adapter on Python 3.13. Preserve a known-working environment; do not upgrade during class.
- Rehearse every live path in the target tenant, including quota under expected classroom concurrency, tool calls, Search indexer execution, evaluator region and traces arriving in Application Insights.
- Verify the Day 4 package exception: projects2.3.0 for the pinned provider, separate from Days1–3 projects2.6.0.
- Inspect the three bundled PDFs and confirm 25 orders, 5 users and 20 evaluation rows. Verify every answer against the corpus.
- Allocate individual lab suffixes and explain cleanup ownership. Shared Azure services are prerequisites; lab scripts delete only their owned child resources.
- Record model name/version/type, processing geography, evaluator regions, RBAC, private endpoint connectivity and organisational approval.
- IQ/MCP fallback files are illustrative teaching fixtures, not claimed recordings. Capture your own successful output if you need a demonstrated tenant fallback.
- Rehearse denied/unfiltered access only against synthetic data. Ensure the omitted-filter exercise cannot be copied into a production route.
- Confirm Python, Azure CLI, Docker and azd on instructor machines. azd was not present on the authoring machine; cloud hosting has not been run there.

## Classroom interventions

| Failure | Teaching response |
|---|---|
| 401 or wrong tenant | Check az account show and login tenant; avoid rewriting working code. |
| 403 after role assignment | Check role scope, propagation and private network access. |
| 404 model | Compare actual deployment name with .env; catalogue model name can differ. |
| 429 under concurrency | Stagger groups or use approved quota; follow Retry-After. |
| Search index empty | Inspect indexer execution errors and identity permissions before querying. |
| Evaluator not available | Use approved supported judge region or instructor results, labelled as such. |
| Hosted rights absent | Run local workflows/host and demonstrate deployment from instructor account. |
| Package conflict | Recreate the affected lab's isolated environment from its requirements. |

## Demonstration questions

Day 1: Where does the definition live? Day 2: Who executes the function, and where is authorisation enforced? Day 3: What evidence supports this answer or score? Day 4: Which responsibilities moved into the framework, and which remain with Foundry?

Do not call the pack tenant-validated until all live checks have been rehearsed. Use VALIDATION.md to distinguish evidence types.

## Client expansion

Use [CLIENT-COURSE-MAP.md](CLIENT-COURSE-MAP.md) for the eight-module route, time budget and rehearsal prerequisites. Use [CLIENT-REQUIREMENTS-MATRIX.md](CLIENT-REQUIREMENTS-MATRIX.md) to distinguish executable exercises, deployment scaffolds, guided tenant exercises and architecture decisions.
