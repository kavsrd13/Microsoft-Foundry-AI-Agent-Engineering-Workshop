# Validation — 11 September 2026

Offline checks passed. No Cosmos account, container or document was created or queried.

- `python validate.py`: Python syntax, vector/index policy agreement and fixture IDs. Executed the real save/read/cleanup scripts against an in-memory service fake. Verified 3600/86400 TTL values, a missing second-user session, separate saved partitions and cleanup that leaves the first user's five items intact.
- Installed and imported **azure-cosmos 4.17.0**, **azure-identity 1.25.3**, **openai 2.54.0** and **python-dotenv 1.2.3** in an isolated authoring directory. These direct dependency versions are pinned in the participant requirements.
- Executed the real vector script with a fake embedding response and recording container: three 256-dimensional records, authenticated partition on every upsert, parameterized vector query scoped to that partition. This is not a vector-ranking service test.
- Executed the SDK-acquired-token partition extraction with synthetic claims; tenant and object ID both contribute to the key. This does not validate incoming web tokens.
- Rechecked Microsoft Learn Cosmos vector quickstart and Foundry standard-setup documentation. The README preserves the current documentation's inconsistent throughput/container guidance as a rehearsal question rather than promising a universal RU/s setting.

Live rehearsal must still prove resource/role provisioning, Cosmos persistence across processes, TTL expiration, real vector rankings, request charges and service-owned BYO container metadata. No service-owned state is modified by the inspection script. Partitioning is not row-level authorisation.
