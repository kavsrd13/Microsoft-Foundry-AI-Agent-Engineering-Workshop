# Exercise 06.1 — Use Azure Functions with Foundry Agents (Queue-based)

This lab demonstrates how an AI agent in Microsoft Foundry calls an Azure Function asynchronously using Azure Storage queues.

## Folder Structure
- `function_app/` - The Azure Function app listening to `get-weather-input-queue` and writing to `get-weather-output-queue`.
- `agent.py` - The Python script using `azure-ai-projects` to register the agent with `AzureFunctionTool` and invoke it.
- `solution/` - Completed reference files.

Follow the step-by-step instructions in the workshop documentation to complete this lab.
