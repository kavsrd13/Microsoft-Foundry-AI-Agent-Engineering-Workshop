"""Exercise 15 — Host a tool on Azure Functions, queue-based.

Every expected output on this page was observed on a live run in Australia East
on 12 September 2026. The message shape, the timings, the identity problem and
its fix are all things that actually happened, not things the Learn page says
should happen.
"""

from ._code import block, task, upto, whole
from .labs_01_04 import SETUP

LAB = "15-azure-functions-tool"
SCRIPT = "ask_the_agent.py"

MAIN_AFTER_2 = (
    "    import json\n"
    '    print(json.dumps(describe_the_tool().as_dict(), indent=2))'
)
MAIN_AFTER_3 = (
    "    project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=DefaultAzureCredential())\n\n"
    "    agent = create_the_agent(project)"
)
MAIN_AFTER_4 = (
    "    project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=DefaultAzureCredential())\n"
    "    client = project.get_openai_client()\n\n"
    "    agent = create_the_agent(project)\n"
    '    ask(client, agent, "What is the weather like in Sydney right now?")\n'
    '    ask(client, agent, "And in Melbourne?")'
)

LAB15 = {
    "num": "15",
    "slug": "15-azure-functions-tool",
    "short": "A tool hosted on Azure Functions",
    "group": "Day 3 — Memory, tools and orchestration",
    "track": "Platform",
    "module_tags": ["Module 6", "Module 7"],
    "title": "Host an agent tool on Azure Functions, connected by queues",
    "minutes": 120,
    "lab_path": "labs/15-azure-functions-tool",
    "env_note": "`azd` provisions everything; `azure-ai-projects==2.6.0` for the agent script",
    "blurb": "Provision a standard-setup Foundry project, deploy a queue-triggered Function, and have an "
             "agent call it as a tool — asynchronously, with no HTTP endpoint at all.",
    "intro": [
        "Exercise 09 put a tool behind an HTTP endpoint and had *your code* call it. This is the other "
        "pattern Foundry supports, and it is quite different: **the agent service itself** drops a message "
        "on a Storage queue, an Azure Function picks it up, and the answer comes back on a second queue. "
        "Your application code never touches the tool at all.",
        "It is the right shape for background work, long-running jobs and anything that needs retries. It "
        "also needs a **standard-setup** project — one wired to your own Storage, Search and Cosmos DB — "
        "which you will provision here with a single command, and then look inside to see what was built.",
    ],
    "objectives": [
        "Explain the queue-based tool pattern and why it needs the standard agent setup.",
        "Provision a complete standard-setup project with `azd` and read what it created.",
        "Check which identity the agent runtime actually uses, and what it must be allowed to do.",
        "Write a queue-triggered Function that echoes the agent's `CorrelationId`.",
        "Deploy it, describe it to an agent as a tool, and watch a real round trip.",
        "Tear everything down cleanly.",
    ],
    "prereqs": [
        "An Azure subscription where you can create resource groups and **assign roles**.",
        "**Azure CLI**, **Azure Developer CLI (`azd`)** and Python 3.11.",
        "Quota for a `gpt-5.1` GlobalStandard deployment in your region. The exercise was built and tested "
        "in Australia East.",
    ],
    "before_extra": [
        {"warn": "This exercise provisions **real, billable resources**: an Azure AI Search service "
                 "(standard tier), a Cosmos DB account, two storage accounts, a Foundry account with a model "
                 "deployment, and a Flex Consumption Function app. Do the clean-up task when you finish. "
                 "Left running, the Search service alone costs about as much as a modest subscription per "
                 "month."},
        {"note": "The Bicep in `infra/` is vendored from Microsoft's `azure-functions-ai-services-agent-python` "
                 "template. That repository is now **archived** and `azd init --template` refuses it "
                 "non-interactively, but its infrastructure targets the current API and is what the Learn "
                 "page describes. Three corrections were made and each is explained where it matters: the "
                 "parameters file referenced properties the template does not define; the queue names now "
                 "match the Learn page; and the post-capability-host role assignments were rewritten after "
                 "the original ones failed on a live run (Task 5)."},
    ],
    "sections": [
        {
            "h2": "Task 1: Understand what you are building",
            "intro": [
                "Read this before running anything, because the shape is unusual.",
                {"table": (["Step", "Who does it", "Where"], [
                    ["1. The model decides to call `GetWeather`", "The agent service", "Foundry"],
                    ["2. A JSON message is written to the **input queue**",
                     "The agent service, using the **project's** managed identity", "Your storage account"],
                    ["3. The queue trigger fires", "Azure Functions", "Your Function app"],
                    ["4. The answer is written to the **output queue**",
                     "Your function, using the **Function's** managed identity", "Your storage account"],
                    ["5. The answer is matched to the request by `CorrelationId`", "The agent service", "Foundry"],
                ])},
            ],
            "steps": [
                ["Notice who is missing: **you**. In Exercise 09 your Python looped over tool calls and made "
                 "HTTP requests. Here the agent service does the whole round trip. Your script just asks a "
                 "question and gets an answer.",
                 {"note": "That is why this needs the **standard** agent setup. The agent runtime has to "
                          "reach *your* storage queues, which only the standard setup — with its capability "
                          "host bound to your own Storage, Search and Cosmos — can do. The basic setup is "
                          "explicitly unsupported."}],
                ["Two identities need **Storage Queue Data Contributor** on the storage account: the project's "
                 "managed identity (to write requests and read answers) and the Function's (to read requests "
                 "and write answers). Task 5 checks both, because on the first live run one of them was wrong."],
                ["Open a terminal in the exercise folder and check your tools:",
                 block("cd labs/15-azure-functions-tool\naz --version | head -1\nazd version", "powershell")],
                ["Sign in, and tell `azd` to reuse the Azure CLI's sign-in so nothing prompts later:",
                 block("az login --tenant YOUR-TENANT-ID\n"
                       "az account set --subscription YOUR-SUBSCRIPTION-ID\n"
                       "azd config set auth.useAzCliAuth true\n"
                       "azd auth login --check-status", "powershell"),
                 {"ok": "`Logged in to Azure as you@example.com`."}],
            ],
        },
        {
            "h2": "Task 2: Provision the standard setup",
            "steps": [
                ["Have a look at `infra/main.parameters.json`. The model is set to `gpt-5.1` (the one the "
                 "Learn page uses) and `vnetEnabled` is `false` to keep the exercise simple.",
                 {"tip": "If `gpt-5.1` is not available in your region, change `modelName` and `modelVersion` "
                         "here. Check with `az cognitiveservices model list -l YOUR-REGION`, and check quota "
                         "with `az cognitiveservices usage list -l YOUR-REGION`."}],
                ["Create an `azd` environment and tell it where to build:",
                 block("azd env new azfn-tool-lab\n"
                       "azd env set AZURE_LOCATION australiaeast\n"
                       "azd env set AZURE_SUBSCRIPTION_ID YOUR-SUBSCRIPTION-ID", "powershell"),
                 {"note": "Australia East is on the Flex Consumption allow-list in `main.bicep`. Pick another "
                          "region only from that list."}],
                ["Compile the Bicep first. It is free, fast, and catches most mistakes before Azure does:",
                 block("az bicep build --file infra/main.bicep --stdout > $null", "powershell"),
                 {"ok": "Warnings only. `BCP037` about `capabilityHostKind` is a known Bicep type-definition "
                        "lag; the property is valid at the API."}],
                ["Now provision. On the test run this took **13 minutes**; the Cosmos account and the "
                 "capability host are the slow parts:",
                 block("azd provision --no-prompt", "powershell")],
                ["While it runs, read `infra/main.bicep` and find the order in which things happen, because "
                 "the order is the interesting part:",
                 {"bullets": [
                     "**Dependent resources** — a Foundry account with the model deployment, Search, Cosmos, "
                     "and a storage account for the agent.",
                     "**The project**, with three connections pointing at those resources.",
                     "**Role assignments** for the project's identity on each of them.",
                     "**The capability host**, which turns those connections into the agent's own thread "
                     "storage, file storage and vector store. This is what makes it a standard setup.",
                     "**Role assignments again**, after the capability host — and Task 5 explains why they "
                     "have to be repeated rather than done once.",
                     "In parallel: the **Function app** on a Flex Consumption plan, with its own user-assigned "
                     "identity and a second storage account holding the two queues.",
                 ]}],
                ["When it finishes, read the outputs:",
                 block("azd env get-values", "powershell"),
                 {"ok": "`SUCCESS: Your application was provisioned in Azure in 13 minutes 7 seconds`, then "
                        "the outputs, including `PROJECT_ENDPOINT`, `STORAGE_CONNECTION__queueServiceUri`, "
                        "`MODEL_DEPLOYMENT_NAME`, `PROJECT_PRINCIPAL_ID`, `RESOURCE_GROUP` and "
                        "`AZURE_FUNCTION_APP_NAME`."}],
                ["Copy `.env.example` to `.env` and fill it from those outputs. `STORAGE_QUEUE_ENDPOINT` is "
                 "the `STORAGE_CONNECTION__queueServiceUri` value:",
                 block("PROJECT_ENDPOINT=https://....services.ai.azure.com/api/projects/...\n"
                       "STORAGE_QUEUE_ENDPOINT=https://....queue.core.windows.net\n"
                       "MODEL_DEPLOYMENT=gpt-5.1", "text")],
                ["Confirm the two queues exist. The Function storage account is the one whose name starts "
                 "with `st` (the agent's own is `stai…`):",
                 block("az storage account list -g rg-azfn-tool-lab --query \"[].name\" -o tsv\n"
                       "az storage queue list --account-name YOUR-FUNCTION-STORAGE-ACCOUNT --auth-mode login "
                       "--query \"[].name\" -o tsv", "powershell"),
                 {"ok": "`get-weather-input-queue` and `get-weather-output-queue`."}],
                ["Confirm what makes this a standard setup — the project's capability host, bound to your "
                 "three resources:",
                 block("az rest --method GET --url \"https://management.azure.com/subscriptions/YOUR-SUB"
                       "/resourceGroups/rg-azfn-tool-lab/providers/Microsoft.CognitiveServices/accounts/"
                       "YOUR-ACCOUNT/projects/YOUR-PROJECT/capabilityHosts?api-version=2025-04-01-preview\" "
                       "--query \"value[].{name:name, state:properties.provisioningState, "
                       "threads:properties.threadStorageConnections, storage:properties.storageConnections, "
                       "vectors:properties.vectorStoreConnections}\"", "powershell"),
                 {"ok": "One host, state `Succeeded`, with your Cosmos account under `threads`, your `stai…` "
                        "account under `storage` and your Search service under `vectors`."},
                 {"tip": "In Git Bash on Windows, prefix `az` commands that take a `/subscriptions/...` path "
                         "with `MSYS_NO_PATHCONV=1`, or the shell rewrites the path as a Windows one and Azure "
                         "returns `MissingSubscription`."}],
            ],
        },
        {
            "h2": "Task 3: Write the Function",
            "intro": ["This is the whole tool. It is short, and every line is doing something."],
            "steps": [
                ["Open `app/function_app.py`. It is already in place; read it rather than typing it:",
                 whole(LAB, "function_app.py", name="app/function_app.py", folder="app")],
                ["Three things to notice:",
                 {"bullets": [
                     "**No HTTP.** The trigger is a queue message and the reply is a queue message. There is "
                     "nothing to call and nothing to secure with a key.",
                     "**`CorrelationId` is echoed back exactly.** The agent service uses it to match your "
                     "answer to the request it sent. Leave it out and the agent waits until it times out.",
                     "**The arguments are looked for in two places.** The Learn page shows them under "
                     "`function_args`; the archived azd sample reads them from the top level. In Task 8 you "
                     "will see exactly which one arrives — and the answer is not what the sample assumes.",
                 ]}],
                ["Look at `connection=\"STORAGE_CONNECTION\"` on both decorators. That is not a connection "
                 "string. The Bicep sets three app settings that together mean *\"use the managed identity\"*:",
                 block("STORAGE_CONNECTION__queueServiceUri = https://<account>.queue.core.windows.net\n"
                       "STORAGE_CONNECTION__credential      = managedidentity\n"
                       "STORAGE_CONNECTION__clientId        = <user-assigned identity client id>", "text"),
                 {"note": "The double-underscore form is how Functions bindings take identity-based "
                          "connections. No account key exists anywhere in this exercise — the storage "
                          "accounts are created with shared-key access disabled."}],
                ["`app/host.json` sets `messageEncoding` to `base64` for queues. The agent service writes "
                 "base64-encoded messages, so this must match or the trigger fires on unreadable bytes."],
            ],
        },
        {
            "h2": "Task 4: Deploy it",
            "steps": [
                ["Deploy the Function. There is no Core Tools requirement — `azd` packages the app and the "
                 "platform builds it remotely, so it does not matter which Python you have locally:",
                 block("azd deploy --no-prompt", "powershell"),
                 {"ok": "`SUCCESS: Your application was deployed to Azure in 1 minute 19 seconds`, with the "
                        "Function app's URL."}],
                ["Confirm the platform sees your function:",
                 block("az functionapp function list -g rg-azfn-tool-lab -n YOUR-FUNCTION-APP "
                       "--query \"[].{name:name, trigger:config.bindings[0].type}\" -o table", "powershell"),
                 {"ok": "One row: `GetWeather` with a `queue` binding."}],
                [{"tip": "If it lists nothing, wait a minute and retry — the remote build can take a moment "
                         "to register the function after deployment reports success."}],
            ],
        },
        {
            "h2": "Task 5: Check the identity the runtime actually uses",
            "intro": [
                "This task exists because the first live run of this exercise **failed**, and the reason is "
                "worth ten minutes of anyone's time. Creating the agent produced this:",
                block("azure.core.exceptions.HttpResponseError: (forbidden) ... Request blocked by Auth\n"
                      "agent-ai-cosmos... : principal [1fbe5fa4-...] does not have required RBAC permissions\n"
                      "to perform action [Microsoft.DocumentDB/databaseAccounts/readMetadata] on resource\n"
                      "[dbs/enterprise_memory/colls/0fad3d46-...-agent-definitions-v1]", "text"),
                "Two separate things had gone wrong, and both are general lessons rather than quirks of "
                "this template.",
            ],
            "steps": [
                ["**First: the project's identity had been recreated part-way through provisioning.** Read "
                 "the identity the project has *now*:",
                 block("az rest --method GET --url \"https://management.azure.com/subscriptions/YOUR-SUB"
                       "/resourceGroups/rg-azfn-tool-lab/providers/Microsoft.CognitiveServices/accounts/"
                       "YOUR-ACCOUNT/projects/YOUR-PROJECT?api-version=2025-04-01-preview\" "
                       "--query \"identity.principalId\" -o tsv", "powershell"),
                 "Then read who holds the queue role on the Function storage account:",
                 block("az role assignment list --scope \"/subscriptions/YOUR-SUB/resourceGroups/"
                       "rg-azfn-tool-lab/providers/Microsoft.Storage/storageAccounts/YOUR-FUNCTION-STORAGE\" "
                       "--query \"[?roleDefinitionName=='Storage Queue Data Contributor'].principalName\" "
                       "-o tsv", "powershell"),
                 {"ok": "With the corrected Bicep in this folder the project's current principal id appears in "
                        "that list. On the original template it did **not**: the queue role had been granted "
                        "to `b557be47-…`, but the runtime was using `1fbe5fa4-…` — a different identity with "
                        "the same display name. Creating the capability host had recreated the project's "
                        "system-assigned identity, and every role granted to the old one was dead."},
                 {"note": "The general lesson: **never capture a managed identity's principal id early in a "
                          "deployment and reuse it later** if any intermediate step can recreate the resource. "
                          "Read it at the point of use. The corrected "
                          "`infra/agent/post-capability-host-role-assignments.bicep` does exactly that — "
                          "open it and find `project.identity.principalId`."}],
                ["**Second: the runtime wanted a container that did not exist yet.** List what the capability "
                 "host actually created:",
                 block("az cosmosdb sql container list -g rg-azfn-tool-lab -a YOUR-COSMOS-ACCOUNT "
                       "-d enterprise_memory --query \"[].name\" -o tsv", "powershell"),
                 {"ok": "Three containers, all ending `-thread-message-store`, `-system-thread-message-store` "
                        "or `-agent-entity-store`."},
                 "But the error named `…-agent-definitions-v1` — a **fourth** container the runtime creates on "
                 "first use. The original Bicep granted the Cosmos data role on the three existing containers "
                 "by name. A container-scoped grant can never cover a container that does not exist yet.",
                 {"note": "The corrected Bicep grants the role at **database** scope instead — "
                          "`/dbs/enterprise_memory` — so anything the runtime creates inside it is covered. "
                          "This is the same discrepancy noted in Exercise 08: the documented container names "
                          "differ between runtime versions, so do not hard-code them."}],
                ["Confirm the database-scoped grant is in place:",
                 block("az cosmosdb sql role assignment list -g rg-azfn-tool-lab -a YOUR-COSMOS-ACCOUNT "
                       "--query \"[].{principal:principalId, scope:scope}\" -o table", "powershell"),
                 {"ok": "A row for the project's current principal id whose scope ends in "
                        "`/dbs/enterprise_memory`."}],
                ["If you are ever using a template that has **not** been corrected, these two commands are "
                 "the manual fix — the same ones that were run to rescue the first live attempt:",
                 block("az cosmosdb sql role assignment create -g rg-azfn-tool-lab -a YOUR-COSMOS-ACCOUNT `\n"
                       "  --role-definition-id 00000000-0000-0000-0000-000000000002 `\n"
                       "  --principal-id THE-CURRENT-PROJECT-PRINCIPAL-ID `\n"
                       "  --scope \"/dbs/enterprise_memory\"\n\n"
                       "az role assignment create --assignee-object-id THE-CURRENT-PROJECT-PRINCIPAL-ID `\n"
                       "  --assignee-principal-type ServicePrincipal `\n"
                       "  --role \"Storage Queue Data Contributor\" `\n"
                       "  --scope \"/subscriptions/YOUR-SUB/resourceGroups/rg-azfn-tool-lab/providers/"
                       "Microsoft.Storage/storageAccounts/YOUR-FUNCTION-STORAGE\"", "powershell"),
                 {"tip": "Azure RBAC assignments take 30 seconds to a couple of minutes to take effect. "
                         "Cosmos SQL role assignments are usually immediate."}],
            ],
        },
        {
            "h2": "Task 6: Describe the tool to the agent",
            "intro": ["Now the other side. Create `ask_the_agent.py` in the exercise folder. You will build "
                      "it up over the next three tasks."],
            "steps": [
                ["Make a virtual environment for the agent script and install its packages:",
                 block(SETUP, "powershell")],
                ["Start the file with the imports and configuration:",
                 block('"""Create an agent that uses the Azure Function as a tool."""\n\n'
                       "import os\nimport time\n\n"
                       "from azure.ai.projects import AIProjectClient\n"
                       "from azure.ai.projects.models import (\n"
                       "    AzureFunctionBinding,\n    AzureFunctionDefinition,\n"
                       "    AzureFunctionDefinitionFunction,\n    AzureFunctionStorageQueue,\n"
                       "    AzureFunctionTool,\n    PromptAgentDefinition,\n)\n"
                       "from azure.identity import DefaultAzureCredential\n"
                       "from dotenv import load_dotenv\n\n"
                       "load_dotenv()\n\n"
                       'PROJECT_ENDPOINT = os.environ["PROJECT_ENDPOINT"]\n'
                       'STORAGE_QUEUE_ENDPOINT = os.environ["STORAGE_QUEUE_ENDPOINT"]\n'
                       'MODEL = os.environ["MODEL_DEPLOYMENT"]\n\n'
                       'AGENT_NAME = "azure-function-agent-get-weather"')],
                ["Add the tool description:",
                 block(task(LAB, SCRIPT, 2))],
                ["Add a main block that just prints what you described, and run it:",
                 block('if __name__ == "__main__":\n' + MAIN_AFTER_2),
                 block("python ask_the_agent.py", "powershell")],
                ["Read the JSON it printed. It has three parts, and they map exactly onto the table in Task 1:",
                 {"table": (["Part", "Tells the agent service"], [
                     ["`input_binding`", "Which queue to drop the request on"],
                     ["`output_binding`", "Which queue to wait on for the answer"],
                     ["`function`", "What the model sees — a name, a description, and the arguments it may send"],
                 ])},
                 {"note": "Compare `function` with the `FunctionTool` from Exercise 03. It is the same idea. "
                          "The bindings are what is new: instead of *your code* being the thing that runs, "
                          "a queue is."}],
                [{"whole_file": upto(LAB, SCRIPT, 2, MAIN_AFTER_2), "name": "ask_the_agent.py"}],
            ],
        },
        {
            "h2": "Task 7: Create the agent",
            "steps": [
                ["Add this:",
                 block(task(LAB, SCRIPT, 3))],
                ["Replace the main block:",
                 block('if __name__ == "__main__":\n' + MAIN_AFTER_3),
                 block("python ask_the_agent.py", "powershell"),
                 {"ok": "`Created agent azure-function-agent-get-weather, version 1`."},
                 {"warn": "If you get a `Forbidden (403)` from Cosmos here, go back to Task 5 — that is "
                          "exactly the failure it describes."}],
                ["Open the project in the Foundry portal and find the agent. The tool shows up on its "
                 "definition, with both queue endpoints visible.",
                 {"note": "Every run of this script creates a *new version*, exactly as in Exercise 03. The "
                          "clean-up in Task 9 deletes the version it made."}],
                [{"whole_file": upto(LAB, SCRIPT, 3, MAIN_AFTER_3), "name": "ask_the_agent.py"}],
            ],
        },
        {
            "h2": "Task 8: Ask it, and watch the round trip",
            "steps": [
                ["Add this:",
                 block(task(LAB, SCRIPT, 4))],
                ["Replace the main block:",
                 block('if __name__ == "__main__":\n' + MAIN_AFTER_4),
                 block("python ask_the_agent.py", "powershell")],
                [{"ok": "On the live test run:\n\n"
                        "`You: What is the weather like in Sydney right now?`\n"
                        "`Agent: It's currently 16°C and sunny in Sydney.`\n"
                        "`(took 46.6s including the queue round-trip)`\n"
                        "`You: And in Melbourne?`\n"
                        "`Agent: It's currently 19°C and sunny in Melbourne.`\n"
                        "`(took 8.9s including the queue round-trip)`"},
                 "Now check the arithmetic. The Function computes `len(location) + 10`. `Sydney` is six "
                 "letters, `Melbourne` is nine. **Those numbers came from your Function, not from the "
                 "model.** That is the proof the tool ran."],
                ["Look at the two timings. The first call includes the model deciding to use the tool, the "
                 "message reaching the queue, a Flex Consumption **cold start**, and the answer coming back. "
                 "The second, with the Function already warm, is a fifth of the time. Inside the Function "
                 "itself each call took about 90 ms."],
                ["Now prove the Function really ran, from its own logs. The query command needs an `az` "
                 "extension the first time:",
                 block("az extension add --name application-insights\n\n"
                       "az monitor app-insights query --app YOUR-APP-INSIGHTS -g rg-azfn-tool-lab "
                       "--analytics-query \"traces | where message startswith 'Message from agent' or "
                       "message startswith 'Reply to agent' | project timestamp, message | order by "
                       "timestamp asc\" --query \"tables[0].rows[]\" -o json", "powershell"),
                 {"tip": "The App Insights resource is named `appi-<token>` — find it with "
                         "`az resource list -g rg-azfn-tool-lab --resource-type Microsoft.Insights/components "
                         "--query \"[].name\" -o tsv`. Ingestion takes a minute or two after the call."},
                 {"ok": "Two pairs of lines. The first pair, from the live run:\n\n"
                        "`Message from agent: {\"function_args\": {\"location\": \"Sydney\"}, "
                        "\"function_name\": \"GetWeather\", \"CorrelationId\": \"deYD1Ev…rh4=\"}`\n"
                        "`Reply to agent: {\"Value\": \"It is 16 degrees and sunny in Sydney.\", "
                        "\"CorrelationId\": \"deYD1Ev…rh4=\"}`"}],
                ["That first line answers the question left open in Task 3. **The service sends the "
                 "arguments nested under `function_args`**, alongside a `function_name` field the Learn page "
                 "does not mention, and an opaque `CorrelationId`. The archived azd sample reads "
                 "`messagepayload['location']` at the top level and would crash here with a `KeyError`. The "
                 "Learn page is right; the older sample is not.",
                 {"note": "This is why the Function checks both places. It costs nothing, and it meant the "
                          "first live run answered the question instead of failing on it."}],
                ["Both queues should now be empty — the service consumed its answers:",
                 block("az storage queue stats --name get-weather-output-queue "
                       "--account-name YOUR-FUNCTION-STORAGE --auth-mode login "
                       "--query approximateMessageCount -o tsv", "powershell"),
                 {"ok": "`0`, for both queues."}],
                ["**Try breaking it, once.** In `app/function_app.py`, comment out the `\"CorrelationId\"` "
                 "line, run `azd deploy --no-prompt`, and ask again.",
                 {"warn": "The agent waits, and eventually fails or answers without the tool. Your Function "
                          "ran perfectly and wrote a perfectly good answer that nothing could match to the "
                          "request. Put the line back and redeploy."}],
                [{"whole_file": upto(LAB, SCRIPT, 4, MAIN_AFTER_4), "name": "ask_the_agent.py"}],
            ],
        },
        {
            "h2": "Task 9: Clean up",
            "steps": [
                ["Add the last function and make the main block tidy up after itself:",
                 block(task(LAB, SCRIPT, 5))],
                ["The finished script:",
                 whole(LAB, SCRIPT)],
                ["Run it once more. It creates a version, asks, and deletes the version — leaving the "
                 "project as it found it.",
                 {"ok": "`Deleted azure-function-agent-get-weather version 1` as the last line."}],
                ["Then remove everything the exercise provisioned. `--purge` also purges the soft-deleted "
                 "Foundry account so its quota is released:",
                 block("azd down --purge --no-prompt", "powershell"),
                 {"warn": "This deletes the resource group and every resource in it, including the Search "
                          "service and Cosmos account. Make sure `azd env get-values` shows the environment "
                          "you expect before you run it."}],
            ],
        },
        {
            "h2": "When to use this instead of Exercise 09",
            "steps": [
                [{"table": (["", "HTTP tool (Exercise 09)", "Queue tool (this exercise)"], [
                    ["Who calls the tool", "Your application code", "The agent service itself"],
                    ["Timing", "Synchronous — the caller waits", "Asynchronous — with retries built in"],
                    ["Setup needed", "Any project", "Standard setup only"],
                    ["Security surface", "An HTTP endpoint to authenticate", "Two queues; identities only"],
                    ["Good for", "Fast lookups, interactive chat", "Background jobs, long-running work, "
                                                                   "reliable delivery"],
                ])}],
                ["The Learn page also lists MCP hosted on Functions as a third option, and it maps onto "
                 "Exercise 09's MCP task. Three integrations, one Function service — choose by whether you "
                 "need real-time answers or reliable background processing."],
            ],
        },
    ],
    "knowledge_check": [
        {"q": "Why does this pattern require the standard agent setup?",
         "options": ["A. It is faster", "B. The agent runtime must reach your storage queues, which only the "
                     "standard setup's capability host allows", "C. Basic setup has no model deployments"],
         "answer": "B",
         "why": "The Learn page is explicit that basic setup is unsupported for this tool."},
        {"q": "Creating the agent fails with a Cosmos 403 naming a principal you have never seen. What "
              "happened?",
         "options": ["A. Cosmos is in the wrong region", "B. The project's managed identity was recreated "
                     "after the roles were granted, so the runtime is using an identity with no rights",
                     "C. The model deployment failed"],
         "answer": "B",
         "why": "Task 5. Read the identity at the point of use; do not reuse one captured earlier."},
        {"q": "Where does the agent service put the tool arguments in the queue message?",
         "options": ["A. At the top level, as `location`", "B. Nested under `function_args`",
                     "C. In the message's metadata"],
         "answer": "B",
         "why": "Observed in the Function's own log in Task 8. The archived sample gets this wrong."},
    ],
    "summary": [
        "You provisioned a complete standard-setup Foundry project with one command and read what it built, "
        "found and understood a real identity-recreation problem in the template, deployed a queue-triggered "
        "Function with no HTTP surface and no keys, described it to an agent as a tool, and watched the "
        "agent service do the whole round trip without your code being involved.",
        "You also settled two things the documentation leaves ambiguous, from evidence: the runtime sends "
        "tool arguments under `function_args`, and it creates Cosmos containers whose names you should not "
        "hard-code.",
    ],
    "cleanup": [
        "Task 9 covers it: run the finished script once (it deletes its own agent version), then "
        "`azd down --purge --no-prompt`.",
        {"warn": "Do not skip this. The Search service and the Foundry account keep costing money while "
                 "they exist."},
    ],
    "refs": [
        ("Integrate Azure Functions with Foundry agents",
         "https://learn.microsoft.com/azure/foundry/agents/how-to/tools/azure-functions?pivots=python"),
        ("Standard agent setup", "https://learn.microsoft.com/azure/foundry/agents/concepts/standard-agent-setup"),
        ("Flex Consumption plan", "https://learn.microsoft.com/azure/azure-functions/flex-consumption-plan"),
        ("Identity-based connections in Functions",
         "https://learn.microsoft.com/azure/azure-functions/functions-reference#configure-an-identity-based-connection"),
        ("Cosmos DB data-plane RBAC", "https://learn.microsoft.com/azure/cosmos-db/nosql/security/how-to-grant-data-plane-role-based-access"),
    ],
}

LABS = [LAB15]
