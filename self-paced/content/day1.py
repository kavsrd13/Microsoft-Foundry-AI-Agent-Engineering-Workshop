"""Exercises 01-04 — Foundry foundations (Day 1)."""

SETUP_PS = """py -3.11 -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
az login"""

TROUBLE = ["Error or symptom", "What to do"], [
    ["`KeyError: 'PROJECT_ENDPOINT'`",
     "You did not copy `.env.example` to `.env`, or you are not running from the lab folder."],
    ["`CredentialUnavailableError` or HTTP 401",
     "Run `az login` against the intended tenant. Check that the project endpoint belongs to that tenant."],
    ["HTTP 403 Forbidden",
     "Your identity lacks the project or account role, the assignment has not propagated yet, or the resource is behind a private network. Do not widen the scope blindly."],
    ["HTTP 404 on a deployment",
     "You used the catalogue *model* name instead of your *deployment* name. Copy the deployment name from the portal."],
    ["HTTP 429 throttling",
     "Reduce concurrency or request more quota, and honour the service's `Retry-After` value."],
    ["Empty deployment list",
     "The project has no deployed model. Complete Exercise 02 or ask your instructor to deploy one."],
]


LAB01 = {
    "num": "01",
    "slug": "01-foundry-setup",
    "short": "Connect to a Foundry project",
    "group": "Day 1 — Foundry foundations",
    "track": "Foundry SDK",
    "module_tags": ["Module 1", "Module 3"],
    "title": "Connect to a Microsoft Foundry project and inspect its deployments",
    "minutes": 45,
    "lab_path": "day1-foundry-sdk-foundations/lab01-foundry-setup",
    "env_note": "`azure-ai-projects==2.6.0` in its own virtual environment",
    "blurb": "Authenticate with Entra ID, open a project client and list the models actually deployed in it.",
    "intro": [
        "In this exercise you connect to a Microsoft Foundry project from Python using your own Entra ID "
        "identity, and list the model deployments the project can actually reach.",
        "The exercise looks small, and that is the point. Almost every later exercise begins with these same "
        "three lines, and almost every classroom failure is an authentication or naming problem rather than a "
        "code problem. You will also learn to tell the difference between a value you *configured* and a fact "
        "you *verified* — a distinction that matters a great deal when someone later asks you where data is "
        "processed.",
    ],
    "objectives": [
        "Authenticate a project client with `DefaultAzureCredential` instead of a key.",
        "List the model deployments available in a project.",
        "Distinguish a configured location label from verified resource metadata.",
        "Recognise the common 401 / 403 / 404 / 429 failures and what each one means.",
    ],
    "prereqs": [
        "An active Azure subscription, and an Azure CLI signed in to the correct tenant.",
        "**Python 3.11** installed and on your path.",
        "A Microsoft Foundry project supplied by your instructor, with **at least one chat model deployed** "
        "and available quota.",
        "A least-privilege project role that permits model inference (for example *Foundry User*). "
        "Deploying a model, which you do in Exercise 02, needs a separate account-scoped permission.",
    ],
    "before_extra": [
        {"note": "Every exercise in this workshop is independent. You never need the output of a previous "
                 "exercise, and you should create a fresh virtual environment for each one."},
    ],
    "sections": [
        {
            "h2": "Set up the exercise environment",
            "steps": [
                ["Open a PowerShell terminal in the lab folder:",
                 {"code": "cd day1-foundry-sdk-foundations/lab01-foundry-setup", "lang": "powershell"}],
                ["Create and activate a virtual environment, install the pinned packages, and create your "
                 "environment file:",
                 {"code": SETUP_PS, "lang": "powershell"},
                 {"tip": "If `Activate.ps1` is blocked, run "
                         "`Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` in that terminal first."}],
                ["Open `.env` and replace each placeholder with your own values:",
                 {"code": """PROJECT_ENDPOINT=https://YOUR-RESOURCE.services.ai.azure.com/api/projects/YOUR-PROJECT
MODEL_DEPLOYMENT=YOUR-CHAT-DEPLOYMENT
AZURE_TENANT_ID=YOUR-TENANT-ID
AZURE_LOCATION=australiaeast""", "lang": "text"},
                 {"bullets": [
                     "`PROJECT_ENDPOINT` — copy it from the project home page in the Foundry portal. It ends "
                     "in `/api/projects/<project-name>`.",
                     "`MODEL_DEPLOYMENT` — the *deployment* name, which is often different from the catalogue "
                     "model name.",
                     "`AZURE_TENANT_ID` — must match the tenant you signed in to.",
                     "`AZURE_LOCATION` — a label only. You verify the real value in the next step.",
                 ]},
                 {"warn": "Never put an API key in `.env` for this workshop. Every exercise uses Entra ID."}],
                ["Confirm the tenant you are actually signed in to, and the region the account really lives in:",
                 {"code": """az account show --query tenantId -o tsv
az cognitiveservices account show --name YOUR-ACCOUNT --resource-group YOUR-RG --query location -o tsv""",
                  "lang": "powershell"},
                 "Compare both against what you typed into `.env`. If the tenant differs, your token will be "
                 "issued for the wrong directory and you will see a 401 later."],
                ["Run the offline check. It parses the source without contacting Azure:",
                 {"code": "python validate.py", "lang": "powershell"},
                 {"ok": "You should see `PASS: OFFLINE source syntax; no Azure call made`."}],
            ],
        },
        {
            "h2": "Read the code before you run it",
            "intro": ["Open `src/main.py`. It is deliberately about twenty lines. Find each of these three ideas "
                      "before running anything."],
            "steps": [
                ["**Authentication.** `DefaultAzureCredential()` looks for a usable identity in order — "
                 "environment variables, a managed identity, the Azure CLI, and so on. On your laptop it finds "
                 "your `az login` session; in Exercise 22 the same line finds the web app's managed identity. "
                 "The code does not change between those two worlds."],
                ["**Project access.** `AIProjectClient(endpoint=..., credential=...)` is the entry point to "
                 "everything project-scoped: deployments, agents, and an OpenAI-compatible client.",
                 {"code": """project = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)""", "lang": "python"}],
                ["**The single concept being taught.** `project.deployments.list()` is a *read*. It provisions "
                 "nothing and costs nothing. The final `assert` turns an empty list into a clear message rather "
                 "than a confusing failure three exercises later.",
                 {"code": """deployments = list(project.deployments.list())
for deployment in deployments:
    print(deployment.as_dict())
assert deployments, "Deploy a supported chat model in this project first." """, "lang": "python"}],
            ],
        },
        {
            "h2": "Run the script and interpret the output",
            "steps": [
                ["From the lab folder, run:",
                 {"code": "python src/main.py", "lang": "powershell"}],
                ["You should see the project endpoint, your configured tenant and location labels, and one "
                 "dictionary per deployment. A typical deployment entry includes its name, the model it serves, "
                 "and its deployment type.",
                 {"note": "The two lines labelled *configured* are echoing your `.env` file back at you. They "
                          "are not evidence. The deployment list is evidence, because it came from the service."}],
                ["Open the Foundry portal and compare the deployment names on screen with the names printed by "
                 "the script. They must match exactly, including case. This is the single most common cause of "
                 "the 404 you will otherwise meet in Exercise 03."],
                ["Now break it deliberately, so you recognise the failure later. Change `MODEL_DEPLOYMENT` in "
                 "`.env` to `not-a-real-deployment` and re-run. Nothing fails — because this script never uses "
                 "that variable. Restore the correct value.",
                 {"tip": "A configuration value is only validated when something actually consumes it. "
                         "Exercise 03 is the first exercise that will reject a wrong deployment name."}],
                ["Confirm live access with the same validator, this time in live mode:",
                 {"code": "python validate.py --live", "lang": "powershell"},
                 {"ok": "`PASS: LIVE deployment access` means your identity reached the project and it returned "
                        "at least one deployment. That is a real end-to-end check of authentication, network "
                        "path and RBAC."}],
            ],
        },
        {
            "h2": "Separate what you configured from what you verified",
            "intro": [
                "Public-sector reviewers will ask where a request is processed. The honest answer never comes "
                "from a string in a configuration file.",
            ],
            "steps": [
                ["Write down three facts and, next to each, the command or screen that proves it: the "
                 "subscription and resource group, the account's region, and the deployment *type* of the model "
                 "you will use."],
                ["Note which one you cannot yet prove from this exercise. The deployment type — Global "
                 "Standard, Data Zone or Regional — is what actually governs processing geography, and it is "
                 "visible in the portal's deployment details. Exercise 02 makes that choice explicitly.",
                 {"warn": "An Australia East project does **not** by itself mean Australian processing. "
                          "The model's deployment type and the model's own terms decide that."}],
            ],
            "outro": [
                {"table": TROUBLE},
            ],
        },
    ],
    "knowledge_check": [
        {"q": "What authenticates the project client in this exercise?",
         "options": ["A. Entra ID, through `DefaultAzureCredential`", "B. An API key embedded in the source",
                     "C. The `AZURE_LOCATION` value"],
         "answer": "A",
         "why": "`DefaultAzureCredential` resolves your `az login` session locally and a managed identity when "
                "hosted, so the same code works in both places without a stored secret."},
        {"q": "What does `project.deployments.list()` do?",
         "options": ["A. Creates a model deployment", "B. Reads the deployments that already exist",
                     "C. Reserves quota"],
         "answer": "B",
         "why": "It is a read-only call. It provisions nothing, which is why this exercise has no cloud clean-up."},
        {"q": "Which of these is evidence that a deployment is reachable?",
         "options": ["A. `AZURE_LOCATION=australiaeast` in `.env`", "B. A passing offline syntax check",
                     "C. A successful live list that returns the deployment"],
         "answer": "C",
         "why": "A configured string and a local syntax pass prove nothing about the service. Only a successful "
                "call proves authentication, network path and RBAC together."},
    ],
    "summary": [
        "You connected to a Foundry project with your own Entra identity, listed its real deployments, and "
        "practised separating configured labels from verified facts.",
        "Those three lines — credential, project client, project call — open every remaining exercise. When a "
        "later exercise fails with 401, 403 or 404, come back to this one and re-run "
        "`python validate.py --live` to isolate whether the problem is access or code.",
    ],
    "cleanup": [
        "This exercise is read-only and creates nothing in Azure, so there is nothing to delete.",
        {"code": "python cleanup.py", "lang": "powershell"},
        "The script confirms that no cloud resources were created. Your virtual environment and `.env` stay on "
        "your machine; delete the `.venv` folder if you want the disk space back, and never commit `.env`.",
    ],
    "refs": [
        ("Foundry SDK overview", "https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview"),
        ("Foundry RBAC", "https://learn.microsoft.com/azure/foundry/concepts/rbac-azure-ai-foundry"),
        ("Standard agent setup", "https://learn.microsoft.com/azure/foundry/agents/concepts/standard-agent-setup"),
    ],
}


LAB02 = {
    "num": "02",
    "slug": "02-model-deployment",
    "short": "Deploy a model and choose its type",
    "group": "Day 1 — Foundry foundations",
    "track": "Foundry SDK",
    "module_tags": ["Module 1", "Module 2"],
    "title": "Deploy a model and choose a deployment type for a residency requirement",
    "minutes": 90,
    "lab_path": "day1-foundry-sdk-foundations/lab02-model-deployment",
    "env_note": "`azure-ai-projects==2.6.0`; the same environment shape as Exercise 01",
    "blurb": "Check quota, deploy a model from the portal, and justify the deployment type against an approved "
             "processing geography.",
    "intro": [
        "In this exercise you deploy a model yourself and, more importantly, justify *which kind* of deployment "
        "you chose. Deployment management is done through the portal on purpose: the Python here stays focused "
        "on project access rather than ARM plumbing, and the decision you are practising is an architectural "
        "one, not a coding one.",
        "The question this exercise answers is the one an Australian public-sector reviewer will actually ask: "
        "*where is this request processed, and what proves it?*",
    ],
    "objectives": [
        "Check real model, version, region and quota availability before promising a capability.",
        "Deploy a uniquely named model through the Foundry portal.",
        "Choose between Regional, Data Zone and Global deployment types against a stated requirement.",
        "Record the evidence that establishes processing geography.",
    ],
    "prereqs": [
        "Exercise 01 completed, or at least a working `.env` and a successful `az login`.",
        "**Account-scoped permission to create a model deployment.** A project-only role is not enough. "
        "If you do not have it, follow the exercise in inspection-only mode — every step except the deploy "
        "itself still works.",
        "Available quota in the region you intend to use.",
    ],
    "sections": [
        {
            "h2": "Set up and inspect what already exists",
            "steps": [
                ["Create this exercise's own environment:",
                 {"code": "cd day1-foundry-sdk-foundations/lab02-model-deployment\n" + SETUP_PS,
                  "lang": "powershell"}],
                ["Fill in `.env` exactly as you did for Exercise 01, then list the deployments that exist today:",
                 {"code": "python src/main.py", "lang": "powershell"},
                 "Keep this output. At the end of the exercise you will run the same command again and expect "
                 "exactly one new entry."],
            ],
        },
        {
            "h2": "Decide the deployment type before you deploy",
            "intro": [
                "Open `data/deployment-options.yaml`. It states three scenarios and, for each, the check you "
                "must perform. Read it as a decision aid, not as a claim about what is available today.",
                {"table": (["Requirement", "Candidate type", "What you must verify"], [
                    ["Australian processing required", "Regional Standard",
                     "That the exact model **and version** is offered in `australiaeast`, and that your "
                     "organisation's policy accepts it."],
                    ["Approved geographic data zone", "DataZoneStandard",
                     "Which zone is actually offered. Never assume an Australian data zone exists."],
                    ["Global processing explicitly approved", "GlobalStandard",
                     "Model availability, and a written record of the approved geography."],
                ])},
            ],
            "steps": [
                ["Decide which row applies to a scenario where Acme must keep resident enquiry processing in "
                 "Australia. Write down your choice and the reason before you open the portal.",
                 {"warn": "If the only available type violates the approved processing geography, the correct "
                          "outcome is to stop and escalate — not to switch to a Global SKU because it has quota."}],
                ["The broader catalogue also offers provisioned throughput (PTU), serverless/API offerings and "
                 "managed compute. Those are compared in the worksheet used by Exercise 17. They are not "
                 "interchangeable SKU names, and not every model offers every option — which is why you check "
                 "per model rather than reasoning from the family name."],
            ],
        },
        {
            "h2": "Check quota, then deploy one model",
            "intro": ["Follow `data/portal-deployment.md` in the lab folder. The steps below are the same "
                      "sequence with the reasoning spelled out."],
            "steps": [
                ["In the Foundry portal, open the project your instructor supplied. Record the subscription, "
                 "resource group, account and project names."],
                ["Open the management or quota view. Filter for the exact model, version, region and deployment "
                 "type you chose. Record the available tokens-per-minute and compare it with the concurrency "
                 "your class will generate.",
                 {"warn": "A model appearing in the catalogue does **not** prove you have quota for it. These "
                          "are two separate checks and the second one is the one that fails at 9:05am on day one."}],
                ["Choose **Deploy model**, select the verified model and version, and name it "
                 "`acme-lab02-chat-<your-unique-suffix>`. Use the smallest quota allocation that will work.",
                 {"tip": "Write that exact name into `data/my-deployment.txt`. Clean-up at the end of this "
                         "exercise deletes only the name recorded in that file, which is what keeps you from "
                         "deleting a classmate's deployment."}],
                ["Select the deployment type you justified earlier, set the capacity, and create it. Wait for "
                 "provisioning to finish."],
                ["Test it in the playground with a harmless synthetic greeting, to confirm the deployment "
                 "actually serves inference and not just that the resource exists."],
                ["Copy the deployment name into `MODEL_DEPLOYMENT` in this exercise's `.env`, then verify from "
                 "code:",
                 {"code": "python src/main.py\npython validate.py --live", "lang": "powershell"},
                 {"ok": "Your new deployment name should now appear in the printed list."}],
            ],
        },
        {
            "h2": "Record the evidence",
            "steps": [
                ["Capture, in your own notes: deployment name, model name, model version, deployment type, "
                 "region, and allocated quota."],
                ["Answer in one sentence: *which of those facts determines where the request is processed?* "
                 "The deployment type and the model's terms — not the account's region, and not the project's "
                 "region."],
                ["If quota was unavailable and you used your instructor's existing deployment, label this "
                 "exercise **inspection-only** in your notes. Do not record it as a deployment you provisioned.",
                 {"note": "This habit matters beyond the classroom. Confusing 'I read the configuration' with "
                          "'I configured it' is how compliance evidence goes wrong."}],
            ],
        },
    ],
    "knowledge_check": [
        {"q": "What determines the geography in which a model request is processed?",
         "options": ["A. The deployment type and the model's terms", "B. The project's location alone",
                     "C. The region in your `.env` file"],
         "answer": "A",
         "why": "An Australia East account can still hold a Global Standard deployment that processes elsewhere. "
                "The type is the control; the account location is not."},
        {"q": "What must you check before promising a model capability to a customer?",
         "options": ["A. The model's display name in the catalogue",
                     "B. Model, version, deployment type, region **and** quota",
                     "C. That the storage account exists"],
         "answer": "B",
         "why": "Catalogue presence and usable quota are independent. Both must hold, for the exact version and "
                "type you intend to deploy."},
        {"q": "The only deployment type with quota would breach your approved processing geography. What do you do?",
         "options": ["A. Deploy it anyway and note it later", "B. Silently switch region",
                     "C. Stop, use an approved demo, and escalate for approval"],
         "answer": "C",
         "why": "Quota pressure is not an approval. Changing processing geography to get capacity is exactly the "
                "decision that has to be made deliberately and recorded."},
    ],
    "summary": [
        "You checked quota against a specific model and version, deployed a uniquely named model, and justified "
        "its deployment type against a residency requirement rather than reasoning from the account's region.",
        "You also recorded the evidence that supports that claim — which is the artefact a reviewer will ask "
        "for, and the artefact that a passing script can never substitute for.",
    ],
    "cleanup": [
        "This exercise creates a billable deployment, so clean-up matters.",
        {"code": "python cleanup.py", "lang": "powershell"},
        "The Python script is informational. Perform the actual deletion in the portal:",
        {"bullets": [
            "Open the deployment named in `data/my-deployment.txt` — **only** that one.",
            "Delete it, then refresh the deployment list to confirm it is gone.",
            "If it is already absent, clean-up is complete; nothing further is needed.",
        ]},
        {"warn": "Do not delete the Foundry account, the project, or any deployment you did not create. Those "
                 "are shared, instructor-owned resources that later exercises depend on."},
    ],
    "refs": [
        ("Deploy models in Foundry", "https://learn.microsoft.com/azure/foundry/how-to/deploy-models-openai"),
        ("Deployment types", "https://learn.microsoft.com/azure/ai-foundry/openai/how-to/deployment-types"),
    ],
}


LAB03 = {
    "num": "03",
    "slug": "03-prompt-agent",
    "short": "Create a versioned prompt agent",
    "group": "Day 1 — Foundry foundations",
    "track": "Foundry SDK",
    "module_tags": ["Module 3"],
    "title": "Create a prompt agent and compare two immutable versions",
    "minutes": 45,
    "lab_path": "day1-foundry-sdk-foundations/lab03-prompt-agent",
    "env_note": "`azure-ai-projects==2.6.0`",
    "blurb": "Create a named agent, publish two instruction versions, and invoke the agent through its own client.",
    "intro": [
        "In this exercise you create your first real agent asset: a **prompt agent**, which is a named, "
        "versioned definition stored in the project rather than a string living in your application code.",
        "This is the first half of the agent lifecycle the client asked about — *create* and *version*. "
        "Exercises 11, 12, 22 and 23 add evaluate, trace, publish and monitor. Understanding why versions are "
        "immutable here makes the release gate in Exercise 23 obvious later.",
    ],
    "objectives": [
        "Create a named prompt agent with `create_version()`.",
        "Publish a second version with different instructions and see that the first is unchanged.",
        "List stored versions to make the version boundary visible.",
        "Invoke the agent through an agent-bound OpenAI-compatible client.",
    ],
    "prereqs": [
        "A Foundry project and a working chat deployment, as in Exercise 01.",
        "A project role that permits creating agents.",
    ],
    "sections": [
        {
            "h2": "Set up",
            "steps": [
                [{"code": "cd day1-foundry-sdk-foundations/lab03-prompt-agent\n" + SETUP_PS, "lang": "powershell"}],
                ["Fill in `.env`. `MODEL_DEPLOYMENT` must be a deployment name that exists in your project — "
                 "this is the first exercise that will fail with a 404 if it is wrong.",
                 {"code": "python validate.py", "lang": "powershell"}],
            ],
        },
        {
            "h2": "Understand what a version is before creating one",
            "intro": ["Open `src/main.py`. Four things happen, in order."],
            "steps": [
                ["**A unique name is recorded locally first.** The script writes a generated name such as "
                 "`acme-lab03-prompt-7f3a9c21` into `data/resource-state.json`.",
                 {"code": """state_file = Path("data/resource-state.json")
if not state_file.exists():
    state_file.write_text(json.dumps({"agent": "acme-lab03-prompt-" + uuid4().hex[:8]}))""", "lang": "python"},
                 "It records the name *before* creating anything in Azure. That ordering is deliberate: if "
                 "creation succeeds but the process dies, you still own a record of what to clean up."],
                ["**Two versions are created under that one name.** Each `create_version()` call publishes a new, "
                 "immutable version. It does not edit the previous one.",
                 {"code": """for instructions in ["Answer in Australian English.",
                     "Answer in Australian English using one short sentence."]:
    agent = project.agents.create_version(
        agent_name=state["agent"],
        definition=PromptAgentDefinition(
            model=os.environ["MODEL_DEPLOYMENT"],
            instructions=instructions,
        ),
    )""", "lang": "python"},
                 {"note": "A `PromptAgentDefinition` carries the model *and* the instructions. Changing either "
                          "one produces a new version — the model choice is part of the versioned definition, "
                          "not a runtime parameter."}],
                ["**Stored versions are listed**, which is what makes the boundary visible rather than theoretical."],
                ["**Inference is bound to the agent by name**, so the request does not restate the instructions:",
                 {"code": """client = project.get_openai_client(agent_name=state["agent"])
response = client.responses.create(
    input="Explain why an agent might use a tool.", store=False)""", "lang": "python"},
                 "Notice there is no `model=` and no `instructions=` on that call. Both come from the stored "
                 "agent definition. Compare this with Exercise 04, where you supply both explicitly."],
            ],
        },
        {
            "h2": "Run it and observe versioning",
            "steps": [
                [{"code": "python src/main.py", "lang": "powershell"},
                 "Expect one agent name, two created version numbers, the stored version list, and a short "
                 "Australian English answer."],
                ["Run the script **again** without changing anything.",
                 {"code": "python src/main.py", "lang": "powershell"},
                 "It reuses the same agent name from `data/resource-state.json` and adds two more versions. "
                 "You now have four. Versions accumulate; they do not overwrite."],
                ["Change the second instruction string — for example, ask for two sentences instead of one — "
                 "and run again. Compare the new answer's style with the earlier one.",
                 {"tip": "Model wording is nondeterministic, so compare *style and length*, not exact text. "
                         "This is the same reason Exercise 23 scores answers with a rubric rather than string "
                         "equality."}],
                ["Confirm the versions really exist server-side:",
                 {"code": "python validate.py --live", "lang": "powershell"},
                 {"ok": "`PASS: LIVE two agent versions` confirms the service returned at least two versions "
                        "for your agent name."}],
            ],
        },
        {
            "h2": "Why immutability matters",
            "intro": [
                "It would be simpler to let instructions be edited in place. Foundry does not, and the reason "
                "shows up later in this workshop.",
            ],
            "steps": [
                ["In Exercise 23 you build a release gate that ties an evaluation report to a specific revision. "
                 "That only means something if the thing evaluated cannot silently change afterwards."],
                ["In Exercise 22's publishing walkthrough you publish a version to a channel and then roll back "
                 "to a previously approved version. Rollback requires the old definition to still exist."],
                ["Write one sentence in your notes: what would break in a release process if agent instructions "
                 "were mutable?"],
            ],
        },
    ],
    "knowledge_check": [
        {"q": "What is a prompt agent?",
         "options": ["A. A named, versioned definition stored in the project", "B. A virtual machine",
                     "C. A copy of your `.env` file"],
         "answer": "A",
         "why": "It bundles a model and instructions under a name, with each change published as a new version."},
        {"q": "You need to change an agent's instructions. What happens?",
         "options": ["A. The existing version is edited in place", "B. A new version is created",
                     "C. The project must be recreated"],
         "answer": "B",
         "why": "Versions are immutable. That is what makes evaluation evidence and rollback meaningful."},
        {"q": "In `client.responses.create(input=...)` after `get_openai_client(agent_name=...)`, "
              "where do the model and instructions come from?",
         "options": ["A. The `.env` file, read at call time", "B. Defaults chosen by the service",
                     "C. The stored agent version the client is bound to"],
         "answer": "C",
         "why": "Binding the client to an agent name is what lets the call omit both. Exercise 04 shows the "
                "opposite style, where the application supplies them on every request."},
    ],
    "summary": [
        "You created a named prompt agent, published two immutable instruction versions, listed them, and "
        "invoked the agent through an agent-bound client that needed neither a model name nor instructions.",
        "You have now done the *create* and *version* steps of the lifecycle. Keep the agent name in "
        "`data/resource-state.json` until you have run clean-up.",
    ],
    "cleanup": [
        "This exercise creates a real agent in your project. Remove it.",
        {"code": "python cleanup.py", "lang": "powershell"},
        "The script prints the recorded resource names, asks you to type `DELETE` to confirm, and then removes "
        "**only** the agent whose name starts with `acme-lab03-prompt-`. It refuses anything else, and it "
        "deletes `data/resource-state.json` on success.",
        {"tip": "If you ran the script several times, all versions live under that one agent name, so a single "
                "clean-up removes all of them."},
    ],
    "refs": [
        ("Prompt agent quickstart", "https://learn.microsoft.com/azure/foundry/agents/quickstarts/prompt-agent"),
    ],
}


LAB04 = {
    "num": "04",
    "slug": "04-responses-api",
    "short": "Responses API, conversations and streaming",
    "group": "Day 1 — Foundry foundations",
    "track": "Foundry SDK",
    "module_tags": ["Module 2", "Module 3"],
    "title": "Call models directly with the Responses API, conversations and streaming",
    "minutes": 45,
    "lab_path": "day1-foundry-sdk-foundations/lab04-responses-api",
    "env_note": "`azure-ai-projects==2.6.0`",
    "blurb": "Use the OpenAI-compatible Responses API without creating an agent, carry state across turns, and "
             "stream text deltas.",
    "intro": [
        "Exercise 03 stored a definition on the server. This exercise does the opposite: the application keeps "
        "the instructions and names the model on every call, using the OpenAI-compatible **Responses API**.",
        "Both styles are valid, and the choice has real consequences for versioning, evaluation and clean-up. "
        "You will also meet two mechanics that reappear throughout the workshop: a server-side *conversation* "
        "that carries context between turns, and *streaming*, which Exercise 21 turns into a live chat UI.",
    ],
    "objectives": [
        "Call a model without creating any agent resource.",
        "Reuse a conversation across two turns and observe recall.",
        "Print incremental text as it is generated.",
        "Choose between a stored agent definition and application-supplied instructions.",
    ],
    "prereqs": ["A Foundry project and a working chat deployment, as in Exercise 01."],
    "sections": [
        {
            "h2": "Set up",
            "steps": [
                [{"code": "cd day1-foundry-sdk-foundations/lab04-responses-api\n" + SETUP_PS, "lang": "powershell"}],
                ["Fill in `.env`, then run the offline check:",
                 {"code": "python validate.py", "lang": "powershell"}],
            ],
        },
        {
            "h2": "Carry context across two turns",
            "intro": ["Open `src/main.py`. Unlike Exercise 03, `get_openai_client()` is called with no agent "
                      "name, so every request must state its own model and instructions."],
            "steps": [
                ["A conversation is created as a **server-side resource** and its ID is recorded locally:",
                 {"code": """conversation = client.conversations.create()
state["conversations"].append(conversation.id)
state_file.write_text(json.dumps(state))""", "lang": "python"},
                 {"note": "This is why the exercise has a clean-up step even though it creates no agent. "
                          "'No agent' does not mean 'nothing persisted'."}],
                ["Two questions are then sent against that same conversation ID:",
                 {"code": """for question in ["Our synthetic workshop is in Sydney. Remember this location.",
                 "Which city is our workshop in?"]:
    response = client.responses.create(
        model=os.environ["MODEL_DEPLOYMENT"],
        instructions="Answer briefly in Australian English.",
        conversation=conversation.id,
        input=question,
    )""", "lang": "python"}],
                ["Run it:",
                 {"code": "python src/main.py", "lang": "powershell"},
                 {"ok": "The second answer should mention Sydney, even though the second request never repeats it."}],
                ["Now prove where that memory lives. Edit the script to remove the `conversation=conversation.id` "
                 "argument from both calls, and run again. The second answer can no longer name the city. "
                 "Restore the argument afterwards.",
                 {"tip": "The model has no memory of its own. The conversation resource is what carries state, "
                         "which is exactly why Exercise 19 has to make a deliberate decision about where "
                         "conversation state is stored for a real application."}],
            ],
        },
        {
            "h2": "Stream the response",
            "steps": [
                ["Open `src/stream.py`. The only differences are `stream=True` and a loop that filters events:",
                 {"code": """with client.responses.create(model=os.environ["MODEL_DEPLOYMENT"],
                             input="Explain tool calling in two sentences.",
                             stream=True, store=False) as events:
    for event in events:
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)""", "lang": "python"}],
                ["Run it and watch the text arrive progressively:",
                 {"code": "python src/stream.py", "lang": "powershell"}],
                ["A stream emits several event types — lifecycle events, content events and completion events. "
                 "This example prints only `response.output_text.delta`. Temporarily remove the `if` and print "
                 "`event.type` for every event to see the full sequence, then restore it.",
                 {"note": "Exercise 21 forwards these same deltas to a browser as server-sent events, and uses "
                          "the completion event to know when the answer is finished. Seeing the raw event "
                          "types here makes that code much easier to read."}],
                ["Note that `stream.py` passes `store=False`, so this call leaves nothing behind."],
            ],
        },
        {
            "h2": "Choose between an agent and a direct call",
            "intro": [
                "You have now built the same capability two ways. The table below is the decision you will be "
                "asked to justify.",
                {"table": (["Dimension", "Prompt agent (Exercise 03)", "Responses API (Exercise 04)"], [
                    ["Definition", "Named, versioned server asset", "Instructions live in application code"],
                    ["Inference call", "Agent-bound client; no model argument", "Explicit model and instructions each time"],
                    ["Memory", "Explicit conversation, if used", "Explicit conversation, if used"],
                    ["Versioning and rollback", "Built in", "Your own source control and release process"],
                    ["Clean-up", "Agent versions, plus any conversations", "Conversations only"],
                ])},
            ],
            "steps": [
                ["Decide which you would use for a resident-facing assistant whose wording must be reviewed and "
                 "approved before each change, and write down why."],
                ["Decide which you would use for a short internal batch job that summarises documents once a "
                 "night. The answers are usually different, and that is the point."],
            ],
        },
    ],
    "knowledge_check": [
        {"q": "What allows the second turn to recall Sydney?",
         "options": ["A. The conversation ID passed to both requests", "B. The script's filename",
                     "C. The model's built-in memory"],
         "answer": "A",
         "why": "Remove the `conversation` argument and recall disappears. The model is stateless; the "
                "conversation resource carries the context."},
        {"q": "Which streaming event carries incremental text?",
         "options": ["A. `conversation.created`", "B. `response.output_text.delta`", "C. `deployment.deleted`"],
         "answer": "B",
         "why": "Other event types describe lifecycle and completion; only the delta events carry text fragments."},
        {"q": "This exercise creates no agent. Does that mean nothing is stored?",
         "options": ["A. No — conversations are server resources and persist", "B. Yes, always",
                     "C. Only outside Australia"],
         "answer": "A",
         "why": "`main.py` creates conversations that outlive the process, which is why this exercise still has "
                "a clean-up step. `store=False` in `stream.py` is what avoids retaining a response."},
    ],
    "summary": [
        "You called a model directly through the Responses API, carried context across two turns with a "
        "server-side conversation, proved where that memory lives by removing it, and streamed text deltas.",
        "You also compared the stored-definition and application-supplied styles. Exercise 13 revisits exactly "
        "this comparison one level higher, between the Foundry SDK and the Microsoft Agent Framework.",
    ],
    "cleanup": [
        {"code": "python cleanup.py", "lang": "powershell"},
        "Clean-up removes the conversations recorded in `data/resource-state.json`. Those are real server "
        "resources created by `main.py`, so run this even though the exercise created no agent.",
    ],
    "refs": [
        ("Responses API quickstart", "https://learn.microsoft.com/azure/foundry/agents/quickstarts/responses-api"),
        ("Responses streaming", "https://learn.microsoft.com/azure/foundry/openai/how-to/responses"),
    ],
}

LABS = [LAB01, LAB02, LAB03, LAB04]
