# Illustrative fallback — NOT recorded endpoint output

1. Model requests `microsoft_docs_search` on `microsoft_learn` with a public Azure AI Search question.
2. Participant reviews the proposed arguments and chooses **deny**. The tool is not authorised.
3. On a second run the participant chooses **approve**. The model may receive public documentation and cite it.

This is an explanatory scenario, not an actual MCP transcript. No response text or tool request ID has been fabricated. Endpoint-down mode teaches the boundary using these steps and source code; it does not claim a successful call. During rehearsal save the genuine `live-output.txt` alongside date, selected model and approval decisions.

Read-only refers to the tool's operation: its query still leaves the Foundry processing boundary. Do not include citizen records, credentials or internal policy text in tool arguments.
