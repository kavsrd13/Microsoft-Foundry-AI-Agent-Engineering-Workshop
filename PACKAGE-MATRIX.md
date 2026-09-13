# Package matrix and compatibility decisions

Versions are pinned in each lab's requirements. The provided brief is a starting specification, not proof of compatibility. On 10 September2026 PyPI metadata confirmed the requested main packages exist; local SDK surface and resolver checks are described in VALIDATION.md.

| Package | Version / decision | Status | Labs |
|---|---|---|---|
| azure-ai-projects | 2.6.0 | GA package | 01–12 |
| azure-ai-projects | 2.3.0; provider requires >=2.2,<2.4 | GA package; explicit brief correction | 13–16 |
| azure-identity | 1.25.3 base; see isolated Day4 requirements | GA | All |
| python-dotenv | 1.2.3 base | Tooling | All |
| pymupdf | 1.28.2 | Tooling | Shared generator / extraction validation |
| azure-ai-documentintelligence | 1.0.2 / API2024-11-30 | GA | 06 |
| azure-search-documents | 12.0.0 | GA core; preview features separately labelled | 07–09 |
| azure-storage-blob | 12.30.1 | GA | 07 |
| azure-ai-evaluation | 1.18.5 | Stable package; safety feature experimental where noted | 11 |
| azure-monitor-opentelemetry | 1.8.9 | GA | 12 |
| azure-core-tracing-opentelemetry | 1.0.0b13 | Prerelease package (brief corrected) | 12 |
| agent-framework | 1.17.0 | GA package | 13–16 |
| agent-framework-foundry | 1.12.0 | GA package | 13–16 |
| agent-framework-foundry-hosting | 1.0.0b260903 | Prerelease, exact pin | 16B |

Python3.11 is the participant baseline for ordinary labs. Local authoring checks used Python3.12 unless otherwise recorded. Hosted deployment uses a separate Python3.13 environment. `requirements.txt` in the specific lab is authoritative for all additional packages and exact pins; do not use a single aggregate environment.

Source metadata: [projects2.6.0](https://pypi.org/project/azure-ai-projects/2.6.0/), [Foundry provider1.12.0](https://pypi.org/project/agent-framework-foundry/1.12.0/), [hosting adapter](https://pypi.org/project/agent-framework-foundry-hosting/1.0.0b260903/). Package status is not service/feature status.

## Client extension environments

The following per-lab files are authoritative; install each independently. Lab21 deliberately uses Search11.x while Labs18/23 use Search12.x. Optional Foundry Local uses a separate native-runtime environment. A version range is not a resolved lock.

| Lab | Requirements |
|---|---|
| 17 | [requirements.txt](Advance labs client-engineering/lab17-models-embeddings-and-architecture/requirements.txt) |
| 18 | [requirements.txt](Advance labs client-engineering/lab18-end-to-end-rag/requirements.txt) |
| 19 | [requirements.txt](Advance labs client-engineering/lab19-cosmos-state-and-vectors/requirements.txt) |
| 20 | [requirements.txt](Advance labs client-engineering/lab20-hosted-tools-and-integrations/requirements.txt) |
| 21 | [requirements.txt](Advance labs client-engineering/lab21-agent-web-application/requirements.txt) |
| 22 | [requirements.txt](Advance labs client-engineering/lab22-deployment-and-devops/requirements.txt) |
| 23 | [requirements.txt](Advance labs client-engineering/lab23-evaluation-and-operations/requirements.txt) |
| 24 | [requirements.txt](Advance labs client-engineering/lab24-enterprise-security-and-governance/requirements.txt) |
