# Lab 17 — Platform, model choices and embeddings (120 minutes; split into short exercises)

## Status badges (GA/Preview/Prerelease)

Embedding APIs / Responses: GA for the selected supported model. Foundry Local and multimodal support: verify model, package, hardware and current availability individually.

## Learning objectives

- Map the platform and BYO data stores.
- Compare two model deployments on an identical task.
- Inspect embedding dimensions, similarity, latency and storage.
- Run a vision input and optional on-device model.

## Prerequisites (roles, resources, quota)

Python3.11+, Azure CLI login, the service endpoints named in `.env.example`, supported model quota and least-privilege data-plane access. Use an independent instructor-supplied environment. Cloud setup and tenant integrations are separate from offline validation. For optional Foundry Local install the separately pinned SDK and verify native runtime/hardware support.

## Australian/residency note

Verify Australia East separately for project, model, tool, evaluator and telemetry. Model deployment type determines processing geography; account location is insufficient. Only synthetic data is bundled. Cross-region models/judges require explicit organisational approval. Tenant governance demonstrations may export interaction data: review their data destinations.

## Setup steps

From this lab directory:

```powershell
py -3.11 -m venv .venv
.venv/Scripts/Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
az login
python validate.py
```

Populate `.env` with endpoints and actual deployment names. No service keys are used. OpenAI client `api_key=token` in the embedding example is an Entra token callback, not a stored API key.

## Guided walkthrough with numbered steps and code explanation

1. Complete `data/architecture-and-model-decisions.md`: draw the actual resource IDs and identity boundaries, not just product boxes. Inspect model catalogue cards and deployment options without creating every expensive alternative.
2. Run `python src/compare_models.py`. Record correctness (opening time is supported; bin pickup is unknown), latency and token usage for two actual deployments. Repeat three times; a single latency reading is not a benchmark.
3. Run `python src/embeddings.py` against a `text-embedding-3-small` deployment. Compare 256 versus 1536 dimensions, cosine ranking, token count and raw vector bytes. The index and query vectors must use the same model and dimensions. These samples do not prove that fewer dimensions always preserve retrieval quality.
4. Use `python src/estimate_cost.py --input-per-million 1 --output-per-million 2 --requests 1000` to practise cost arithmetic with illustrative rates. Replace both rates with the selected model's current approved pricing, in one currency. The same supplied rates apply to every row; calculate different models separately. Add Search, Cosmos, hosting, tools and telemetry in the worksheet.
5. Run `python src/multimodal.py`. Check the two leave numbers against `data/policy-page.png`; discuss why generative image reading differs from deterministic extraction plus retrieval.
6. Optional hardware exercise: install `foundry-local-sdk-winml==1.2.4` on supported Windows, or `foundry-local-sdk==2.0.1` cross-platform, in a separate environment. Run `python src/local_model.py` with an available alias. First use downloads runtime/model assets; disconnect only after caching to test local inference. No Azure subscription or credential is used by this script. Local inference does not automatically make a whole connected application sovereign.
7. Complete the cost/compliance choice in the worksheet and retain measured evidence. Do not provision PTU or managed compute merely to demonstrate a catalogue selection.

## Run & expected output

```powershell
python src/compare_models.py
python src/embeddings.py
python src/multimodal.py
```

Two model result rows, two embedding dimensions with real similarity rankings, an image answer, and optional local streamed text. No cloud execution is claimed until you run these.

## Validation

`python validate.py` checks local source and the named deterministic mechanics. It prints PASS/FAIL and exits nonzero on failure. Follow the walkthrough for live evidence; offline validation does not contact Azure or certify production controls.

## Troubleshooting

| Symptom | Action |
|---|---|
| KeyError for configuration | Populate this lab's .env; check actual deployment names. |
| 401 or unavailable credential | Sign in to the intended Entra tenant. |
| 403 | Verify service role, scope, propagation and private-network path. |
| 404 model/index | Copy the deployed name and endpoint from the supplied environment. |
| 429 | Lower classroom concurrency and check per-deployment quota. |
| Unsupported feature/package | Use the documented compatible environment and record the limitation; do not mark an unrun step passed. |

## Cleanup

Run `python cleanup.py` for this lab's generated local reports. It prompts and is safe to repeat. Shared services are instructor-owned. Reverse any scoped tenant changes you created using the recorded resource names; no blanket subscription or tenant deletion. Optional local model caches are managed through the Local SDK rather than deleting unrelated cache folders.

## Knowledge check (3 MCQs with answer key)

1. What must match between ingestion and query vectors?

   A. Model and dimensions B. Only filename C. Only region

   Answer: A.

2. What does a single latency result prove?

   A. One observed request time B. A universal model ranking C. A production SLA

   Answer: A.

3. Does local model inference imply all app data stays on-device?

   A. No; tools and telemetry may be remote B. Always C. Only for PDFs

   Answer: A.

## Stretch challenge

Change one variable, predict the result, run the experiment and attach observed evidence to your decision. Explain which conclusion the evidence does not support.

## References

- [Primary Microsoft Learn](https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview)
- [Official sample repository](https://github.com/microsoft-foundry/foundry-samples/tree/main/samples/python/foundry-local/native-chat-completions)
