# Publishing and hosting are separate exercises

## Publish a Foundry agent version to Teams / Microsoft 365 Copilot

**Guided tenant exercise: 30–45 minutes.** Use the persistent Foundry agent created in the earlier agent-version lab. Lab21's stateless Responses app is not itself a publishable Foundry agent version.

1. Verify the target agent version responds in the Foundry playground. Record its version ID and evaluation evidence. Review the current [publishing prerequisites and steps](https://learn.microsoft.com/azure/foundry/agents/how-to/publish-copilot) with the tenant administrator: publishing can create/configure an agent application, identity and Bot Service resources. Confirm permissions and channel policies before starting.
2. In the agent's current publishing surface choose the supported Teams/M365 destination. Inspect the proposed resources, identity and authorised callers. Publish only this workshop agent/version into the approved test tenant.
3. Record the stable published endpoint/resource ID separately from the development agent version. If an agent application is created, inspect its deployment and invocation permission using [agent applications](https://learn.microsoft.com/azure/foundry/agents/how-to/agent-applications).
4. Install/open the approved app through the channel's test/distribution flow. Send a synthetic enquiry, find the corresponding agent trace, and record the actual response. A portal success notification is not channel execution evidence.
5. Test an excluded user. Verify the channel's caller identity is mapped into retrieval permissions before adding private records: publishing does not automatically reproduce Lab21's JWT-to-ACL filter. Keep this channel test on public synthetic knowledge until its identity path has been implemented.
6. Publish an intentionally distinguishable, evaluated second version; verify the channel uses the new version. Restore the approved version through the available application deployment/publishing control and verify again. Record the supported rollback steps for this tenant.
7. Remove the workshop app/channel registration and workshop-only publishing resources after testing; do not remove shared Bot or identity resources.

If licensing, admin consent, network compatibility or the publishing surface is unavailable, mark this exercise **not executed** and record the precise prerequisite. Do not substitute screenshots of another tenant as execution evidence.

## App Service, Functions and Container Apps comparison

| Host | Exercise | Scaling observation |
|---|---|---|
| App Service | Lab22 deploys the authenticated web API/UI to a Python Linux plan. | Inspect plan capacity. Add an approved Azure Monitor autoscale rule (minimum 1, maximum 2 for this exercise), generate bounded synthetic load, then remove it. The supplied template has fixed capacity. |
| Azure Functions | Lab22 deploys a separate HTTP tool to the same dedicated plan. Lab20 covers richer tool identity and integrations. | Dedicated-plan Functions share plan capacity; this template does not demonstrate consumption scaling. Compare with a separately provisioned supported Flex plan before choosing it. |
| Container Apps | Build the Dockerfile below using the Lab21 folder as context; deploy through an approved Container Apps environment and registry. | Configure HTTP concurrent-request scaling with min 1/max 2, inspect replica changes and revision traffic; remove test resources. |

For the container exercise use this minimal Dockerfile in Lab21 (optional file creation):

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
CMD ["python", "-m", "uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build with `docker build -t resident-app:workshop .`. Deploy the image with ingress targeting port 8000, HTTPS and the **same public ID/endpoint settings** as Lab21. Assign the new container managed identity Search reader and Foundry inference roles; do not reuse App Service's identity ID. Register the container HTTPS origin in the SPA redirect list. Complete both authenticated user ACL tests before shifting traffic. The example copies only requirements and source, so `.env` is not baked into the image. Image registry credentials should use managed identity. Review [Container Apps deployment](https://learn.microsoft.com/azure/container-apps/get-started) and [scaling](https://learn.microsoft.com/azure/container-apps/scale-app).

These are alternatives, not three mandatory simultaneous production hosts. The container/autoscale/channel exercises are guided configurations, not pre-provisioned by the Bicep scaffold.
