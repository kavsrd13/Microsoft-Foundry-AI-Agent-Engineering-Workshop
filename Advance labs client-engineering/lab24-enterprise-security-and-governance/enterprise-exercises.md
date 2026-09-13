# Tenant-dependent enterprise exercises

These are guided practical exercises, not preconfigured integrations. Use disposable resources, current official instructions and appropriately licensed administrator access. For every exercise, record scope, owner, observed result, evidence location and reversal procedure. Mark an unavailable feature `pending`, not `verified`.

## A. Entra identity and Conditional Access

1. Draw three distinct subjects: signed-in user, application's managed identity and an Entra Agent ID. Identify which token each downstream service expects. The JWT app in Lab21 is not automatically an Agent ID deployment.
2. With an authorised administrator, inspect or create a dedicated agent identity through the supported Agent ID onboarding flow. Record its blueprint relationship, sponsor, object ID and allowed resource permissions. Do not put tokens in the evidence file. Verify a token/sign-in event belongs to this specific identity; a normal app registration is not equivalent evidence.
3. Use a test identity and narrowly scoped Conditional Access policy in report-only mode. Trigger token acquisition, inspect policy evaluation in sign-in logs and explain the subject/audience. User-delegated flows and app-only agent flows can require different policy scopes. Have the administrator review impact before any enforcement test.
4. Remove only the test assignment/policy/identity you created. Preserve unrelated tenant objects and emergency-access arrangements.

Evidence: blueprint/agent relationship, sponsor, permission scope and sanitised sign-in/policy evaluation. Licensing and supported policy controls must be checked in the tenant.

Sources: [Agent identities](https://learn.microsoft.com/entra/agent-id/identity-platform/agent-service-principals), [Conditional Access for agents](https://learn.microsoft.com/entra/identity/conditional-access/agent-id).

## B. Networking and Australian processing

1. Identify the chosen supported private-network architecture and its DNS zones for each service; do not assume one private endpoint isolates all dependencies.
2. In a disposable deployment, inspect private endpoint approval and service public-network settings. Run `network_check.py` inside the runtime network and from the instructor's outside test host.
3. With an authorised identity, verify intended access from inside and rejection from outside when public access is disabled. Inspect private DNS, route and endpoint state when results differ. A DNS answer alone is insufficient.
4. Record model and embedding deployment type, actual resource regions and every external tool/evaluator destination. Review any cross-region exception explicitly.

Use [Foundry private networking](https://learn.microsoft.com/azure/foundry/how-to/configure-private-link) and the selected services' private endpoint instructions. Lab22's public workshop deployment is not a private-network production template; this exercise is a separate tenant configuration activity.

## C. Defender, Purview and Control Plane

1. In the Foundry operational/compliance view locate the lab asset and owner. Inspect current guardrail compliance and follow its trace/evaluation links.
2. A security administrator selects the lab subscription/resource scope and reviews the applicable Defender plan, cost and permissions. Enable only an approved test integration, inspect posture recommendations, and use the documented benign/test alert method if one is available. Record an actual recommendation/alert or mark alert verification pending; do not manufacture one.
3. With a Purview/Foundry administrator, review the integration's interaction-data destination and policy prerequisites before enabling it. Submit a synthetic labelled document/query and locate its audit/classification evidence. Where data-security policy enforcement is supported, test an allowed and denied interaction using the required user context.
4. Compare this evidence with Lab21 Search filtering. A label, audit event or managed-identity request alone does not prove that a user-context Purview policy is enforced.
5. Restore the recorded test configuration. Retain organisational controls that existed before the lab.

Evidence: scoped configuration, actual posture/audit event, allowed/denied result and data destination. [Foundry compliance/security](https://learn.microsoft.com/azure/foundry/control-plane/how-to-manage-compliance-security), [Purview AI integrations](https://learn.microsoft.com/purview/developer/secure-ai-with-purview).

## D. Content safety and red teaming

Run the benign API classification and four synthetic probes first. Review unsupported claims as well as marker disclosure. Then, where available, follow the official managed Red Teaming Agent workflow against the owned test candidate: select risk categories, a small supported scan, approved model/region and synthetic target inputs. Inspect findings and rerun after an instruction/filter change. Keep scan IDs and failed examples in approved private storage. The four local probes are not a replacement for that scan.

Sources: [Content Safety](https://learn.microsoft.com/azure/ai-services/content-safety/quickstart-text), [managed red-team scans](https://learn.microsoft.com/azure/foundry/how-to/develop/run-scans-ai-red-teaming-agent).

## E. Production readiness review

Run `readiness.py` against your evidence file. Explain each pending control and assign a next action. Include app auth, downstream authorisation, retention, cost owner, evaluation thresholds, alert response and rollback. A completed evidence form is still subject to engineering/security review; it is not a certification.
