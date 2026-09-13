# Lab 21 — Build an authenticated streaming agent application

**Participant build · 90 minutes · Modules 3, 4, 7, 8.** Build the browser → API → authorised Search → Responses path. The app implements a small grounded assistant using Responses instructions; it does not register/publish a persistent Foundry agent version. Use the earlier agent-version lab for that lifecycle.

## Status badges (GA/Preview/Prerelease)

Uses Entra JWT validation, Azure AI Search and the Foundry Responses API. Model/region capabilities vary. This is a minimal teaching application, not a complete resident-facing product.

## Learning objectives
The browser receives an Entra access token. The API verifies its signature, issuer, tenant, audience, expiration and delegated scope before constructing a Search filter from verified object/group IDs. The API's managed identity accesses Azure; the user token is not forwarded as a service credential. The response streams as server-sent events (SSE). No conversation is stored: wire lab19 memory in a follow-up only after preserving tenant/user partitioning.

## Prerequisites (roles, resources, quota)
1. Complete an ACL index exercise. This app expects `id`, `content`, `is_public` (filterable Boolean), `allowed_user_ids` and `allowed_group_ids` (filterable string collections). Use real Entra GUIDs for ACL values. If using another lab's index, map its field names explicitly in `permission_filter` and `retrieve`; do not silently drop the filter.
2. Have a Foundry project/chat deployment and Search index. Grant the developer identity or deployed app managed identity the appropriate Foundry inference access and **Search Index Data Reader** on Search.
3. Register a **single-tenant API** in Entra. Expose `api://API-CLIENT-ID/access_as_user`; set the access token version to 2 (`api.requestedAccessTokenVersion`). Configure group claims to include groups assigned to the application. Assign two test users/groups with different record access. Group overage is deliberately denied; a production extension must resolve membership through Microsoft Graph with approved permissions, rather than trusting a browser-supplied list.
4. Register a separate **single-page application**. Add delegated API permission `access_as_user`; obtain tenant consent as required. Configure SPA redirect URI `http://localhost:8000` (and the exact HTTPS hosting origin when deployed). Neither registration needs a client secret for this browser PKCE flow.
## Australian/residency note

Use synthetic records and approved regional deployments. Confirm model processing geography, identity logs and service storage locations separately; an Australian web server alone does not establish data residency.

## Setup steps

From this lab folder:

```powershell
python -m pip install -r requirements.txt
# Use the shared foundry-agent-workshop/.env file
# Edit public IDs/endpoints in .env. Never put model keys in the HTML.
az login
# Instructor: set two test-user object IDs and a new lab21- index in .env.
python seed_index.py
python -m uvicorn src.app:app --host 127.0.0.1 --port 8000
```

The seed step needs **Search Service Contributor** and **Search Index Data Contributor** on the dedicated Search service. The running app needs only data-reader access. It creates a fresh index and refuses to overwrite an existing one. Skip seeding if the instructor already prepared it. It supplies a public opening-time record plus private inspection records for A (Monday) and B (Thursday). Ask about both cases as each user; only the permitted private case should appear. For group access, put a real test group GUID into `allowed_group_ids` on a synthetic record and repeat with a verified member/nonmember.

Open http://localhost:8000, sign in, then ask about an indexed record. Only public app IDs are returned by `/config`; these are identifiers, not secrets. The sample uses an explicitly pinned MSAL browser CDN script. For managed/offline delivery, package a reviewed MSAL build locally and establish CSP/script integrity according to organisational policy.

## Guided walkthrough with numbered steps and code explanation
1. Read `current_user`, then change the API audience locally and observe rejection. Restore it.
2. Read `permission_filter`; locate the user GUID and group GUIDs in a verified token using a local debugger without saving tokens/screenshots.
3. Sign in as test user A. Ask a question whose answer appears only in user B's record. The source list must omit that record and the answer must report insufficient evidence.
4. Sign out of the browser account and repeat as B in a separate browser session. Record accessible source IDs, not token contents.
5. Open Network → `/chat`: observe the sources event, individual deltas and final completion event. Answer text uses `textContent`, avoiding execution of model-generated markup.
6. Restart the server: there is no application conversation history to recover. Explain how per-user Cosmos persistence differs from the model's stored Responses option, disabled here with `store=False`.

## Run & expected output

After sign-in, ask about an indexed record. Expect a source-ID list followed by streamed answer text. `/chat` rejects a missing token with 401. When no authorised evidence exists the assistant should say it lacks evidence. The browser marks a stream without the completion event as incomplete.

## Validation
Run `python -m compileall .`. This is an **offline mocked smoke test**, not proof of real Entra, Search or Foundry execution. Live evidence: two actual user access outcomes, a rejected missing/wrong-audience/expired token, and one completed stream. A failed stream requires retry; this teaching app omits reconnect, quotas and durable chat history. It never accepts `X-MS-CLIENT-PRINCIPAL` or arbitrary user IDs as authentication.

## Troubleshooting

For 401 check tenant, audience, v2 token and delegated scope. For group-overage 403 configure application-assigned group claims; never bypass the check. Search 404 means the index is absent or misnamed. Search/model 403 requires the service identity's data-plane role. Sign in again when an access token expires; automatic token renewal is omitted from this teaching UI.

## Cleanup
Lab22 hosts this application. Keep HTTPS, validated access tokens and managed service identities. Add per-user rate limits, timeouts, approved logging, deployment testing and accessibility review before real residents use it. `remove generated local files manually` creates/deletes nothing; stop the server with Ctrl+C. In Search, delete only the dedicated `lab21-` index you created after confirming its name. Remove only workshop-owned Entra registrations after recording their IDs.

## Knowledge check (3 MCQs with answer key)

1. What controls record access? A: Browser text B: Validated user identity C: Model choice. **B**.
2. Where do filter group IDs come from? A: Chat body B: UI setting C: Validated Entra claims. **C**.
3. Does streaming persist memory? A: No B: Always C: Only on HTTPS. **A**.

## Stretch challenge

Connect Lab19 memory using a tenant/user partition derived from verified identity. Add automatic token renewal with MSAL and approved request tracing using Lab23; log metadata rather than record bodies or tokens.

## References
- [Protected web API token validation](https://learn.microsoft.com/en-us/entra/identity-platform/scenario-protected-web-api-app-configuration)
- [Group claims and overage](https://learn.microsoft.com/en-us/security/zero-trust/develop/configure-tokens-group-claims-app-roles)
- [Search security filters](https://learn.microsoft.com/en-us/azure/search/search-security-trimming-for-azure-search)
- [Responses streaming](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/responses)
- [MSAL browser SPA](https://learn.microsoft.com/en-us/entra/msal/javascript/browser/initialization)

- [Search index creation](https://learn.microsoft.com/azure/search/search-how-to-create-search-index)
