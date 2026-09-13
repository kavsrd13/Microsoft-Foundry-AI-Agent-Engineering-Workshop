# Lab 16B — Hosted deployment

Use Python **3.13** for this part. The service is GA, but the pinned Python hosting adapter is prerelease. This is a real deployment recipe, not evidence that deployment has been run in your tenant.

1. Install Azure Developer CLI and the Foundry extension following the [official sample](https://github.com/microsoft-foundry/foundry-samples/tree/main/samples/python/hosted-agents/agent-framework/responses/01-basic). Check `azd version`, `azd ext list` and `azd ai agent --help`. The sample requires azd >=1.27.1 and the agents extension >=1.0.0-beta.9. The current installation command is `azd ext install microsoft.foundry`.
2. Run and inspect the local workflow and host first. Local model inference still requires Azure authentication. Stop the host before changing environments.
3. From the lab directory create a Python 3.13 environment, activate it, and install `requirements.txt`. Then `cd deploy`. This folder is a self-contained azd project; its `agent/main.py` is the same simple host concept.
4. Read `azure.yaml`. Supply a unique `AZURE_ENV_NAME` such as `acme-lab16-a1b2c3`. Select an approved subscription and Australia East in the azd prompts. Set the model name, version, deployment SKU and capacity to values the instructor has verified for that region. The template deliberately does not hardcode GlobalStandard or silently choose another region.

```powershell
azd auth login
azd env new acme-lab16-a1b2c3
azd env set AZURE_LOCATION australiaeast
azd env set AZURE_AI_MODEL_NAME YOUR-VERIFIED-MODEL
azd env set AZURE_AI_MODEL_VERSION YOUR-VERIFIED-VERSION
azd env set AZURE_AI_MODEL_DEPLOYMENT_NAME acme-lab16-chat
azd env set AZURE_AI_MODEL_SKU YOUR-APPROVED-SKU
azd provision
azd deploy
azd ai agent invoke "Explain why service assistants cite sources."
```

The uppercase values above must be replaced before provisioning; edit the numeric `capacity: 10` in azure.yaml to the instructor-approved allocation. The provisioner creates a dedicated project/model and the agent service uses that project. Inspect the provision summary and deployment logs, then invoke again and check the actual response and service status. Record resource group, project, agent name/version and deployment type. Reuse this environment on reruns.

If Foundry Project Manager/provisioning rights, approved model capacity or the hosted runtime are unavailable, participants complete the local work and the instructor demonstrates this part in an approved environment. Do not substitute a different region without review.

Cleanup: from this exact `deploy` directory, select the recorded dedicated lab environment and review `azd env get-values` locally. Then use `azd down` and its confirmation to remove only that environment's resources. Never run down against a shared classroom environment. Recheck the portal for the recorded resource group/agent. Stop local servers with Ctrl+C and run `remove generated local files manually` from the lab folder for local generated files.

The YAML shape follows the official sample; cloud provisioning, Python3.13 runtime and tenant permissions must still be rehearsed. See the repository VALIDATION.md for the local checks actually performed.
