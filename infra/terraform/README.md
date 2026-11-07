# Terraform infrastructure

A self-contained, fresh-deployment Terraform alternative for the standalone
AI Gateway and Foundry support infrastructure. Existing Bicep, application and
`azure.yaml` defaults are unchanged. The gateway resource family is
`Microsoft.ApiManagement/aigateways`, not classic API Management
`Microsoft.ApiManagement/service`.

**The end-to-end on-demand hosted digest was verified on November 7, 2026:**
Terraform infrastructure, hosted agent, AI Gateway/model, all three real GitHub
tools and correlated agent/gateway telemetry. The gateway API is
`2025-09-01-preview`, aligned with the upstream Bicep path. This is one accepted
runtime path, not certification of every build, credential or lifecycle scenario.
See the [acceptance matrix and precise boundaries](docs/evidence-map.md#acceptance-matrix).

## Start here

Follow the single [offline and deployment-preparation route](docs/architecture.md#offline-and-deployment-preparation).
For the complete staged route through the agent and optional daily schedule,
follow the [guided application flow](docs/application-flow.md). It keeps
Terraform plan/apply explicit and does not change the root Bicep manifest.
The compatibility baseline is Terraform **1.11.4**, locked AzAPI **2.13.0**,
PowerShell 7 and Python 3. Offline checks need no Azure credentials; uncached
locked providers still require registry access.

| Entry | Purpose |
|---|---|
| This root | Three workload groups, three modules, default Foundry access/monitoring/shared registry wiring and nonsecret outputs |
| [Gateway only](examples/gateway-only/README.md) | Gateway scaffold without backend models or agent support |
| [Existing models](examples/existing-models/README.md) | Gateway routing to a referenced, same-subscription backend |
| [Models only](examples/models-only/README.md) | Model account and pinned deployments |
| [Agent support only](examples/agent-support-only/README.md) | Project, Storage, ACR and monitoring; no deployed agent |

Modules: [ai-gateway](modules/ai-gateway/README.md),
[foundry-models](modules/foundry-models/README.md),
[foundry-agents](modules/foundry-agents/README.md).

The application root **enables by default** Foundry model-access grants, a
separate project-only tool-access grant, the managed-identity Insights connection
with two scoped publisher grants, and registry-connection sharing. Each setting
can be disabled independently; reusable modules and standalone examples retain
their minimal defaults. Existing users should review the
[default changes and explicit opt-outs](docs/architecture.md#optional-application-integration)
before planning an upgrade.

Registry sharing remains the Bicep-matching default request, not a requirement
for project-local application access. See the [explicit compatibility choice](docs/architecture.md#project-local-registry-compatibility)
when Azure returns the owned connection unshared.

After deploying the agent, its actual identity can differ from both Foundry
support identities. The opt-in `hosted_agent_principals` map supplies that
independently verified principal for gateway Models User and agent-Insights
publisher grants. Its empty default changes no resources. Follow the
[postdeployment identity handoff](docs/application-flow.md#3-bind-the-deployed-agent-identity);
do not duplicate or silently adopt existing operational assignments.

## Model content safety

The application root's **bundled model profile now selects `Medium`** for Hate,
Self-Harm, Sexual and Violence on every gateway catalog model, matching the
[Bicep policy body](../ai-gateway/main.bicep). Reusable modules and the
existing-models example retain null/omitted defaults.

An explicit `model_deployments` map **replaces**, rather than merges with, that
profile. Set each model's `content_safety_severity` to `Low`, `Medium` or `High`
to select the same severity for all four categories. Null or omission in an
explicit map omits that model's policy; the string `"None"` is not accepted.
To preserve the previous root policy omission, provide your full deployment
map with null severities. Keep deployment keys compatible with `model_aliases`.

This is a gateway model policy, not MCP protection or a change to the separate
`Microsoft.DefaultV2` backend filter. Review the policy-body changes in a fresh
plan before upgrading. A disposable selected-2025-API probe returned all four
Medium severities; neither that readback nor the offline contracts prove safety
enforcement. See the [acceptance matrix](docs/evidence-map.md).

## Application and telemetry boundaries

A tool role does not create a ToolServer, deliver a credential or establish
working invocation. The RemoteTool still requires an explicit verified endpoint.
The opt-in [GitHub tool runner](docs/toolchain.md) provides the separate
credential-explicit ToolServer/Toolbox lifecycle and nonsecret connection
handoffs. It is not called by Terraform or azd. Real tool invocation and a
bounded synthetic-header control-plane lifecycle were verified separately;
credential rotation and general secret-handling guarantees remain unqualified.
Foundry monitoring is separate from gateway OpenTelemetry. Gateway-bearing roots
now default to the [two-stage native telemetry path](docs/native-telemetry.md):
managed ingestion first, then a GET-only readiness handoff and a fresh plan for
the scoped DCR publisher/exporter. Stage one reports `pending`; existing legacy
exporters require an explicit compatibility choice and separate migration.
The nonsecret JSON
environment adapter and [GET-only live qualification runner](docs/live-readback.md)
remain separate from application deployment.

See [ownership, state and API differences](docs/architecture.md) and the
[validation and acceptance guide](docs/evidence-map.md). Recurring execution,
credential lifecycle guarantees and full teardown remain separate qualifications;
no schedule was enabled by the accepted on-demand run.
The [application helper](docs/application-flow.md) now provides offline preparation
and separately confirmed app-only azd deployment; it neither replaces Terraform
nor installs tools, grants roles or reuses Bicep hooks. The
[tool contract boundary](docs/tool-credential-boundary.md) explains why existing
credential hooks are not reused. Telemetry
configuration alone is not delivery proof; the evidence map records the
independently correlated hosted-agent, model and GitHub request traces.
