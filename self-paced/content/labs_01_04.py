"""Exercises 01-04."""

from ._code import block, task, upto, whole

SETUP = """py -3.11 -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env"""

VENV_NOTE = {
    "warn": "Make a **new virtual environment for every exercise**. The exercises pin different "
            "versions of the same packages on purpose, and one shared environment will break them."
}


# ============================================================================
LAB01 = {
    "num": "01",
    "slug": "01-get-started",
    "short": "Get started with Foundry",
    "group": "Day 1 — Foundations and your first agent",
    "track": "Foundations",
    "module_tags": ["Module 1", "Module 2", "Module 3"],
    "title": "Get started with Microsoft Foundry",
    "minutes": 90,
    "lab_path": "labs/01-get-started",
    "env_note": "`azure-ai-projects`, `azure-identity`, `python-dotenv`",
    "blurb": "Connect with your own identity, see what models you have, ask one, hold a conversation, "
             "and stream an answer.",
    "intro": [
        "You are going to write one Python file, a few lines at a time, and by the end of it you will have "
        "talked to a model four different ways.",
        "Nothing here is complicated. It is worth doing carefully anyway, because these same few lines open "
        "every other exercise in the workshop — and because most of the problems people hit later are "
        "authentication or naming problems that show up right here.",
    ],
    "objectives": [
        "Connect to a Foundry project using your own Entra ID sign-in, with no API key.",
        "List the models your project can actually use.",
        "Send a question and read the answer.",
        "Hold a two-turn conversation and see where the memory lives.",
        "Stream an answer as it is being written.",
    ],
    "prereqs": [
        "An Azure subscription, and the **Azure CLI** installed.",
        "**Python 3.11** installed.",
        "A Microsoft Foundry project with at least one chat model deployed. Your instructor supplies this.",
        "A project role that lets you run inference — *Foundry User* or equivalent.",
    ],
    "before_extra": [VENV_NOTE],
    "sections": [
        {
            "h2": "Task 1: Set up",
            "steps": [
                ["Open a PowerShell terminal in the exercise folder:",
                 block("cd labs/01-get-started", "powershell")],
                ["Create the environment and install what you need:",
                 block(SETUP, "powershell")],
                ["Sign in to Azure. Use the tenant your instructor gave you:",
                 block("az login --tenant YOUR-TENANT-ID\naz account show --query tenantId -o tsv",
                       "powershell"),
                 {"tip": "That second command prints the tenant you are *actually* signed in to. If it does "
                         "not match what you expected, fix it now — otherwise you will get a confusing 401 "
                         "in a few minutes."}],
                ["Open `.env` and fill in your two values:",
                 block("PROJECT_ENDPOINT=https://YOUR-RESOURCE.services.ai.azure.com/api/projects/YOUR-PROJECT\n"
                       "MODEL_DEPLOYMENT=YOUR-CHAT-DEPLOYMENT", "text"),
                 {"bullets": [
                     "`PROJECT_ENDPOINT` — copy it from your project's home page in the Foundry portal. "
                     "It ends with `/api/projects/<something>`.",
                     "`MODEL_DEPLOYMENT` — the name of the **deployment**, which is often not the same as "
                     "the model's name in the catalogue. You will confirm it in the next task.",
                 ]},
                 {"warn": "There is no API key in this file, and there will not be one in any exercise. "
                          "Everything uses your Entra sign-in."}],
            ],
        },
        {
            "h2": "Task 2: Connect, and see what you have",
            "intro": ["Create a new file called `hello_foundry.py` in this folder. You will add to it in "
                      "every task from here on."],
            "steps": [
                ["Paste this in to start the file:",
                 block('"""Get started with Microsoft Foundry."""\n\n'
                       "import os\n\n"
                       "from azure.ai.projects import AIProjectClient\n"
                       "from azure.identity import DefaultAzureCredential\n"
                       "from dotenv import load_dotenv\n\n"
                       "load_dotenv()\n\n"
                       'MODEL = os.environ["MODEL_DEPLOYMENT"]'),
                 {"note": "`DefaultAzureCredential` goes looking for an identity. On your laptop it finds "
                          "your `az login` session. When this same code runs in Azure later (Exercise 13) it "
                          "finds the app's managed identity instead. You do not change the code."}],
                ["Now add a function that lists your deployments. Put it at the bottom of the file:",
                 block(task("01-get-started", "hello_foundry.py", 2))],
                ["And add this at the very bottom, to actually run it:",
                 block('if __name__ == "__main__":\n'
                       "    project = AIProjectClient(\n"
                       '        endpoint=os.environ["PROJECT_ENDPOINT"],\n'
                       "        credential=DefaultAzureCredential(),\n"
                       "    )\n\n"
                       "    show_deployments(project)")],
                ["Run it:",
                 block("python hello_foundry.py", "powershell"),
                 {"ok": "You should see a list of deployment names. **Check that the name you put in "
                        "`MODEL_DEPLOYMENT` is in that list**, spelled exactly the same way. This is the "
                        "single most common cause of a 404 later."},
                 {"whole_file": upto("01-get-started", "hello_foundry.py", 2,
                                     '    project = AIProjectClient(\n'
                                     '        endpoint=os.environ["PROJECT_ENDPOINT"],\n'
                                     '        credential=DefaultAzureCredential(),\n'
                                     '    )\n\n'
                                     '    show_deployments(project)'),
                  "name": "hello_foundry.py"}],
                ["If you got an error instead, find it here:",
                 {"table": (["What you saw", "What it means"], [
                     ["`KeyError: 'PROJECT_ENDPOINT'`", "You did not copy `.env.example` to `.env`, or you "
                                                        "are running from the wrong folder."],
                     ["`CredentialUnavailableError` or 401", "Not signed in, or signed in to the wrong "
                                                             "tenant. Run `az login --tenant ...` again."],
                     ["403 Forbidden", "You are signed in, but your account does not have a role on this "
                                       "project. Ask your instructor."],
                     ["An empty list", "The project has no model deployed yet."],
                 ])}],
            ],
        },
        {
            "h2": "Task 3: Ask a question",
            "steps": [
                ["Add this function to the bottom of the file:",
                 block(task("01-get-started", "hello_foundry.py", 3)),
                 {"bullets": [
                     "`instructions` is the standing brief — who the assistant is and how it should behave.",
                     "`input` is the actual question.",
                     "`output_text` is the answer as a plain string.",
                 ]}],
                ["Your main block needs two changes — get an OpenAI-compatible client, and call the new "
                 "function. Replace the whole `if __name__` block with this:",
                 block('if __name__ == "__main__":\n'
                       "    project = AIProjectClient(\n"
                       '        endpoint=os.environ["PROJECT_ENDPOINT"],\n'
                       "        credential=DefaultAzureCredential(),\n"
                       "    )\n"
                       "    client = project.get_openai_client()\n\n"
                       "    show_deployments(project)\n"
                       "    ask_one_question(client)")],
                ["Run it again:",
                 block("python hello_foundry.py", "powershell"),
                 {"ok": "A short paragraph of advice about a missed bin collection."}],
                ["**Try changing something.** Edit the `instructions` to say "
                 "`\"Answer like a pirate.\"` and run it again. Then put it back.",
                 {"note": "That is the whole idea of instructions: the question stayed the same, the "
                          "behaviour changed. Exercise 03 turns instructions into a versioned, saved thing "
                          "rather than a string in your file."}],
                [{"whole_file": upto("01-get-started", "hello_foundry.py", 3,
                                     '    project = AIProjectClient(\n'
                                     '        endpoint=os.environ["PROJECT_ENDPOINT"],\n'
                                     '        credential=DefaultAzureCredential(),\n'
                                     '    )\n'
                                     '    client = project.get_openai_client()\n\n'
                                     '    show_deployments(project)\n'
                                     '    ask_one_question(client)'),
                  "name": "hello_foundry.py"}],
            ],
        },
        {
            "h2": "Task 4: Have a conversation",
            "intro": [
                "Ask the model two questions and it will not remember the first one. It has no memory at "
                "all. Anything it appears to remember is something you sent it again.",
                "A **conversation** is a server-side object that does that for you.",
            ],
            "steps": [
                ["Add this function:",
                 block(task("01-get-started", "hello_foundry.py", 4))],
                ["Add the call to your main block, after `ask_one_question(client)`:",
                 block("    have_a_conversation(client)")],
                ["Run it:",
                 block("python hello_foundry.py", "powershell"),
                 {"ok": "The second answer should mention **ACME-204**, even though the second question "
                        "never says it."}],
                ["**Now prove where that memory lives.** Delete `conversation=conversation.id,` from the "
                 "`client.responses.create(...)` call and run again.",
                 {"ok": "The second answer can no longer tell you the case reference. Put the line back."},
                 {"note": "This is worth two minutes of your time. The model is stateless. The conversation "
                          "object is what carries the context — which is exactly why Exercise 08 has to "
                          "make a real decision about where conversation state is kept in a production app."}],
                [{"whole_file": upto("01-get-started", "hello_foundry.py", 4,
                                     '    project = AIProjectClient(\n'
                                     '        endpoint=os.environ["PROJECT_ENDPOINT"],\n'
                                     '        credential=DefaultAzureCredential(),\n'
                                     '    )\n'
                                     '    client = project.get_openai_client()\n\n'
                                     '    show_deployments(project)\n'
                                     '    ask_one_question(client)\n'
                                     '    have_a_conversation(client)'),
                  "name": "hello_foundry.py"}],
            ],
        },
        {
            "h2": "Task 5: Stream the answer",
            "intro": ["Waiting for a long answer to appear all at once feels broken. Streaming sends it in "
                      "pieces as it is written."],
            "steps": [
                ["Add the last function:",
                 block(task("01-get-started", "hello_foundry.py", 5))],
                ["Add the call to your main block:",
                 block("    stream_an_answer(client)")],
                ["Run it and watch the text appear:",
                 block("python hello_foundry.py", "powershell")],
                ["**Have a look at what else is in that stream.** Temporarily change the `if` line to print "
                 "every event type instead:",
                 block("        print(event.type)"),
                 "Run it, see the sequence of events, then put the original line back.",
                 {"note": "You have just seen the raw shape of a stream: lifecycle events, many small text "
                          "deltas, then a completion event. Exercise 13 forwards these same deltas to a "
                          "browser, and uses the completion event to know the answer actually finished "
                          "rather than the connection dropping."}],
                ["That is the finished file:",
                 whole("01-get-started", "hello_foundry.py")],
            ],
        },
    ],
    "knowledge_check": [
        {"q": "What signs you in, in this exercise?",
         "options": ["A. An API key in `.env`", "B. Your Entra ID sign-in, via `DefaultAzureCredential`",
                     "C. The project endpoint URL"],
         "answer": "B",
         "why": "The same line finds your `az login` session on a laptop and a managed identity in Azure, "
                "so the code does not change when you deploy it."},
        {"q": "The second question got the case reference right. Why?",
         "options": ["A. The model remembered it", "B. It was in the instructions",
                     "C. Both requests used the same conversation"],
         "answer": "C",
         "why": "You proved this by removing the `conversation` argument and watching the memory disappear. "
                "The model itself is stateless."},
        {"q": "Which event carries the pieces of text when streaming?",
         "options": ["A. `response.output_text.delta`", "B. `conversation.created`", "C. `response.done`"],
         "answer": "A",
         "why": "The others tell you about the lifecycle. Only the delta events carry words."},
    ],
    "summary": [
        "You connected to Foundry with your own identity, checked which models you can actually use, asked "
        "a question, held a conversation, and streamed an answer.",
        "More usefully, you proved to yourself that the model has no memory — the conversation object does. "
        "Keep `hello_foundry.py`; Exercise 02 starts from the same four lines of setup.",
    ],
    "cleanup": [
        "This exercise creates one thing in Azure: the conversation in Task 4. It is small and it will age "
        "out, but you can leave nothing behind by adding `store=False` to the calls that do not need to be "
        "kept.",
        "Nothing else to do. Your virtual environment and `.env` stay on your machine — and `.env` should "
        "never be committed to source control.",
    ],
    "refs": [
        ("Foundry SDK overview", "https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview"),
        ("Responses API", "https://learn.microsoft.com/azure/foundry/agents/quickstarts/responses-api"),
    ],
}


# ============================================================================
LAB02 = {
    "num": "02",
    "slug": "02-choose-a-model",
    "short": "Choose a model",
    "group": "Day 1 — Foundations and your first agent",
    "track": "Foundations",
    "module_tags": ["Module 1", "Module 2"],
    "title": "Choose a model, and know what it costs",
    "minutes": 75,
    "lab_path": "labs/02-choose-a-model",
    "env_note": "adds `openai` for the embeddings client",
    "blurb": "Measure two models on the same question, compare embedding sizes, work out the bill, and send "
             "a picture.",
    "intro": [
        "\"Which model should we use?\" is usually answered by reading a table. This exercise answers it by "
        "measuring, because the thing that matters most is not in any table: **does the model admit when it "
        "does not know?**",
        "You will also meet embeddings, which are the foundation of everything in Day 2.",
    ],
    "objectives": [
        "Run the same question through two models and compare speed, tokens and honesty.",
        "Turn text into vectors, and see what changing the vector size costs you.",
        "Work out the money from the measured token counts.",
        "Send an image to a model that can see.",
    ],
    "prereqs": [
        "Exercise 01 finished.",
        "**Two** chat deployments in your project — ideally a small one and a larger one.",
        "A vision-capable deployment.",
        "An Azure OpenAI resource with `text-embedding-3-small` deployed, and **Cognitive Services OpenAI "
        "User** on it.",
    ],
    "sections": [
        {
            "h2": "Task 1: Set up",
            "steps": [
                [block("cd labs/02-choose-a-model\n" + SETUP, "powershell")],
                ["Fill in `.env`:",
                 block("PROJECT_ENDPOINT=https://YOUR-RESOURCE.services.ai.azure.com/api/projects/YOUR-PROJECT\n"
                       "MODEL_DEPLOYMENTS=YOUR-SMALL-DEPLOYMENT,YOUR-LARGER-DEPLOYMENT\n"
                       "VISION_DEPLOYMENT=YOUR-VISION-DEPLOYMENT\n"
                       "AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE.openai.azure.com\n"
                       "EMBEDDING_DEPLOYMENT=text-embedding-3-small", "text"),
                 {"warn": "`AZURE_OPENAI_ENDPOINT` is the **Azure OpenAI resource** URL. It is not the same "
                          "as `PROJECT_ENDPOINT`. Mixing these two up is the most common setup mistake in "
                          "this workshop, and it will come back in Exercise 05."},
                 {"tip": "`MODEL_DEPLOYMENTS` is plural and comma-separated — two deployment names, no spaces."}],
                ["Create a file called `choose_a_model.py` and start it with this:",
                 block('"""Choose a model."""\n\n'
                       "import base64\nimport json\nimport math\nimport os\nimport time\n\n"
                       "from azure.ai.projects import AIProjectClient\n"
                       "from azure.identity import DefaultAzureCredential, get_bearer_token_provider\n"
                       "from dotenv import load_dotenv\n"
                       "from openai import OpenAI\n\n"
                       "load_dotenv()\n\n"
                       "COUNCIL_FACTS = (\n"
                       '    "Council facts: the library opens at 9 am on weekdays. "\n'
                       '    "Waste pickup days vary by address."\n'
                       ")\n"
                       'RESIDENT_QUESTION = "When does the library open, and when is my bin collected?"'),
                 {"note": "Read those two facts carefully. The library time **is** there. The bin day **is "
                          "not**. That is deliberate."}],
            ],
        },
        {
            "h2": "Task 2: Compare two models",
            "steps": [
                ["Add this function:",
                 block(task("02-choose-a-model", "choose_a_model.py", 2))],
                ["Add a main block at the bottom:",
                 block('if __name__ == "__main__":\n'
                       "    credential = DefaultAzureCredential()\n"
                       "    project = AIProjectClient(\n"
                       '        endpoint=os.environ["PROJECT_ENDPOINT"],\n'
                       "        credential=credential,\n"
                       "    )\n"
                       "    client = project.get_openai_client()\n\n"
                       "    results = compare_two_models(client)")],
                [block("python choose_a_model.py", "powershell")],
                ["Now mark each answer yourself, on three things:",
                 {"bullets": [
                     "Did it get the **library time** right? (9 am — it is in the facts.)",
                     "Did it **admit it does not know** the bin day? Or did it invent one?",
                     "How did the **time and token counts** compare?",
                 ]},
                 {"ok": "A model that invents a bin collection day has failed, no matter how fast or fluent "
                        "it was. For resident enquiries that single behaviour matters more than anything "
                        "else you can measure."}],
                ["**Run it three times.**",
                 {"warn": "One timing is not a measurement. Watch how much the seconds move between runs "
                          "before you quote a number to anyone."}],
                [{"whole_file": upto("02-choose-a-model", "choose_a_model.py", 2,
                                     "    credential = DefaultAzureCredential()\n"
                                     "    project = AIProjectClient(\n"
                                     '        endpoint=os.environ["PROJECT_ENDPOINT"],\n'
                                     "        credential=credential,\n"
                                     "    )\n"
                                     "    client = project.get_openai_client()\n\n"
                                     "    results = compare_two_models(client)"),
                  "name": "choose_a_model.py"}],
            ],
        },
        {
            "h2": "Task 3: Embeddings",
            "intro": [
                "An embedding turns text into a list of numbers, positioned so that things which mean "
                "similar things end up near each other. That is what makes search-by-meaning possible, and "
                "it is the foundation of every exercise on Day 2.",
            ],
            "steps": [
                ["Add these two functions:",
                 block(task("02-choose-a-model", "choose_a_model.py", 3))],
                ["The embeddings live on the Azure OpenAI resource, so you need a second client. Add this to "
                 "your main block, before the call:",
                 block("    token_provider = get_bearer_token_provider(\n"
                       '        credential, "https://cognitiveservices.azure.com/.default"\n'
                       "    )\n"
                       "    embeddings_client = OpenAI(\n"
                       '        base_url=os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/") + "/openai/v1/",\n'
                       "        api_key=token_provider,\n"
                       "    )\n\n"
                       "    compare_embedding_sizes(embeddings_client)"),
                 {"note": "`api_key=token_provider` looks alarming but it is not a key — it is a **function** "
                          "that fetches a fresh Entra token whenever one is needed."}],
                [block("python choose_a_model.py", "powershell")],
                ["Look at what you got back for each size:",
                 {"table": (["Dimensions", "Bytes per vector", "For one million chunks"], [
                     ["256", "1,024", "about 1 GB"],
                     ["1536", "6,144", "about 6 GB"],
                 ])},
                 "Then check whether the **ranking actually changed** between the two sizes.",
                 {"warn": "If the ranking is the same, that tells you something about these three short "
                          "sentences — not about your documents. Measure on real data before deciding to "
                          "shrink your vectors."}],
                ["One rule to take away, because breaking it causes silent nonsense:",
                 {"warn": "The vectors you **store** and the vectors you **search with** must come from the "
                          "same model at the same size. Changing either means rebuilding the whole index. "
                          "It is not a config change."}],
                [{"whole_file": upto("02-choose-a-model", "choose_a_model.py", 3,
                                     "    credential = DefaultAzureCredential()\n"
                                     "    project = AIProjectClient(\n"
                                     '        endpoint=os.environ["PROJECT_ENDPOINT"],\n'
                                     "        credential=credential,\n"
                                     "    )\n"
                                     "    client = project.get_openai_client()\n\n"
                                     "    token_provider = get_bearer_token_provider(\n"
                                     '        credential, "https://cognitiveservices.azure.com/.default"\n'
                                     "    )\n"
                                     "    embeddings_client = OpenAI(\n"
                                     '        base_url=os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/") '
                                     '+ "/openai/v1/",\n'
                                     "        api_key=token_provider,\n"
                                     "    )\n\n"
                                     "    results = compare_two_models(client)\n"
                                     "    compare_embedding_sizes(embeddings_client)"),
                  "name": "choose_a_model.py"}],
            ],
        },
        {
            "h2": "Task 4: What does it cost?",
            "steps": [
                ["Add this:",
                 block(task("02-choose-a-model", "choose_a_model.py", 4))],
                ["And call it, using the token counts you actually measured in Task 2:",
                 block("    estimate_cost(results, price_per_million_input=1.0,\n"
                       "                  price_per_million_output=2.0, requests=1000)")],
                [block("python choose_a_model.py", "powershell")],
                ["**Now replace those two rates with the real ones** for the model you measured, and write "
                 "down the date and where you got them.",
                 {"warn": "The script applies one pair of rates to both models. If your two deployments "
                          "have different prices — and they usually do — run it once per model. Comparing "
                          "two models using one model's price is worse than not comparing at all."}],
                ["Model tokens are only part of the bill. Add these to your estimate:",
                 {"bullets": [
                     "Azure AI Search tier, replicas and partitions (Exercises 05–07, 11, 13).",
                     "Storage for the original documents.",
                     "Cosmos DB throughput (Exercise 08).",
                     "Hosting (Exercise 13).",
                     "**The judge calls in Exercise 11** — evaluation costs roughly as much as serving.",
                     "Telemetry ingestion and retention (Exercise 12).",
                 ]}],
            ],
        },
        {
            "h2": "Task 5: Send a picture",
            "steps": [
                ["Open `policy-page.png` and read the leave table yourself first, so you know the right "
                 "answer before the model gives you one."],
                ["Add the last function:",
                 block(task("02-choose-a-model", "choose_a_model.py", 5))],
                ["Call it:",
                 block("    read_a_picture(client)")],
                [block("python choose_a_model.py", "powershell"),
                 "Check both numbers against the image. Did it get the page number right?"],
                ["You now know two ways to read a document. They are for different jobs:",
                 {"table": (["", "Vision model (this task)", "Extraction + search (Exercise 04 onward)"], [
                     ["What you get", "A generated description, which may paraphrase or err",
                      "The actual text, with page numbers"],
                     ["Citations", "Whatever the model says", "Real, checkable page references"],
                     ["Scale", "One picture per request", "Thousands of documents, indexed and kept current"],
                     ["Good for", "Charts, layout questions, ad-hoc reading", "A searchable, citable record set"],
                 ])},
                 {"note": "For a council's records and enquiries, extraction plus search is almost always "
                          "the right answer. Vision complements it — it does not replace it."}],
                ["The finished file:",
                 whole("02-choose-a-model", "choose_a_model.py")],
            ],
        },
    ],
    "knowledge_check": [
        {"q": "One model answered faster and sounded better, but invented a bin collection day. Is it the "
              "better choice for resident enquiries?",
         "options": ["A. Yes — speed and fluency matter most", "B. No — inventing facts disqualifies it",
                     "C. It depends on the price"],
         "answer": "B",
         "why": "A confident wrong answer to a resident is worse than a slow correct one. This is the "
                "measurement most model comparisons leave out."},
        {"q": "What must match between the vectors you store and the vectors you search with?",
         "options": ["A. The model and the number of dimensions", "B. Just the file names",
                     "C. Just the region"],
         "answer": "A",
         "why": "Vectors from different models are not comparable. Changing either means a full rebuild."},
        {"q": "You halve your embedding dimensions from 1536 to 256. What definitely changes?",
         "options": ["A. Retrieval quality gets worse", "B. Storage drops to about a sixth",
                     "C. Nothing measurable"],
         "answer": "B",
         "why": "The storage saving is arithmetic and certain. Whether quality suffers depends entirely on "
                "your data, which is why you measure it rather than assume."},
    ],
    "summary": [
        "You measured two models on one question — including whether each admits what it does not know — "
        "compared embedding sizes on both ranking and storage, turned measured tokens into money, and sent "
        "an image to a model.",
        "The habit worth keeping is the one in Task 2: decide what \"good\" means *before* you look at the "
        "output, then mark against it.",
    ],
    "cleanup": [
        "Nothing was created in Azure. Delete the local files if you want:",
        block("Remove-Item model-results.json, embedding-results.json "
              "-ErrorAction SilentlyContinue", "powershell"),
    ],
    "refs": [
        ("Embeddings", "https://learn.microsoft.com/azure/ai-foundry/openai/how-to/embeddings"),
        ("Deployment types", "https://learn.microsoft.com/azure/ai-foundry/openai/how-to/deployment-types"),
        ("Azure pricing calculator", "https://azure.microsoft.com/pricing/calculator/"),
    ],
}


# ============================================================================
LAB03 = {
    "num": "03",
    "slug": "03-first-agent",
    "short": "Build your first agent",
    "group": "Day 1 — Foundations and your first agent",
    "track": "Foundations",
    "module_tags": ["Module 3", "Module 6"],
    "title": "Build your first agent, and give it tools",
    "minutes": 90,
    "lab_path": "labs/03-first-agent",
    "env_note": "same packages as Exercise 01",
    "blurb": "Save an agent in your project, publish two versions, then let it look things up instead of "
             "guessing.",
    "intro": [
        "So far your instructions lived in a string in a Python file. An **agent** is that same idea, saved "
        "in your project with a name and a version number.",
        "Then comes the part that makes agents genuinely useful: **tools**. You give the model a list of "
        "things it is allowed to ask for, and when it asks, *your code* decides whether to do it. The model "
        "never runs anything itself — and understanding exactly where that line sits is the most important "
        "thing in this exercise.",
    ],
    "objectives": [
        "Create a named agent and publish two versions of it.",
        "See that an old version is still there, unchanged.",
        "Call the agent without repeating the model or instructions.",
        "Describe two Python functions to the model as tools.",
        "Run the tool loop by hand, so you can see every step of it.",
    ],
    "prereqs": [
        "Exercise 01 finished.",
        "A project role that lets you create agents.",
    ],
    "sections": [
        {
            "h2": "Task 1: Set up",
            "steps": [
                [block("cd labs/03-first-agent\n" + SETUP, "powershell")],
                ["Fill in `.env`. **Put your own initials in `YOUR_INITIALS`** so your agent does not collide "
                 "with anyone else's in a shared project:",
                 block("PROJECT_ENDPOINT=https://YOUR-RESOURCE.services.ai.azure.com/api/projects/YOUR-PROJECT\n"
                       "MODEL_DEPLOYMENT=YOUR-CHAT-DEPLOYMENT\n"
                       "YOUR_INITIALS=xx", "text")],
                ["Open `orders.json` and look at one record. Twenty-five synthetic orders, each with an "
                 "id, a customer, a status and a total. No real people."],
                ["Create `my_agent.py` and start it:",
                 block('"""My first agent."""\n\n'
                       "import json\nimport os\n\n"
                       "from azure.ai.projects import AIProjectClient\n"
                       "from azure.ai.projects.models import FunctionTool, PromptAgentDefinition\n"
                       "from azure.identity import DefaultAzureCredential\n"
                       "from dotenv import load_dotenv\n\n"
                       "load_dotenv()\n\n"
                       'MODEL = os.environ["MODEL_DEPLOYMENT"]\n'
                       'AGENT_NAME = "acme-agent-" + os.environ.get("YOUR_INITIALS", "xx")')],
            ],
        },
        {
            "h2": "Task 2: Create an agent, twice",
            "steps": [
                ["Add this:",
                 block(task("03-first-agent", "my_agent.py", 2))],
                ["Add a main block:",
                 block('if __name__ == "__main__":\n'
                       "    project = AIProjectClient(\n"
                       '        endpoint=os.environ["PROJECT_ENDPOINT"],\n'
                       "        credential=DefaultAzureCredential(),\n"
                       "    )\n\n"
                       "    create_two_versions(project)")],
                [block("python my_agent.py", "powershell"),
                 {"ok": "Two version numbers created, then a list showing both."}],
                ["**Run it again.**",
                 {"ok": "You now have four versions, not two. Versions accumulate — creating one never "
                        "changes or replaces an old one."},
                 {"note": "This matters more than it looks. In Exercise 11 you build a release gate that "
                          "ties test evidence to a specific version. That is only meaningful if the thing "
                          "you tested cannot quietly change afterwards."}],
                [{"whole_file": upto("03-first-agent", "my_agent.py", 2,
                                     "    project = AIProjectClient(\n"
                                     '        endpoint=os.environ["PROJECT_ENDPOINT"],\n'
                                     "        credential=DefaultAzureCredential(),\n"
                                     "    )\n\n"
                                     "    create_two_versions(project)"),
                  "name": "my_agent.py"}],
            ],
        },
        {
            "h2": "Task 3: Talk to it by name",
            "steps": [
                ["Add this:",
                 block(task("03-first-agent", "my_agent.py", 3))],
                ["Call it:",
                 block("    ask_the_agent(project)")],
                [block("python my_agent.py", "powershell")],
                ["Look carefully at what is **missing** from that `responses.create(...)` call: there is no "
                 "`model=` and no `instructions=`.",
                 {"note": "Both come from the saved agent. Compare it with Exercise 01, where you passed "
                          "them on every single request. That is the difference between an agent and a "
                          "plain model call."}],
            ],
        },
        {
            "h2": "Task 4: Write the tools",
            "intro": [
                "Two ordinary Python functions, and then a description of each one for the model.",
                "The description is all the model ever sees. It never receives your code.",
            ],
            "steps": [
                ["Add the functions and their descriptions:",
                 block(task("03-first-agent", "my_agent.py", 4))],
                ["Three things in there are worth pausing on:",
                 {"bullets": [
                     "`FunctionTool` describes the **name, purpose and arguments** — nothing else.",
                     "`strict=True` with `additionalProperties: False` means the model must send exactly "
                     "the arguments you declared, and nothing extra.",
                     "`AVAILABLE_TOOLS` is **your own list of what you are willing to run**. If the model "
                     "asks for something not in that dictionary, it simply does not happen.",
                 ]},
                 {"warn": "That last point is the security boundary of the whole exercise. Never dispatch a "
                          "function by name straight from model output without checking it against a list "
                          "you control."}],
            ],
        },
        {
            "h2": "Task 5: Run the tool loop",
            "steps": [
                ["Add these two functions:",
                 block(task("03-first-agent", "my_agent.py", 5))],
                ["Update your main block to call them:",
                 block("    version_with_tools = add_tools_to_the_agent(project)\n"
                       "    run_the_tool_loop(project, version_with_tools)")],
                [block("python my_agent.py", "powershell"),
                 {"ok": "You should see `model asked for: find_orders_for_customer({...})` and then "
                        "`get_order_status({...})`, followed by an answer built from the real data."}],
                ["Follow what just happened, because this loop is the heart of every agent:",
                 {"bullets": [
                     "You asked a question. The model replied — not with an answer, but with a **request**: "
                     "*please run this function with these arguments*.",
                     "Your code looked the name up in `AVAILABLE_TOOLS` and ran the real Python.",
                     "You sent the result back, tagged with `call_id`.",
                     "The model used it, and possibly asked for another tool. The loop repeats until it stops "
                     "asking.",
                 ]},
                 {"note": "`call_id` is what ties a result to the request that asked for it. When the model "
                          "asks for three tools at once, nothing else is reliable — not the order, not the "
                          "function name."}],
                ["**Try breaking it, deliberately.** Change the question to ask about order `ORD-99999`, "
                 "which does not exist, and run again.",
                 {"ok": "The function returns `{'error': 'Order not found'}` and a good model tells you it "
                        "cannot find that order. A model that invents a status here would invent one in "
                        "production too."}],
                ["**Now break it the other way.** Delete `find_orders_for_customer` from the "
                 "`AVAILABLE_TOOLS` dictionary — but leave its description in `TOOL_SCHEMAS` — and run again.",
                 {"ok": "You get a `KeyError`. The model asked for a tool you were not prepared to run."},
                 "Put it back.",
                 {"note": "In a real service that is a case you handle deliberately rather than crash on. "
                          "Exercise 09 handles exactly this, by returning HTTP 403."}],
                ["The finished file:",
                 whole("03-first-agent", "my_agent.py")],
            ],
        },
        {
            "h2": "Task 6: Tidy up",
            "steps": [
                ["You created a real agent in the project. Remove it by uncommenting the last line in the "
                 "main block:",
                 block("    delete_the_agent(project)")],
                [block("python my_agent.py", "powershell"),
                 {"tip": "All those versions live under one agent name, so deleting the agent removes all "
                         "of them in one go. The function refuses to delete anything whose name does not "
                         "start with `acme-agent-`."}],
            ],
        },
    ],
    "knowledge_check": [
        {"q": "Who actually executes a tool function?",
         "options": ["A. The model", "B. Your application", "C. The Foundry service"],
         "answer": "B",
         "why": "The model only sends a request. Your code checks it against `AVAILABLE_TOOLS` and decides."},
        {"q": "What does the model receive about a tool?",
         "options": ["A. The Python source", "B. Its name, description and argument schema",
                     "C. Read access to your files"],
         "answer": "B",
         "why": "It sees the `FunctionTool` description and nothing more."},
        {"q": "You change an agent's instructions. What happens to the old version?",
         "options": ["A. It is overwritten", "B. It is deleted", "C. It stays exactly as it was"],
         "answer": "C",
         "why": "You saw four versions after running twice. Immutability is what makes evaluation evidence "
                "and rollback mean anything."},
    ],
    "summary": [
        "You created a named agent, published versions that accumulate rather than overwrite, called it "
        "without repeating the model or instructions, and ran the full tool loop by hand.",
        "The line you drew in Task 5 — model proposes, your application decides and executes — is the same "
        "line enforced with HTTP status codes in Exercise 09 and with a verified user identity in "
        "Exercise 13.",
    ],
    "cleanup": [
        "Run the file with `delete_the_agent(project)` uncommented, as in Task 6. It removes only the agent "
        "whose name starts with `acme-agent-`.",
        {"tip": "If you skip this, you leave a named agent in a shared project. It costs nothing, but the "
                "next class will thank you."},
    ],
    "refs": [
        ("Prompt agents", "https://learn.microsoft.com/azure/foundry/agents/quickstarts/prompt-agent"),
        ("Function calling", "https://learn.microsoft.com/azure/foundry/agents/how-to/tools/function-calling"),
    ],
}


# ============================================================================
LAB04 = {
    "num": "04",
    "slug": "04-prepare-documents",
    "short": "Prepare documents",
    "group": "Day 2 — Retrieval and grounding",
    "track": "RAG",
    "module_tags": ["Module 4"],
    "title": "Turn documents into something searchable",
    "minutes": 75,
    "lab_path": "labs/04-prepare-documents",
    "env_note": "adds `azure-ai-documentintelligence`",
    "blurb": "Extract three policy PDFs, compare two ways of cutting them up, and label every piece with "
             "where it came from and who may read it.",
    "intro": [
        "This is the first step of the pipeline that answers resident enquiries from real documents — the "
        "thing this workshop is mostly about.",
        "The API call is three lines. The interesting decisions are everything around it: keeping tables "
        "intact, keeping page numbers so answers can be checked, and deciding where to cut a document into "
        "pieces.",
    ],
    "objectives": [
        "Extract a PDF as Markdown, with its tables still tables.",
        "Keep the page number attached to every piece of text.",
        "Compare fixed-width chunking with paragraph-aware chunking, and see what each breaks.",
        "Label every chunk with who is allowed to read it.",
    ],
    "prereqs": [
        "An **Azure AI Document Intelligence** resource, with **Cognitive Services User** on it.",
        "Python 3.11 and the Azure CLI signed in.",
    ],
    "before_extra": [
        {"note": "This exercise needs no Foundry project and no chat model. Its `.env` has one line in it."},
    ],
    "sections": [
        {
            "h2": "Task 1: Set up",
            "steps": [
                [block("cd labs/04-prepare-documents\n" + SETUP, "powershell")],
                ["Fill in the one value:",
                 block("DOCUMENT_INTELLIGENCE_ENDPOINT=https://YOUR-DI.cognitiveservices.azure.com", "text")],
                ["**Open the three PDFs in `benefits/` and read them.** They are short. You cannot tell "
                 "whether extraction worked if you do not know what was in there.",
                 {"tip": "Pay attention to the table in the leave policy. You will watch what happens to it."}],
                ["Create `prepare_documents.py`:",
                 block('"""Prepare documents for search."""\n\n'
                       "import json\nimport os\nfrom pathlib import Path\n\n"
                       "from azure.ai.documentintelligence import DocumentIntelligenceClient\n"
                       "from azure.identity import DefaultAzureCredential\n"
                       "from dotenv import load_dotenv\n\n"
                       "load_dotenv()\n\n"
                       'PDF_FOLDER = Path("benefits")')],
            ],
        },
        {
            "h2": "Task 2: Extract a PDF",
            "steps": [
                ["Add this:",
                 block(task("04-prepare-documents", "prepare_documents.py", 2))],
                ["Add a main block:",
                 block('if __name__ == "__main__":\n'
                       "    client = DocumentIntelligenceClient(\n"
                       '        os.environ["DOCUMENT_INTELLIGENCE_ENDPOINT"],\n'
                       "        DefaultAzureCredential(),\n"
                       "    )\n\n"
                       '    print("=== Extracting PDFs ===")\n'
                       "    pages = extract_one_pdf(client, sorted(PDF_FOLDER.glob(\"*.pdf\"))[0])")],
                [block("python prepare_documents.py", "powershell")],
                ["**Open the `.md` file it just wrote, next to the original PDF.** Check two things:",
                 {"bullets": [
                     "Did the headings become Markdown headings?",
                     "Did the leave table survive as a table, with its rows lined up?",
                 ]},
                 {"note": "That is what `output_content_format='markdown'` bought you. Plain text extraction "
                          "would have flattened the table into a jumble of loose words, and an answer quoting "
                          "it would have been wrong in a way that is very hard to spot."}],
                ["The other important part is this loop:",
                 block("    for page in result.pages:\n"
                       "        page_text = \"\"\n"
                       "        for span in page.spans:\n"
                       "            page_text += result.content[span.offset:span.offset + span.length]\n"
                       "        pages.append((page.page_number, page_text))"),
                 "Every piece of text stays tied to the page it came from. Without that, an assistant can "
                 "tell a resident something but cannot show them where it says so."],
                [{"whole_file": upto("04-prepare-documents", "prepare_documents.py", 2,
                                     "    client = DocumentIntelligenceClient(\n"
                                     '        os.environ["DOCUMENT_INTELLIGENCE_ENDPOINT"],\n'
                                     "        DefaultAzureCredential(),\n"
                                     "    )\n\n"
                                     '    print("=== Extracting PDFs ===")\n'
                                     '    pages = extract_one_pdf(client, sorted(PDF_FOLDER.glob("*.pdf"))[0])'),
                  "name": "prepare_documents.py"}],
            ],
        },
        {
            "h2": "Task 3: Cut it into pieces",
            "intro": [
                "A whole policy is too big to hand to a model for one question. You cut it into chunks — and "
                "**where you cut matters a great deal**.",
            ],
            "steps": [
                ["Add all three functions:",
                 block(task("04-prepare-documents", "prepare_documents.py", 3))],
                ["Call the comparison:",
                 block("    compare_the_two_strategies(pages)")],
                [block("python prepare_documents.py", "powershell")],
                ["Look at where the fixed-width chunker cut. Does the first chunk end mid-sentence? "
                 "Mid-word?",
                 {"table": (["", "Fixed width", "By paragraph"], [
                     ["How it cuts", "Every 650 characters, regardless of content",
                      "At paragraph breaks, packing up to a target size"],
                     ["Overlap", "150 characters, so a split sentence survives in one piece",
                      "None needed — it does not split sentences"],
                     ["Risk", "Cuts through tables and sentences",
                      "A single huge paragraph can exceed the target"],
                     ["Good for", "Uniform prose", "Structured documents like policies"],
                 ])}],
                ["Work out the overlap arithmetic for yourself: window 800, step `800 - 150 = 650`, so "
                 "consecutive chunks share **150 characters**.",
                 {"note": "These are *characters*, not tokens or sentences. It is the simplest thing that "
                          "works, and it is worth knowing it is simple. Neither strategy here understands "
                          "headings — a real improvement would carry the current section title into every "
                          "chunk, which usually helps a policy corpus more than tuning the window size."}],
            ],
        },
        {
            "h2": "Task 4: Label every chunk",
            "intro": [
                "A chunk of text on its own is not much use. It needs to know where it came from and who is "
                "allowed to see it.",
            ],
            "steps": [
                ["Add these two functions:",
                 block(task("04-prepare-documents", "prepare_documents.py", 4))],
                ["Replace your main block with this:",
                 block('if __name__ == "__main__":\n'
                       "    client = DocumentIntelligenceClient(\n"
                       '        os.environ["DOCUMENT_INTELLIGENCE_ENDPOINT"],\n'
                       "        DefaultAzureCredential(),\n"
                       "    )\n\n"
                       '    print("=== Extracting PDFs ===")\n'
                       '    pages = extract_one_pdf(client, sorted(PDF_FOLDER.glob("*.pdf"))[0])\n\n'
                       "    compare_the_two_strategies(pages)\n"
                       '    build_chunk_records(client, strategy="paragraph")')],
                [block("python prepare_documents.py", "powershell")],
                ["**Open `chunks.json`.** Every record has five fields, and each one is there for a "
                 "reason:",
                 {"table": (["Field", "Why it exists"], [
                     ["`id`", "Stable — same document, page and position always gives the same id. "
                              "Exercise 07 depends on this."],
                     ["`content`", "The text a model will actually read."],
                     ["`source` and `page`", "So an answer can cite something checkable."],
                     ["`allowed_groups`", "So Exercise 06 can show different people different things."],
                 ])}],
                ["Notice where the access decision was made — at extraction time, in `who_can_see_this`. "
                 "The leave policy is HR-only; the rest are shared.",
                 {"note": "This is the moment access control begins. Exercise 06 enforces these exact labels "
                          "at query time. Get them wrong here and no amount of filtering later will fix it."}],
                ["The finished file:",
                 whole("04-prepare-documents", "prepare_documents.py")],
            ],
        },
    ],
    "knowledge_check": [
        {"q": "Why ask for Markdown output rather than plain text?",
         "options": ["A. It is smaller", "B. Tables stay tables instead of becoming loose words",
                     "C. It is required by the API"],
         "answer": "B",
         "why": "A flattened table can produce an answer that is confidently wrong and hard to catch."},
        {"q": "Why keep the page number on every chunk?",
         "options": ["A. For billing", "B. For authentication", "C. So an answer can cite a checkable source"],
         "answer": "C",
         "why": "A resident-facing answer that cannot be traced back to a document is very hard to defend."},
        {"q": "What is the risk of fixed-width chunking?",
         "options": ["A. It is slower", "B. It can cut through a sentence or a table",
                     "C. It cannot handle PDFs"],
         "answer": "B",
         "why": "Half a table retrieved as evidence is worse than no table, because it looks authoritative."},
    ],
    "summary": [
        "You extracted three policies as Markdown with their tables intact, kept every page number, compared "
        "two chunking strategies on real text, and labelled each chunk with its source and its audience.",
        "`chunks.json` is the input to the next three exercises. Keep it.",
    ],
    "cleanup": [
        "Nothing was created in Azure — Document Intelligence just read your files and charged you for the "
        "pages.",
        "Keep `chunks.json`. Exercise 05 needs it.",
    ],
    "refs": [
        ("Document Intelligence layout model",
         "https://learn.microsoft.com/azure/ai-services/document-intelligence/prebuilt/layout?view=doc-intel-4.0.0"),
        ("Chunking guidance", "https://learn.microsoft.com/azure/search/vector-search-how-to-chunk-documents"),
    ],
}

LABS = [LAB01, LAB02, LAB03, LAB04]
