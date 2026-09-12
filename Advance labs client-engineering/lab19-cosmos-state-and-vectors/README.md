# Lab 19 — Where state and vectors live (120 minutes)

Build real Cosmos NoSQL persistence with small scripts. Live Azure execution requires prepared resources; offline validation does not prove tenant access. Use synthetic records only. This lab adds client Modules 2 and 5; it complements Lab 14's framework session serialisation.

## Outcomes and architecture

| Store | Holds | Owner |
|---|---|---|
| Blob Storage | Original files and extraction inputs | Ingestion application |
| Azure AI Search | Chunks, searchable fields, embeddings and access metadata | Retrieval application |
| Cosmos `enterprise_memory` | Service-managed agent state in standard BYO setup | Foundry runtime |
| Cosmos `workshop-memory` | This exercise's conversation, preferences and vectors | Your application |

Short-term messages expire after one hour; the preference survives for a day. Neither is automatically injected into an agent: after `read.py`, pass the recovered messages/preference to the agent as in Lab 14. The database does not decide what the model remembers.

## Prepare once (instructor)

Use an existing Cosmos DB for NoSQL account with vector search enabled in an approved region. Use a dedicated workshop database. Resource control-plane permissions create databases/containers; **Cosmos DB Built-in Data Contributor** permits document operations. Azure subscription Contributor alone is not data access. Assign the learner data role at `/dbs/workshop-memory`; only the instructor needs metadata read access to service-owned BYO resources. Grant the embedding caller Cognitive Services OpenAI User on the model resource. Confirm firewalls/private endpoint routing from the classroom. Do not place real records in these examples.

Run from this lab directory after setting the existing account/resource group:

```powershell
$rg = 'YOUR-RESOURCE-GROUP'
$account = 'YOUR-COSMOS-ACCOUNT'
az cosmosdb sql database create -g $rg -a $account -n workshop-memory
az cosmosdb sql container create -g $rg -a $account -d workshop-memory -n sessions --partition-key-path /userId --ttl -1
az cosmosdb sql container create -g $rg -a $account -d workshop-memory -n vectors --partition-key-path /userId --vector-embeddings '@data/vector-policy.json' --idx '@data/index-policy.json'
```

These commands provision billable resources when a learner executes them. Instructor chooses serverless or provisioned throughput for the existing account; do not assume the example sets a budget. `--ttl -1` enables item-specific TTL with no default expiry. The scripts supply TTL on sessions/preferences. `flat` vectors use 256 dimensions, within the 505-dimension flat-index limit; these are real shortened text-embedding-3-small embeddings. For large collections compare quantizedFlat/DiskANN after loading representative data, not three records. [Cosmos vector search](https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/vector-search), [TTL](https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/time-to-live)

## Participant steps

1. Create an isolated Python 3.11+ virtual environment, install `requirements.txt`, copy `.env.example` to `.env`, fill endpoints/deployment and run `az login`. Keep `.env` untracked.
2. Read `src/store.py`: the identity partition comes from a token acquired directly by Azure Identity. It is not taken from a user-supplied field. Token payload decoding here is **not validation of incoming tokens**. A web application must authenticate requests in middleware first and use its validated principal.
3. Run the two commands below separately, closing Python between them. A second process recovers ACME-204 and the preference.

```powershell
python src/save.py
python src/read.py
python src/vectors.py
python validate.py
```

4. Inspect both session items in Data Explorer, including `_ts` and `ttl`. Point reads require `id` and partition key. Capture request charge from Data Explorer Query Stats; compare a point read with a query. Set the session TTL to 30 seconds in `save.py`, save again, wait at least 30 seconds, then read. The session should become unavailable while the preference remains; restore 3600 afterwards. No catch block hides the expected not-found response.
5. Sign into a different learner identity with its own allowed access and run `read.py` before saving: no session should exist in that identity's partition. Then save its synthetic session. **Partition keys improve routing; they are not row-level RBAC.** The trusted application enforces per-user access; a principal with database-wide contributor access can query other partitions. Production end users must never receive that database role or direct database credentials.
6. Run `vectors.py`; the bin record should rank first for the recycling question. Compare with Search lab results. Both documents and query must use the same embedding model and dimensions. Changing the vector policy requires a new compatible container/re-index, not just an environment variable change.

## Guided BYO inspection (instructor, 15 minutes)

Point `COSMOS_ENDPOINT` to the approved BYO account temporarily and run `python src/inspect_byo.py`. Capture container names, partition paths and TTL metadata only; restore the lab endpoint afterwards. Standard setup uses `enterprise_memory`. Classic runtime containers include `thread-message-store`, `system-thread-message-store` and `agent-entity-store`; newer runtime state uses `agent-definitions-v1` and `run-state-v1`. Actual provisioned containers depend on runtime/setup; do not create, edit, delete or impose TTL on service-owned containers.

**Throughput is a deployment prerequisite, not a universal memory constant.** The current standard-setup documentation states a 3000 RU/s account limit and also describes five containers at 1000 RU/s each; its troubleshooting still references three containers. Reconcile the selected runtime's template/container count, account limit and actual offers before provisioning. Do not present 3000 RU/s as sufficient for every topology. Serverless consumption and provisioned RU/s are different billing modes. Record the verified setting in rehearsal evidence. [Standard setup and storage requirements](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/standard-agent-setup)

## Decision exercise and evidence

Choose Cosmos vectors when operational JSON and vector similarity should live together with your application data. Choose Azure AI Search for this course's document ingestion, skillsets, hybrid/semantic retrieval and search-specific features. Managed memory is runtime-owned; custom RAG is application-owned retrieval. Neither automatically provides cross-session preferences or grants access to documents. Record these decisions, save/read outputs, TTL result, vector ranking and request charge in `data/evidence.md` (create locally). [Vector Python reference](https://learn.microsoft.com/en-us/azure/cosmos-db/quickstart-vector-store-python)

## Cleanup and checks

Run `python cleanup.py` only after both save and vector steps; it removes the fixed synthetic items in the current identity partition. A missing item raises visibly (including after TTL expiry); remove remaining IDs in Data Explorer if needed. Instructor reviews then removes the dedicated `workshop-memory` database if no other participant uses it. Never delete `enterprise_memory` for this exercise.

1. Why is `/userId` not itself authorisation? **Answer:** the application must constrain access using authenticated identity.
2. Why do original files and vectors use different stores? **Answer:** their ingestion, retrieval and persistence responsibilities differ.
3. Does Cosmos persistence imply model memory? **Answer:** no; the application must select and supply the saved context.
