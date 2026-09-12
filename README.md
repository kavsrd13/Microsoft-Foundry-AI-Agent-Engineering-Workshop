# Microsoft Foundry AI Agent Engineering Workshop

**Fourteen hands-on exercises.** Connect to Foundry, build an agent that uses tools, turn a pile of PDFs
into a grounded assistant that cites its sources and shows each person only what they may see, give it
memory, measure whether it is any good, and decide whether it is safe to ship.

Everything uses synthetic data belonging to a fictional council, Acme Public Sector Pty Ltd.

## Start here

**→ [Open the exercises](https://kavsrd13.github.io/Microsoft-Foundry-AI-Agent-Engineering-Workshop/)**

Or open [`self-paced/index.html`](self-paced/index.html) locally — the pages are static and need no server.

Each exercise page contains **all the code you need**. You create a file, add to it a few lines at a time,
and run it after each step. Every task also ends with a collapsible *complete file so far*, so if you lose
track you can paste the whole thing and carry on.

## The exercises

| # | Exercise | Time | What you build |
|---|---|---|---|
| 01 | [Get started with Foundry](labs/01-get-started) | 90 min | Connect, list models, ask, converse, stream |
| 02 | [Choose a model](labs/02-choose-a-model) | 75 min | Compare two models, embeddings, cost, vision |
| 03 | [Build your first agent](labs/03-first-agent) | 90 min | Versioned agent, tools, the tool loop |
| 04 | [Prepare documents](labs/04-prepare-documents) | 75 min | Extract PDFs, compare chunking strategies |
| 05 | [Build a vector index](labs/05-vector-index) | 90 min | Embed, index, four kinds of search |
| 06 | [Ground an agent](labs/06-ground-an-agent) | 90 min | Cited answers, permission filtering, the leak |
| 07 | [Keep the index fresh](labs/07-keep-the-index-fresh) | 75 min | Add / change / delete, OCR |
| 08 | [Give the agent memory](labs/08-agent-memory) | 90 min | Cosmos, TTL, what a partition key is not |
| 09 | [Connect external tools](labs/09-external-tools) | 90 min | An HTTP tool with permissions, MCP |
| 10 | [The Agent Framework](labs/10-agent-framework) | 90 min | Sessions, middleware, multi-agent workflows |
| 11 | [Measure quality](labs/11-measure-quality) | 90 min | Retrieval metrics, a judge, a release gate |
| 12 | [Observe and cost](labs/12-observe-and-cost) | 75 min | Tracing, token telemetry, failures |
| 13 | [Build a chat app](labs/13-chat-app) | 120 min | Real sign-in, verified claims, streaming UI |
| 14 | [Secure and govern](labs/14-secure-and-govern) | 75 min | Content safety, injection probes, readiness |

About 20 hours of exercises. For a four-day delivery, run three or four a day.

## Before you begin

1. Install **Python 3.11**, **Git** and the **Azure CLI**.
2. Sign in and pick your subscription:

   ```powershell
   az login --tenant YOUR-TENANT-ID
   az account set --subscription YOUR-SUBSCRIPTION-ID
   ```

3. **Make a separate virtual environment for every exercise.** They pin different versions of the same
   packages deliberately — Exercise 10 in particular needs an older `azure-ai-projects` than the rest.
   One shared environment will break them.

Each exercise folder holds its own `requirements.txt`, `.env.example`, `data/`, and a `solution/` folder
with the finished working code to check yourself against.

> **Note**: These exercises run against Azure resources your instructor or administrator supplies. Running
> them uses quota and costs money. Every dataset here is synthetic — never substitute real citizen, staff
> or customer records.

## For instructors

- [LAB-ANALYSIS.md](LAB-ANALYSIS.md) — the review and offline test report behind this material, including
  what was verified and what still needs a tenant rehearsal.
- [SETUP.md](SETUP.md) — resources to provision and roles to assign.
- [AUSTRALIA-RESIDENCY.md](AUSTRALIA-RESIDENCY.md) — data residency notes. An Australia East project
  location does not by itself establish where a request is processed; the model's deployment type does.

Prerequisites to have ready: a Foundry project with two chat deployments and a vision-capable one; an Azure
OpenAI resource with `text-embedding-3-small`; an Azure AI Search service with the semantic ranker enabled;
Document Intelligence; Cosmos DB for NoSQL; Application Insights; Content Safety; and two test user
accounts for Exercise 13.

## How the material is built

The code shown on each exercise page is **sliced out of the solution files**, not retyped, so the page and
the working code cannot drift apart. To regenerate the pages after editing content:

```powershell
cd self-paced
python build.py
```

See [self-paced/README.md](self-paced/README.md) for the content format.

## Earlier version

The `day1-…` through `day4-…` folders and `Advance labs client-engineering/` hold the previous 24-lab
version of this workshop, kept for reference. The material above supersedes it: those labs were more
numerous, more terse, and asked learners to run supplied scripts rather than write the code themselves.
Their supporting documents — [CLIENT-REQUIREMENTS-MATRIX.md](CLIENT-REQUIREMENTS-MATRIX.md),
[PACKAGE-MATRIX.md](PACKAGE-MATRIX.md), [VALIDATION.md](VALIDATION.md) and others — describe that earlier
structure and still contain links that were broken by a folder rename. See LAB-ANALYSIS.md, finding 2.
