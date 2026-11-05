# Terraform: API2026 infrastructure baseline

A self-contained, fresh-deployment Terraform alternative for the standalone
AI Gateway and Foundry support infrastructure. Existing Bicep, application and
`azure.yaml` defaults are unchanged.

**Status, November 5, 2026:** bounded infrastructure and local application-client
checks passed, as did the full application/container CI. **Full hosted-agent/azd
parity is not accepted.** The latest infrastructure checkpoint returned
37 successful resource GETs and ten matched roles, with five requested fields
omitted by Azure readback; full requested-body acceptance remains incomplete.
The actual application client passed one key-auth Responses request, not hosted
identity or tool execution. See the single
[current acceptance summary and remaining gates](docs/evidence-map.md#current-acceptance-november-5-2026);
earlier 33- and 35-resource checkpoints remain dated evidence, not the current
combined configuration.

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

The root additionally provides **opt-in** Foundry model-access grants, an
explicit-endpoint RemoteTool reference and a nonsecret JSON environment adapter.
An independent monitoring opt-in changes the existing Insights connection to
Bicep's managed-identity body in place and adds two resource-scoped publisher
grants, without creating a second connection owner.
Defaults still create the same 33-resource foundation. See the
[integration inputs and adapter](docs/architecture.md#optional-application-integration)
and [GET-only live qualification runner](docs/live-readback.md).

See [ownership, state and API differences](docs/architecture.md) and the
[source capability/test/proof map](docs/evidence-map.md). ToolServer,
Toolbox, credential delivery, automatic azd integration and hosted
application/routine deployment remain subsequent increments; the
[tool contract boundary](docs/tool-credential-boundary.md) explains why existing
credential hooks are not reused. Telemetry
configuration alone is not delivery proof; the evidence map distinguishes the
verified gateway requests from untested hosted-agent tracing.
