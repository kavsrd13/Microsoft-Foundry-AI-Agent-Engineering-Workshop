# Local verification — 2026-09-11

- Bicep CLI **0.47.16** built `src/infra/main.bicep` including `resources.bicep` with exit 0 and no diagnostics.
- `validate.py` passed service-path, parameter-JSON, workflow gate-order and basic scaffold checks.
- Lab21 `validate.py` passed local RSA-signed JWT verification/rejection tests, missing/forged-header checks, ACL filter checks and mocked SSE completion.

These checks do not establish ARM deployment success, quota/capacity, tenant permissions, Function remote build, GitHub workflow execution, live Search/Foundry access, channel publishing or autoscaling. Rehearse those using the README evidence steps. The Application Insights resource/connection string is provisioned; full correlated web-application instrumentation requires the Lab23 integration exercise.
