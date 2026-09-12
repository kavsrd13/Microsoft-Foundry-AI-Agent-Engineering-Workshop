"""Exercises 13-16 — Microsoft Agent Framework (Day 4)."""

MAF_SETUP = """py -3.11 -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
az login"""

MAF_WARN = {
    "warn": "Day 4 uses a **different and incompatible** package set from Days 1-3. The pinned Foundry "
            "provider requires `azure-ai-projects` below 2.4, so these exercises pin **2.3.0** while Days 1-3 "
            "pin 2.6.0. Create a fresh virtual environment for each Day 4 exercise and never install a Day 1-3 "
            "requirements file into it."
}


LAB13 = {
    "num": "13",
    "slug": "13-maf-transition",
    "short": "Foundry SDK compared with Agent Framework",
    "group": "Day 4 — Microsoft Agent Framework",
    "track": "Agent Framework",
    "module_tags": ["Module 3"],
    "title": "Run the same task through the Foundry SDK and the Microsoft Agent Framework",
    "minutes": 45,
    "lab_path": "day4-agent-framework/lab13-maf-transition",
    "env_note": "`agent-framework==1.17.0`, `agent-framework-foundry==1.12.0`, `azure-ai-projects==2.3.0`",
    "blurb": "Two scripts, one identical task, so you can see exactly what the framework adds and what it does "
             "not.",
    "intro": [
        "The Microsoft Agent Framework is an application framework that sits **on top of** the Foundry SDK. "
        "In this exercise you run one identical task both ways and compare them honestly.",
        "The honest comparison matters because the usual framework demonstration quietly picks a task that "
        "flatters the framework. For a single model call the framework is slightly *longer*, not shorter. Its "
        "value appears in Exercises 14, 15 and 16, when sessions, middleware and workflows arrive.",
    ],
    "objectives": [
        "Run the same task with a direct Responses call and with an Agent Framework agent.",
        "Identify where the Foundry SDK still sits inside the framework call path.",
        "Compare code size and control surface without assuming fewer lines is better.",
    ],
    "prereqs": [
        "A Foundry project and a working chat deployment.",
        "Python 3.11 and a **fresh** virtual environment for this exercise.",
    ],
    "before_extra": [MAF_WARN],
    "sections": [
        {
            "h2": "Set up an isolated Day 4 environment",
            "steps": [
                [{"code": "cd day4-agent-framework/lab13-maf-transition\n" + MAF_SETUP, "lang": "powershell"}],
                ["Check the pins that were installed. `requirements.txt` carries a comment explaining the "
                 "constraint:",
                 {"code": """# Separate Day 4 environment: Foundry provider 1.12 requires projects <2.4.
azure-ai-projects==2.3.0
azure-identity==1.25.3
python-dotenv==1.2.3
agent-framework==1.17.0
agent-framework-foundry==1.12.0""", "lang": "text"}],
                ["Set `PROJECT_ENDPOINT` and `MODEL_DEPLOYMENT_NAME` in `.env`, then:",
                 {"code": "python validate.py", "lang": "powershell"},
                 {"ok": "`PASS Foundry provider installed` confirms you are in the right environment. If that "
                        "line fails, you are almost certainly in a Day 1-3 environment."}],
            ],
        },
        {
            "h2": "Run the direct SDK version",
            "steps": [
                ["Open `src/a_foundry_sdk.py`. It is the pattern from Exercise 04: project client, OpenAI "
                 "client, one Responses call.",
                 {"code": """response = client.responses.create(
    model=os.environ['MODEL_DEPLOYMENT_NAME'],
    instructions='Use Australian English. Answer in two sentences.',
    input='Explain why a government service assistant should cite its sources.',
    store=False)
print(response.output_text)""", "lang": "python"}],
                [{"code": "python src/a_foundry_sdk.py", "lang": "powershell"},
                 "Note the `store=False`: this call retains no response resource, so there is nothing to clean up."],
            ],
        },
        {
            "h2": "Run the framework version",
            "steps": [
                ["Open `src/b_agent_framework.py`. The task string and the instruction string are **character "
                 "for character identical** to the first script. Everything that differs is structure.",
                 {"code": """async with DefaultAzureCredential() as credential, \\
           AIProjectClient(endpoint=os.environ['PROJECT_ENDPOINT'],
                           credential=credential) as project:
    client = FoundryChatClient(project_client=project,
                               model=os.environ['MODEL_DEPLOYMENT_NAME'])
    agent = Agent(client,
                  instructions='Use Australian English. Answer in two sentences.',
                  default_options={'store': False})
    print((await agent.run('Explain why a government service assistant should cite its sources.')).text)""",
                  "lang": "python"}],
                [{"code": "python src/b_agent_framework.py", "lang": "powershell"},
                 "Both scripts answer the same question. Wording differs between runs because model output is "
                 "nondeterministic — compare the shape, not the text."],
                ["Find the line that answers the key architectural question:",
                 {"code": "client = FoundryChatClient(project_client=project, ...)", "lang": "python"},
                 {"note": "The framework is handed **the same `AIProjectClient`** you used in the first script. "
                          "The framework does not replace the Foundry SDK; it composes with it. Your project, "
                          "RBAC, endpoint and deployment story are unchanged."}],
                ["Note that the framework version is asynchronous. `Agent.run()` is awaited, which is why "
                 "`main()` is a coroutine driven by `asyncio.run()`. This is a real difference in how you "
                 "structure an application, not a cosmetic one."],
            ],
        },
        {
            "h2": "Compare them fairly",
            "intro": [
                {"table": (["Dimension", "Direct SDK", "Agent Framework"], [
                    ["Non-blank Python lines", "14", "17"],
                    ["Concepts beyond auth and config",
                     "Project client, Responses request, output text (3)",
                     "Project client, chat client, Agent, async run (4)"],
                    ["Control surface", "Explicit Responses request fields",
                     "Agent lifecycle, tools, context providers, middleware"],
                    ["Dependency", "`azure-ai-projects`",
                     "The provider itself depends on `azure-ai-projects`"],
                    ["Task and instructions", "Identical", "Identical"],
                ])},
            ],
            "steps": [
                ["For a single call, the framework costs you three extra lines and one extra concept. Accept "
                 "that honestly rather than explaining it away."],
                ["Now consider what you would have to write yourself, in the direct version, to add: "
                 "conversation history that survives a restart; a rule that blocks certain requests before any "
                 "model call; logging around every tool invocation; three agents cooperating on one task.",
                 "Those are Exercises 14, 15 and 16 — and each is a handful of lines in the framework."],
                ["Write down your own answer to: *at what point in a project would you adopt the framework, and "
                 "what would make you keep the direct SDK?*",
                 {"tip": "A defensible answer names a specific capability you need — not 'it is cleaner'."}],
            ],
        },
    ],
    "knowledge_check": [
        {"q": "Under the Agent Framework's Foundry provider, what supplies project access?",
         "options": ["A. Browser storage", "B. The Foundry SDK's `AIProjectClient`", "C. A SQL database"],
         "answer": "B",
         "why": "`FoundryChatClient` is given the same project client. The framework composes with the SDK "
                "rather than replacing it."},
        {"q": "Does the Agent Framework always reduce the size of a single-call script?",
         "options": ["A. Yes", "B. No", "C. Only when using API keys"],
         "answer": "B",
         "why": "Here it is three lines longer. The benefit arrives with sessions, middleware and workflows."},
        {"q": "Which part of the two scripts is identical?",
         "options": ["A. The task and instruction strings", "B. The output wording", "C. The import count"],
         "answer": "A",
         "why": "Holding the task constant is what makes the structural comparison meaningful."},
    ],
    "summary": [
        "You ran one identical task through the Foundry SDK and the Agent Framework, confirmed the framework "
        "delegates project access to the same `AIProjectClient`, and compared them without pretending the "
        "framework was shorter.",
        "You also set up the isolated Day 4 environment that Exercises 14 to 16 depend on.",
    ],
    "cleanup": [
        {"code": "python cleanup.py", "lang": "powershell"},
        "Both scripts pass `store=False`, so no response resources persist and no agent is registered. There is "
        "nothing to delete in Azure.",
    ],
    "refs": [
        ("Agent Framework with Foundry",
         "https://learn.microsoft.com/agent-framework/integrations/by-component/model-providers/microsoft-foundry"),
    ],
}


LAB14 = {
    "num": "14",
    "slug": "14-session-and-context",
    "short": "Sessions, persistence and context providers",
    "group": "Day 4 — Microsoft Agent Framework",
    "track": "Agent Framework",
    "module_tags": ["Module 5"],
    "title": "Persist a conversation across processes and inject per-user context",
    "minutes": 45,
    "lab_path": "day4-agent-framework/lab14-session-and-context",
    "env_note": "Day 4 environment; see the warning below",
    "blurb": "Serialise an AgentSession to disk, restore it in a new object, and add a ContextProvider that "
             "injects each user's preferences.",
    "intro": [
        "This exercise covers the framework half of the client's memory question: **short-term** conversation "
        "history that survives a save and restore, and **long-term** per-user preferences injected at run time.",
        "Exercise 19 covers the other half — where that state actually lives in production, and why a partition "
        "key is not an authorisation control. Together they answer 'what is remembered' and 'where is it kept'.",
    ],
    "objectives": [
        "Keep conversation history in an `AgentSession`.",
        "Serialise a session to JSON and reconstruct it.",
        "Inject per-user preferences with a `ContextProvider`.",
        "Keep two users' conversations isolated from each other.",
    ],
    "prereqs": ["A Foundry project and chat deployment, and the Day 4 environment."],
    "before_extra": [MAF_WARN],
    "sections": [
        {
            "h2": "Set up and read the profiles",
            "steps": [
                [{"code": "cd day4-agent-framework/lab14-session-and-context\n" + MAF_SETUP, "lang": "powershell"}],
                ["Set `PROJECT_ENDPOINT` and `MODEL_DEPLOYMENT_NAME`, then `python validate.py`."],
                ["Open `data/user_preferences.json` and read the first two records. Each has a `user_id`, "
                 "`language`, `tone` and `preferred_channel`.",
                 {"warn": "These are synthetic profiles, not authenticated identities. Nothing in this exercise "
                          "verifies that the caller *is* the user whose profile it loads. That gap is the whole "
                          "point of the last section."}],
            ],
        },
        {
            "h2": "Inject per-user context",
            "intro": ["Open `src/demo.py`. A `ContextProvider` is a hook that runs before each agent run and "
                      "can contribute instructions."],
            "steps": [
                [{"code": """class Preferences(ContextProvider):
    async def before_run(self, *, agent, session, context, state) -> None:
        profiles = json.loads((ROOT / 'data/user_preferences.json').read_text())
        profile = next(p for p in profiles if p['user_id'] == session.state['user_id'])
        context.extend_instructions(
            self.source_id,
            f"Use {profile['language']} and a {profile['tone']} tone. "
            f"Preferred channel: {profile['preferred_channel']}.")""", "lang": "python"}],
                ["Three things are worth noticing:",
                 {"bullets": [
                     "The user is chosen from `session.state['user_id']` — the session carries who this "
                     "conversation belongs to.",
                     "`context.extend_instructions(...)` **adds** to the agent's instructions for this run "
                     "rather than replacing them, so the agent's base rules survive.",
                     "Only the one hook this lesson needs is implemented. A provider can do more, but a small "
                     "provider is easier to reason about.",
                 ]}],
                ["Two providers are registered on the agent:",
                 {"code": """agent = Agent(client,
    instructions='Help with public services. Do not invent policy.',
    context_providers=[InMemoryHistoryProvider(), Preferences('preferences')],
    default_options={'store': False})""", "lang": "python"},
                 "`InMemoryHistoryProvider` is what puts the conversation messages into session state. Without "
                 "it, each run would start blank."],
            ],
        },
        {
            "h2": "Persist and restore a conversation",
            "steps": [
                ["Run the demo:",
                 {"code": "python src/demo.py", "lang": "powershell"}],
                ["Follow the three runs it performs. First, a case reference is supplied and the session is "
                 "written to disk:",
                 {"code": """print((await agent.run('My case reference is ACME-204. Please remember it.',
                       session=session)).text)
(ROOT / 'data/session.json').write_text(json.dumps(session.to_dict(), indent=2))""", "lang": "python"}],
                ["Second, a **new session object** is reconstructed from that JSON and asked to recall it:",
                 {"code": """restored = AgentSession.from_dict(json.loads((ROOT / 'data/session.json').read_text()))
print((await agent.run('What case reference did I give you?', session=restored)).text)""",
                  "lang": "python"},
                 {"ok": "The restored session should answer ACME-204. It is a different Python object, rebuilt "
                        "from serialised state — which is exactly what a web application does between requests."}],
                ["Third, a **different user's** session asks the same thing and must not know the reference:",
                 {"code": """other = AgentSession()
other.state['user_id'] = profiles[1]['user_id']
print((await agent.run('Introduce how you can help. Do you know my case reference?',
                       session=other)).text)""", "lang": "python"},
                 {"ok": "The second user should not know ACME-204, and should answer in their own profile's "
                        "language and tone."}],
                ["Open `data/session.json` and read it. You can see the conversation content in plain text.",
                 {"warn": "This is a small classroom file, not a session database. If real conversation content "
                          "were stored this way it would need the same protection as any other record — "
                          "encryption, access control, retention and a defined location. Exercise 19 provides "
                          "the production answer."}],
            ],
        },
        {
            "h2": "Recognise what is missing",
            "intro": [
                "This exercise deliberately stops short of a safe design, and you should be able to name the gap.",
            ],
            "steps": [
                ["The user identity comes from `session.state['user_id']`, which the script simply sets. In a "
                 "web application, a request-supplied user ID is **not** authorisation — anyone could send "
                 "another user's ID.",
                 {"warn": "Derive the user identity from a validated sign-in, as Exercise 21 does, and use that "
                          "verified value as the partition. Never take it from the request body."}],
                ["The history here lives in memory and in one local JSON file. It does not survive across "
                 "servers, does not expire, and has no per-user isolation beyond your own code. Exercise 19 "
                 "adds a real store, a partition key derived from a token, and TTLs that distinguish a "
                 "one-hour conversation from a one-day preference."],
                ["Write down the three properties a production session store needs that this exercise lacks: "
                 "trusted identity, durable shared storage, and a retention policy."],
            ],
        },
    ],
    "knowledge_check": [
        {"q": "What preserves the conversational messages locally?",
         "options": ["A. `InMemoryHistoryProvider` together with session state", "B. The profile's tone setting",
                     "C. The model deployment name"],
         "answer": "A",
         "why": "The history provider writes messages into the session; `to_dict()` then serialises them."},
        {"q": "Is a user ID taken from the incoming request trusted authorisation?",
         "options": ["A. Yes", "B. No", "C. Only if it is short"],
         "answer": "B",
         "why": "It must be derived from a validated sign-in. Exercise 21 shows the verification that makes a "
                "claim trustworthy."},
        {"q": "How should two users' conversations be isolated?",
         "options": ["A. Share all history and filter afterwards", "B. Change only the prompt wording",
                     "C. Use separate sessions keyed by a verified identity"],
         "answer": "C",
         "why": "Isolation must be structural. Filtering after the fact means the data was already loaded."},
    ],
    "summary": [
        "You kept a conversation in an `AgentSession`, serialised it to JSON, restored it into a new object and "
        "confirmed recall, injected per-user preferences with a `ContextProvider`, and kept a second user's "
        "session isolated.",
        "You also named what this design lacks for production — trusted identity, durable storage and "
        "retention — which is exactly what Exercise 19 supplies.",
    ],
    "cleanup": [
        {"code": "python cleanup.py", "lang": "powershell"},
        "No Azure resources are created; `store=False` keeps model history local. Clean-up removes "
        "`data/session.json`, which contains synthetic conversation content.",
    ],
    "refs": [
        ("Context providers",
         "https://learn.microsoft.com/agent-framework/concepts/agents/conversations/context-providers"),
    ],
}


LAB15 = {
    "num": "15",
    "slug": "15-middleware",
    "short": "Middleware and short-circuiting",
    "group": "Day 4 — Microsoft Agent Framework",
    "track": "Agent Framework",
    "module_tags": ["Module 3", "Module 8"],
    "title": "Intercept agent, model and tool calls with middleware",
    "minutes": 45,
    "lab_path": "day4-agent-framework/lab15-middleware",
    "env_note": "Day 4 environment; see the warning below",
    "blurb": "Wrap three different boundaries, trace the call order, block a request before any inference, and "
             "redact PII from logs.",
    "intro": [
        "Middleware is where cross-cutting concerns belong: logging, redaction, policy enforcement and "
        "short-circuiting. In this exercise you register middleware at three distinct boundaries and watch the "
        "order in which they fire.",
        "You will also block a request **before any model or tool call happens**, which is the cheapest and "
        "safest place to enforce a policy — nothing is sent anywhere, so nothing can leak and nothing is billed.",
    ],
    "objectives": [
        "Distinguish agent, chat and function middleware.",
        "Trace before and after behaviour around `call_next()`.",
        "Short-circuit a run by setting a result and not calling `call_next()`.",
        "Redact synthetic email addresses from log output — and see what redaction does not cover.",
    ],
    "prereqs": ["A Foundry project and chat deployment, and the Day 4 environment."],
    "before_extra": [MAF_WARN],
    "sections": [
        {
            "h2": "Set up",
            "steps": [
                [{"code": "cd day4-agent-framework/lab15-middleware\n" + MAF_SETUP, "lang": "powershell"}],
                ["Set `PROJECT_ENDPOINT` and `MODEL_DEPLOYMENT_NAME`, then `python validate.py`."],
            ],
        },
        {
            "h2": "Understand the three boundaries",
            "intro": ["Open `src/demo.py`. Four middleware classes are defined, and where each is *registered* "
                      "is as important as what it does."],
            "steps": [
                [{"table": (["Class", "Base", "Wraps", "Registered on"], [
                    ["`RunLog`", "`AgentMiddleware`", "The whole agent run", "The agent"],
                    ["`BlockExport`", "`AgentMiddleware`", "The whole agent run", "The agent"],
                    ["`ModelLog`", "`ChatMiddleware`", "Each model call", "The chat client"],
                    ["`ToolLog`", "`FunctionMiddleware`", "Each tool invocation", "The chat client"],
                ])}],
                ["Every one has the same shape — work before, `await call_next()`, work after:",
                 {"code": """class ToolLog(FunctionMiddleware):
    async def process(self, context, call_next):
        print('3 TOOL before:', context.function.name)
        await call_next()
        print('4 TOOL after')""", "lang": "python"},
                 "`call_next()` is the rest of the pipeline. What you do before it sees the request; what you "
                 "do after it sees the result; and whether you call it at all decides if the operation happens."],
            ],
        },
        {
            "h2": "Trace the call order",
            "steps": [
                [{"code": "python src/demo.py", "lang": "powershell"},
                 "The first request asks for an order's status and total, which requires tool calls."],
                ["Read the numbered console output. The numbers are boundary labels, and the nesting tells you "
                 "the structure: a RUN surrounds everything; MODEL pairs surround each inference; TOOL pairs "
                 "surround each function."],
                ["Count the MODEL pairs. There will usually be **more than one** inside a single RUN, because "
                 "the agent calls the model, receives tool requests, runs the tools, then calls the model again "
                 "with the results.",
                 {"note": "The labels are numbered 1 to 6 for readability, but do not expect a flat 1-2-3-4-5-6 "
                          "trace. The real sequence depends on how many tools the model decides to call."}],
            ],
        },
        {
            "h2": "Block a request before it costs anything",
            "steps": [
                ["Read `BlockExport`. It sets a result and **returns without calling `call_next()`**:",
                 {"code": """class BlockExport(AgentMiddleware):
    async def process(self, context, call_next):
        if any('export all' in m.text.lower() for m in context.messages):
            context.result = AgentResponse(
                messages=[Message('assistant', ['Bulk export is disabled in this demo.'])])
            print('BLOCK: call_next was not called; no model or tool call.')
            return
        await call_next()""", "lang": "python"}],
                ["The second request in the demo is `Export all orders`. In the output, confirm that the BLOCK "
                 "line appears and that **no MODEL or TOOL lines appear for that request** — while the outer "
                 "RUN pair still completes normally.",
                 {"ok": "No model call means no tokens billed, no data sent to the model, and no tool executed. "
                        "This is the cheapest possible enforcement point."}],
                ["Compare this with filtering an answer after generation. By then the model has already seen "
                 "the data and produced text, and you are relying on catching it. Blocking first avoids the "
                 "question entirely."],
            ],
        },
        {
            "h2": "Redact logs, and see what redaction does not do",
            "steps": [
                ["`RunLog` redacts email addresses from what it prints:",
                 {"code": """text = ' '.join(m.text for m in context.messages)
print('1 RUN before:',
      re.sub(r'[\\w.+-]+@[\\w.-]+\\.[A-Za-z]{2,}', '[EMAIL REDACTED]', text))""", "lang": "python"}],
                ["The first request contains `learner@acme.com.au`. Confirm it appears as `[EMAIL REDACTED]` in "
                 "the console."],
                ["Now the important part. **The email still reached the model.** The middleware redacted the "
                 "log line, not the request.",
                 {"warn": "Log redaction and data minimisation are different controls. If the address must not "
                          "reach the model, remove it from the message before `call_next()` — not from the "
                          "string you print."}],
                ["Note also that the middleware deliberately does not print tool arguments, tool results or "
                 "model responses. Logging everything 'for debugging' is how sensitive content ends up in a "
                 "log store with weaker access controls than the system it came from."],
                ["Test the regex honestly. Try a request containing an address the pattern misses.",
                 {"warn": "A regex is an illustration, not a PII detector. Real redaction needs a purpose-built "
                          "classifier and a policy about what is collected in the first place."}],
            ],
        },
    ],
    "knowledge_check": [
        {"q": "What happens if middleware sets a result and does not call `call_next()`?",
         "options": ["A. The run short-circuits and returns that result", "B. The request is retried",
                     "C. A second agent is created"],
         "answer": "A",
         "why": "No model or tool call occurs, so nothing is sent and nothing is billed."},
        {"q": "Which middleware type surrounds a tool invocation?",
         "options": ["A. Chat middleware", "B. Function middleware", "C. Session middleware"],
         "answer": "B",
         "why": "Chat middleware wraps model calls; agent middleware wraps the whole run."},
        {"q": "Does redacting an email in the log remove it from what the model received?",
         "options": ["A. Yes", "B. No", "C. Only on Windows"],
         "answer": "B",
         "why": "The redaction applies to the printed string. The original message was still sent."},
    ],
    "summary": [
        "You registered middleware at the agent, model and tool boundaries, traced the real call order including "
        "multiple model round-trips inside one run, short-circuited a request before any inference occurred, and "
        "redacted PII from logs.",
        "You also drew the line between log redaction and data minimisation — a distinction that matters as soon "
        "as real personal information is involved.",
    ],
    "cleanup": [
        {"code": "python cleanup.py", "lang": "powershell"},
        "No Azure resources are created and `store=False` keeps nothing server-side.",
    ],
    "refs": [
        ("Agent Framework middleware", "https://learn.microsoft.com/agent-framework/agents/middleware/"),
    ],
}


LAB16 = {
    "num": "16",
    "slug": "16-orchestration-and-hosted",
    "short": "Multi-agent workflows and hosting",
    "group": "Day 4 — Microsoft Agent Framework",
    "track": "Agent Framework",
    "module_tags": ["Module 6", "Module 7"],
    "title": "Build sequential and concurrent workflows, then host an agent",
    "minutes": 90,
    "lab_path": "day4-agent-framework/lab16-orchestration-and-hosted",
    "env_note": "Day 4 environment plus orchestration and hosting packages; part B needs **Python 3.13**",
    "blurb": "Compare two multi-agent topologies on the same task, run a local Responses host, and review a "
             "real azd deployment recipe.",
    "intro": [
        "This exercise has two parts. **Part A** builds real multi-agent workflows — three agents cooperating "
        "on one briefing, arranged two different ways — and measures them. **Part B** runs a local Responses "
        "host and walks through a genuine `azd` deployment recipe for a hosted agent.",
        "Part A everyone can complete. Part B needs elevated provisioning rights and a Python 3.13 environment; "
        "if those are unavailable, the local host still runs and the deployment becomes an instructor "
        "demonstration.",
    ],
    "objectives": [
        "Build sequential and concurrent workflows over the same three agents.",
        "Explain how information flows differently in each topology.",
        "Measure elapsed time and treat a single run as an observation, not a benchmark.",
        "Run a local `ResponsesHostServer` and call it over HTTP.",
        "Read an azd hosted-agent deployment definition critically.",
    ],
    "prereqs": [
        "A Foundry project and chat deployment, and the Day 4 environment for Part A.",
        "For Part B: **Python 3.13**, the Azure Developer CLI (`azd` ≥ 1.27.1) with the Foundry extension, and "
        "Foundry Project Manager plus provisioning rights.",
    ],
    "before_extra": [MAF_WARN],
    "sections": [
        {
            "h2": "Part A — Set up and build two workflows",
            "steps": [
                [{"code": "cd day4-agent-framework/lab16-orchestration-and-hosted\n" + MAF_SETUP,
                  "lang": "powershell"}],
                ["Set `PROJECT_ENDPOINT` and `MODEL_DEPLOYMENT_NAME`, then `python validate.py`."],
                ["Open `src/workflows.py`. The same three agents are used for both topologies:",
                 {"code": """[('retriever', 'Extract three relevant order facts from the supplied data.'),
 ('analyst',   'Identify service implications using available facts. Do not invent facts.'),
 ('writer',    'Write a concise Australian English briefing using the information available.')]""",
                  "lang": "python"},
                 "Only the builder changes:",
                 {"code": """for label, builder in [('sequential', SequentialBuilder),
                       ('concurrent', ConcurrentBuilder)]:
    workflow = builder(participants=agents).build()
    result = await workflow.run(task)""", "lang": "python"}],
            ],
        },
        {
            "h2": "Part A — Compare information flow, not just speed",
            "steps": [
                [{"code": "python src/workflows.py", "lang": "powershell"},
                 "Both workflows run against the same synthetic order dataset, and timings are written to "
                 "`data/timings.json`."],
                ["Read the two outputs carefully before looking at the times. The difference that matters is "
                 "structural:",
                 {"bullets": [
                     "**Sequential** — each participant sees the earlier messages. The writer can build on the "
                     "analyst's conclusions, which can build on the retriever's facts. This is a dependency "
                     "pipeline.",
                     "**Concurrent** — all three work independently from the same initial input. The writer "
                     "never sees the analyst's output, so the combined result is three parallel perspectives, "
                     "not a refined one.",
                 ]},
                 {"note": "Concurrent is not 'sequential but faster'. It is a different information "
                          "architecture, and for a task where later stages genuinely depend on earlier ones it "
                          "produces a worse answer however quickly it finishes."}],
                ["Now compare `data/timings.json`. Concurrency often reduces elapsed time — and sometimes does "
                 "not, because throttling and network variance can dominate.",
                 {"warn": "One run of each is not a benchmark. Run it three times and note how much the numbers "
                          "move before drawing any conclusion."}],
                ["Choose a task from your own domain and decide which topology fits. Justify it by the "
                 "dependencies between steps, not by speed."],
            ],
        },
        {
            "h2": "Part A — Run a local Responses host",
            "steps": [
                ["Open `src/host.py`. It wraps one agent in a `ResponsesHostServer`, which exposes an HTTP "
                 "endpoint speaking the Responses protocol:",
                 {"code": """agent = Agent(client, name='acme-lab16-assistant',
              instructions='Explain public service concepts concisely in Australian English.')
ResponsesHostServer(agent).run()""", "lang": "python"}],
                ["Start it in one terminal:",
                 {"code": "python src/host.py", "lang": "powershell"},
                 "It listens on port 8088."],
                ["In a **second terminal** in the same lab folder, call it:",
                 {"code": "python src/invoke_local.py", "lang": "powershell"},
                 {"code": """request = urllib.request.Request('http://localhost:8088/responses',
    data=json.dumps({'model': 'acme-lab16-assistant',
                     'input': 'Explain why sources matter in a service briefing.',
                     'stream': False}).encode(),
    headers={'Content-Type': 'application/json'})""", "lang": "python"}],
                ["Note what is and is not local here. The **HTTP server** is on your machine; the **inference** "
                 "still goes to Azure using your Entra credentials. Hosting an agent locally does not make it "
                 "offline.",
                 {"note": "Note also that `model` in the request body is the *agent's name*, not a deployment "
                          "name. The host resolves it to the agent it wraps."}],
                ["Stop the host with Ctrl+C before changing any environment settings."],
            ],
        },
        {
            "h2": "Part B — Review the hosted deployment recipe",
            "intro": [
                "Open `src/DEPLOY.md` and `src/deploy/azure.yaml`. Read both before running anything.",
                {"warn": "This part provisions billable Azure resources including a dedicated project and model "
                         "deployment. Do not run it without your instructor confirming region, model and SKU "
                         "availability, cost and your permissions."},
            ],
            "steps": [
                ["`src/deploy` is a self-contained azd project. Its `agent/main.py` is the same hosting concept "
                 "as `src/host.py`, reading its configuration from environment variables the platform supplies."],
                ["Read `azure.yaml` and notice what is **not** hardcoded:",
                 {"code": """deployments:
  - name: ${AZURE_AI_MODEL_DEPLOYMENT_NAME}
    model:
      format: OpenAI
      name: ${AZURE_AI_MODEL_NAME}
      version: ${AZURE_AI_MODEL_VERSION}
    sku:
      name: ${AZURE_AI_MODEL_SKU}""", "lang": "yaml"},
                 {"note": "The model, version, SKU and region are all parameters. The template deliberately "
                          "refuses to pick GlobalStandard for you or silently choose a different region — the "
                          "residency decision from Exercise 02 stays yours."}],
                ["Check your tooling versions before going further:",
                 {"code": "azd version\nazd ext list\nazd ai agent --help", "lang": "powershell"},
                 "The sample requires azd ≥ 1.27.1 and the agents extension ≥ 1.0.0-beta.9. Install the "
                 "extension with `azd ext install microsoft.foundry`."],
                ["Create a **Python 3.13** environment for this part, install `requirements.txt`, then "
                 "`cd src/deploy` and set your values:",
                 {"code": """azd auth login
azd env new acme-lab16-a1b2c3
azd env set AZURE_LOCATION australiaeast
azd env set AZURE_AI_MODEL_NAME YOUR-VERIFIED-MODEL
azd env set AZURE_AI_MODEL_VERSION YOUR-VERIFIED-VERSION
azd env set AZURE_AI_MODEL_DEPLOYMENT_NAME acme-lab16-chat
azd env set AZURE_AI_MODEL_SKU YOUR-APPROVED-SKU
azd provision
azd deploy
azd ai agent invoke "Explain why service assistants cite sources." """, "lang": "powershell"},
                 {"tip": "Also edit the numeric `capacity: 10` in `azure.yaml` down to the allocation your "
                         "instructor approved."}],
                ["Review the provision change summary **before** accepting it. Then record the resource group, "
                 "project, agent name and version, and deployment type."],
                ["If you lack the rights, quota or runtime, complete Part A and record Part B as not executed, "
                 "naming the precise prerequisite that blocked it."],
            ],
        },
    ],
    "knowledge_check": [
        {"q": "In which topology can the writer use the analyst's output?",
         "options": ["A. Sequential", "B. Independent concurrent", "C. Neither"],
         "answer": "A",
         "why": "Concurrent participants all work from the same initial input and do not see each other's results."},
        {"q": "Which Python version does the hosted deployment in Part B require?",
         "options": ["A. 3.9", "B. 3.11", "C. 3.13"],
         "answer": "C",
         "why": "Part A uses 3.11; the hosting runtime needs its own 3.13 environment."},
        {"q": "Does running `ResponsesHostServer` locally mean inference happens locally?",
         "options": ["A. Yes", "B. No — the HTTP server is local, the model call still goes to Azure",
                     "C. Only for JSON requests"],
         "answer": "B",
         "why": "Local hosting changes where the endpoint lives, not where the model runs. Exercise 17's "
                "Foundry Local section covers actual on-device inference."},
    ],
    "summary": [
        "You built sequential and concurrent workflows over the same three agents, compared their information "
        "flow rather than just their speed, ran a local Responses host and called it over HTTP, and reviewed a "
        "real azd hosted-agent deployment definition.",
        "You also saw that the deployment template refuses to make the residency decision for you — it "
        "parameterises model, version, SKU and region so the choice stays explicit.",
    ],
    "cleanup": [
        "Stop the local host and any second terminal with Ctrl+C, then remove local state:",
        {"code": "python cleanup.py", "lang": "powershell"},
        "If you completed Part B, clean up the deployed environment from the `src/deploy` folder:",
        {"code": "azd env get-values\nazd down", "lang": "powershell"},
        {"warn": "Run `azd down` only against the dedicated environment you created in Part B. Confirm the "
                 "environment name first, and never run it against a shared classroom environment. Then "
                 "re-check the portal for the recorded resource group and agent."},
    ],
    "refs": [
        ("Workflow orchestrations", "https://learn.microsoft.com/agent-framework/workflows/orchestrations/"),
        ("Framework hosted agents",
         "https://learn.microsoft.com/azure/foundry/how-to/develop/framework-hosted-agents"),
    ],
}

LABS = [LAB13, LAB14, LAB15, LAB16]
