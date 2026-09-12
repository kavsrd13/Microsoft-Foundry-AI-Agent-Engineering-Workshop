# Workshop setup

Prepare each lab independently. The instructor supplies Azure prerequisites; this repository does not silently provision a subscription-wide environment.

1. Install Python 3.11 for ordinary labs, Git and Azure CLI. Lab 16 hosted deployment uses Python 3.13, Docker and Azure Developer CLI (`azd`); see its README for its isolated environment.
2. Sign in with `az login --tenant YOUR-TENANT-ID`. Select the approved subscription with `az account set --subscription YOUR-SUBSCRIPTION-ID`. Confirm `az account show --query "{tenant:tenantId,subscription:id}"`.
3. Provision or assign an Australia East Foundry account and project through the Azure portal. Select the standard setup only when the course needs customer-owned Storage, Search and Cosmos DB. Review [standard setup](https://learn.microsoft.com/azure/foundry/agents/concepts/standard-agent-setup).
4. Verify a Responses-compatible chat model and `text-embedding-3-small` individually for region, version, quota and approved deployment type. Do not assume the project location fixes processing geography.
5. Assign the participant only the permissions needed below. Wait for role propagation; use project scope for project operations and resource scope for data services. Provisioning rights are separate from runtime access.
6. Create Document Intelligence (Layout API 2024-11-30), an AI Search service with semantic ranking enabled, Storage for indexer input, and Application Insights for tracing as needed. Enable Search managed identity and its downstream RBAC before Lab 07.
7. From a selected lab folder run the commands below. Copy service endpoints/resource IDs into that lab's `.env`. Each README names the exact variable names; they may differ between SDK examples. Never enter an API key.

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python validate.py
```

Use separate virtual environments for labs, especially evaluation and Day 4. Do not install all requirement files into one environment. The pinned Day 4 Foundry provider is incompatible with projects 2.6.0.

## Access map

| Actor / task | Scope and permission to verify |
|---|---|
| Participant project inference / prompt assets | Foundry User or documented equivalent at the supplied project |
| Model deployment | Model deployment write permission on the Foundry account; project role alone is insufficient |
| Search schema/indexer author | Search Service Contributor on the Search service |
| Search document uploader | Search Index Data Contributor on the Search service |
| Search query caller | Search Index Data Reader on the Search service |
| Blob uploader | Storage Blob Data Contributor on the supplied storage account/container |
| Search managed identity reading blobs | Storage Blob Data Reader on its input container |
| Search managed identity embedding/vectoriser | Cognitive Services OpenAI User on the embedding resource |
| Document Intelligence caller | Cognitive Services User on the DI resource |
| Trace ingestion identity | Monitoring Metrics Publisher on Application Insights; enable Entra ingestion |
| Hosted deployment | Foundry Project Manager plus required provisioning/registry permissions; use instructor demo if absent |

Verify current role definitions and organisation policy rather than assigning broad Owner rights. See [Foundry RBAC](https://learn.microsoft.com/azure/foundry/concepts/rbac-azure-ai-foundry) and lab-specific prerequisites.

## Assets and smoke test

Pre-generated assets are included. To rebuild from the repository root in a tooling environment:

```powershell
python -m pip install pymupdf==1.28.2
python shared/generate_assets.py
python check_workshop.py
```

Then open Lab 01 in its own folder, populate `.env`, and run `python validate.py --live`. Offline syntax and asset checks do not prove Entra access, model availability, indexing, evaluator availability or hosted deployment. Run each live walkthrough in the actual training tenant before delivery.

Optional Microsoft samples: `python shared/download_ms_samples.py`. Review upstream licence terms first. Invoice_1.pdf is a local alias for the maintained upstream Data/invoice/invoice.pdf because the requested original binary is absent. Synthetic PDFs remain the default.

## Client labs17–24

Follow the [client course route](CLIENT-COURSE-MAP.md) and each lab's own requirements and `.env.example`. Use isolated environments. Lab22 reuses Lab21 application source. Lab21 includes a dedicated GUID-based index seed; Lab23 requires the original Lab08 corpus/permission schema. Lab18's small retrieval experiment uses a separate index and cannot supply a release-gate report. Tenant identities, role assignments, governance services and channel licences require instructor preparation.
