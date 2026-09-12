# Lab 22 — Deploy, evaluate and promote the resident assistant

**Participant build: 120 minutes; channel and container extensions: 45 minutes. Modules 1, 3, 6, 7, 8.** Deploy Lab21's application and a separate Functions tool. Use the same reviewed commit for dev, test and prod.

## Status badges (GA/Preview/Prerelease)

App Service, Functions, Bicep and GitHub OIDC are established services. Foundry project/model and publishing capabilities depend on the selected region, model and current API. This is a public-endpoint teaching footprint, not a production network baseline. Bicep compiles locally; deployment has not been rehearsed in a tenant.

## Learning objectives

Identify infrastructure versus application deployment; separate user authentication from managed service identity; apply an evaluation gate; promote environment-specific configuration; distinguish web hosting from publishing a Foundry agent to Teams/M365.

## Prerequisites (roles, resources, quota)

Complete Lab21. Install Azure CLI, azd, Bicep, Python 3.11 and Functions Core Tools v4. Use a workshop subscription with permission to create a resource group, resources and scoped role assignments. Check P1v3, Search Basic, Cosmos serverless and selected model/version/SKU availability and quota. Create separate Entra API/SPA registrations per environment. Infrastructure creation incurs charges. Tenant registrations, Search indexing, BYO Agent Service connections and production private networking are not created by this template.

## Australian/residency note

Choose an approved Australian region and compatible **regional** model deployment if required. Global Standard can process outside that region. Region selection alone is not a residency assurance; document processing scope, logs, backups and dependencies. Do not change to a Global SKU merely to bypass a regional quota issue.

## Setup steps

From this lab directory, review `src/infra/resources.bicep`, then:

```powershell
az login
azd auth login
azd env new resident-dev
azd env set AZURE_SUBSCRIPTION_ID YOUR-SUBSCRIPTION-ID
azd env set AZURE_LOCATION australiaeast
azd env set ENTRA_API_CLIENT_ID YOUR-API-ID
azd env set ENTRA_SPA_CLIENT_ID YOUR-SPA-ID
azd env set MODEL_NAME YOUR-AVAILABLE-MODEL
azd env set MODEL_VERSION YOUR-AVAILABLE-VERSION
azd env set MODEL_SKU Standard
az bicep build --file src/infra/main.bicep
azd provision
azd deploy
```

`azure.yaml` explicitly sets `infra.path: src/infra`; its web service points to Lab21. Review provision's change summary before accepting. The template creates Blob Storage, Search, application-owned Cosmos memory, Foundry/project/chat deployment, Application Insights/Logs, an App Service plan, web app and Function app. It does **not** attach Cosmos as Foundry's `enterprise_memory`. The web app currently reads Search and calls the model; Cosmos and the Function are separate teaching components until explicitly integrated.

## Guided walkthrough with numbered steps and code explanation

1. Find the web managed identity's scoped Search Data Reader and Cognitive Services OpenAI User assignments. The browser signs in separately through Lab21's Entra registrations.
2. Configure the deployed HTTPS origin as the SPA redirect URI. Seed the new `resident-records` Search index with Lab21's documented ACL fields using the ingestion lab, mapping fields explicitly. Give only the ingestion identity write permissions. An empty provisioned Search service cannot answer questions.
3. Open the app; prove different authorised source IDs for two users. Keep token values out of evidence. This live access test is required in addition to mocked tests.
4. Call the deployed `/api/collection` Function using its function key in the `x-functions-key` header from a server-side client. A request without the key must fail. This sample tool returns synthetic data; follow Lab20 for Entra-authenticated production tool hosting. Never place a Function key in browser code or source control.
5. Follow [CI and environment promotion](src/CI-CD.md). The workflow runs Lab21 offline tests and the **reference RAG** evaluator from Lab23 before deployment. A passing evaluator does not certify the deployed app, ACLs or network.
6. Follow [publishing and hosting alternatives](src/PUBLISHING.md). Record the version, endpoint/channel, access result and rollback target separately.

## Run & expected output

`azd env get-values` shows resource names/endpoints; do not publish the full environment output. The web app should require sign-in before `/chat`. An unauthenticated chat returns 401; an authorised request streams source IDs and answer deltas. The Functions route returns a synthetic collection day with a valid key. Provisioning alone does not populate Search or configure channel distribution.

## Validation

Run `python -m pip install -r requirements.txt`, then `python validate.py`; compile Bicep separately. Run Lab21 `validate.py` in its own environment. Live evidence: deployment resource IDs, successful authenticated stream, two-user ACL test, keyless Function rejection, CI gate rejection of a failed report, test deployment commit and approved promotion. Never substitute a hand-edited report for a live evaluation. CI and Azure deployment remain tenant-rehearsal requirements.

## Troubleshooting

Model/SKU unavailable: choose another approved compatible deployment, not an arbitrary region. Search 404: create and populate the index. Search/model 403: inspect the web identity's exact data-plane role and allow RBAC propagation. Sign-in failure: check v2 audience, tenant, delegated permission and exact redirect origin. Workflow cannot deploy: check the federated subject includes the selected GitHub environment and that environment variables name existing apps.

## Cleanup

Stop local processes. For an isolated workshop environment run `azd down` from this lab after confirming its environment/resource group; it removes billable resources and data. Do not target a shared resource group. Remove workshop-only Entra registrations, federated credentials and GitHub environments separately. `cleanup.py` is informational and does not delete Azure resources.

## Knowledge check (3 MCQs with answer key)

1. What does provision create? A: Infrastructure B: User conversations C: Teams approval. **A**.
2. Does the reference RAG gate prove deployed user ACLs? A: Yes B: No C: Only in prod. **B**.
3. Where does a Function key belong? A: Browser B: Git C: Approved server-side secret store. **C**.

## Stretch challenge

Move the tool to Entra authentication using Lab20. Containerise Lab21 and compare App Service capacity with Container Apps HTTP scaling. Add a real post-deployment authenticated smoke test using a tenant-approved test identity; preserve user-level ACL tests rather than switching the API to accept app-only tokens.

## References

- [azd GitHub Actions pipelines](https://learn.microsoft.com/azure/developer/azure-developer-cli/pipeline-github-actions)
- [App Service Python configuration](https://learn.microsoft.com/azure/app-service/configure-language-python)
- [Functions security](https://learn.microsoft.com/azure/azure-functions/security-concepts)
- [Foundry publishing](https://learn.microsoft.com/azure/foundry/agents/how-to/publish-copilot)
- [Container Apps scaling](https://learn.microsoft.com/azure/container-apps/scale-app)
