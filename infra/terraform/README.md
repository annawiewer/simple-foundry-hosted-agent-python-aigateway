# Terraform infrastructure

A self-contained, fresh-deployment Terraform alternative for the standalone
AI Gateway and Foundry support infrastructure. Existing Bicep, application and
`azure.yaml` defaults are unchanged.

**Full hosted-agent/azd parity is not yet accepted.** The public gateway API is
`2025-09-01-preview`, aligned with the upstream Bicep path. Earlier live checks
used a separate 2026 deployment and do not qualify this pin change. See the
single [acceptance matrix and remaining gates](docs/evidence-map.md#acceptance-matrix).

## Start here

Follow the single [offline and deployment-preparation route](docs/architecture.md#offline-and-deployment-preparation).
The compatibility baseline is Terraform **1.11.4**, locked AzAPI **2.13.0**,
PowerShell 7 and Python 3. Offline checks need no Azure credentials; uncached
locked providers still require registry access.

| Entry | Purpose |
|---|---|
| This root | Three workload groups, three modules and nonsecret infrastructure outputs |
| [Gateway only](examples/gateway-only/README.md) | Gateway scaffold without backend models or agent support |
| [Existing models](examples/existing-models/README.md) | Gateway routing to a referenced, same-subscription backend |
| [Models only](examples/models-only/README.md) | Model account and pinned deployments |
| [Agent support only](examples/agent-support-only/README.md) | Project, Storage, ACR and monitoring; no deployed agent |

Modules: [ai-gateway](modules/ai-gateway/README.md),
[foundry-models](modules/foundry-models/README.md),
[foundry-agents](modules/foundry-agents/README.md).

The root additionally provides **opt-in** Foundry model-access grants, a separate
project-only tool-access grant, an explicit-endpoint RemoteTool reference and a
nonsecret JSON environment adapter. A tool role does not create a ToolServer,
deliver a credential or establish working tool invocation.
An independent monitoring opt-in changes the existing Insights connection to
Bicep's managed-identity body in place and adds two resource-scoped publisher
grants, without creating a second connection owner.
These settings remain off by default and do not implement gateway OpenTelemetry.
See the
[integration inputs and adapter](docs/architecture.md#optional-application-integration)
and [GET-only live qualification runner](docs/live-readback.md).

See [ownership, state and API differences](docs/architecture.md) and the
[validation and acceptance guide](docs/evidence-map.md). ToolServer,
Toolbox, credential delivery, automatic azd integration and hosted
application/routine deployment remain subsequent increments; the
[tool contract boundary](docs/tool-credential-boundary.md) explains why existing
credential hooks are not reused. Telemetry
configuration alone is not delivery proof; the evidence map distinguishes the
verified gateway requests from untested hosted-agent tracing.
