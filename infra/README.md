# Infrastructure

## Choose a deployment path

Both choices compose the model account, agent support and AI Gateway for the
same [Python application](../repo_digest_agent.py). Their entry points and
deployment ownership are deliberately separate:

| Path | Infrastructure entry | Application and tools | Guide |
|---|---|---|---|
| **Bicep + azd** (default) | [`main.bicep`](main.bicep), selected by the root [`azure.yaml`](../azure.yaml) | azd services and the [configuration/lifecycle hooks](scripts/README.md) | [Repository setup](../README.md#prerequisites) and [Bicep workflow](#bicep-workflow) |
| **Terraform** | The `.tf` files in [`terraform/`](terraform/README.md), composed by [`main.tf`](terraform/main.tf) | Explicit telemetry/tool handoffs and a separate app-only deployment; schedule opt-in | [Preparation and state](terraform/docs/architecture.md#offline-and-deployment-preparation), then [guided application flow](terraform/docs/application-flow.md) |

### Why the workflows differ

Bicep describes ARM resources; azd also runs imperative hooks and deploys the
application. Provisioning only `main.bicep` does not perform those later steps.
Terraform's state maps its resource addresses to the Azure objects it owns;
`plan` proposes changes and an explicitly authorized `apply` executes them.
Keep that state private and use separate state/backend keys for independent
deployments. The [state guidance](terraform/docs/architecture.md#offline-and-deployment-preparation)
explains this repository's local-state default and shared-backend boundary.

These are alternative owners, not interchangeable wrappers for an existing
deployment. Do not provision both against the same resources or expect a naming
override to adopt/migrate them. Terraform does not own every ToolServer, Toolbox,
hosted application or routine through its state, so `terraform destroy` is not
a complete application teardown. Review the
[ownership and deliberate differences](terraform/docs/architecture.md#preserved-contracts-and-deliberate-differences)
and [acceptance boundaries](terraform/docs/evidence-map.md) before deployment.
Matching architecture does not establish matching live SKU, pricing or every
policy's enforcement.

For smaller Terraform compositions, use the
[independent examples](terraform/README.md#start-here); reusable modules live
under `terraform/modules/`. No Bicep or Terraform directory move is required
to select either workflow.

## Bicep workflow

Run the remaining Bicep commands in this README from the `infra/` directory.

The subscription-scoped [`main.bicep`](main.bicep) template creates three
resource groups and deploys one module into each:

- [`foundry-models/`](foundry-models/README.md) creates a model-only Azure AI
  Services account and the GPT deployments.
- [`foundry-agents/`](foundry-agents/README.md) creates the Foundry project and
  hosted-agent runtime dependencies.
- [`ai-gateway/`](ai-gateway/README.md) creates AI Gateway, model registrations,
  and aliases.

The [`scripts/`](scripts/README.md) directory contains the preprovision,
postprovision, and postdown lifecycle hooks. `azd provision` runs the
preprovision and postprovision hooks from `azure.yaml`; postprovision configures
the GitHub MCP ToolServer and Foundry Toolbox after Bicep creates the Azure
resources.

## AI Gateway policies

By default, each model has a `tokenLimit` of 1,000 tokens per minute per unit
of deployment capacity (20,000 for `gpt-latest` and `gpt-6-sol`; 200,000 for
`gpt-mini-latest`), a `$10.00/month` `costLimit` per caller identity
(`monthly-caller-budget`), and `Medium` `contentSafety` thresholds for Hate,
Self-Harm, Sexual, and Violence. The same content-safety thresholds are applied
to the `toolServers/github` MCP server. You can also pass optional
`backendSubnetResourceId` (`properties.backend.subnet.id`, delegated to
`Microsoft.App/environments`) for outbound VNet integration and
`allowedCallerCidrRanges` for inbound caller IP filtering (`ipFilter`). The
`gpt-latest` alias assigns priority 0 to `gpt-6.1-sol`, priority 1 to `gpt-6-sol`,
and priority 2 to `gpt-5.4-mini`. Priority is not guaranteed error-triggered
failover; see the [routing boundary](../IMPLEMENTATION_NOTES.md#regions-and-model-defaults).
Policy configuration alone also does not prove rejection or provide an Azure
billing ceiling. See the [AI Gateway module
README](ai-gateway/README.md) for module usage and configuration.

## Deploy the full stack

`azd provision` also works from `infra/`: azd walks up to find
[`../azure.yaml`](../azure.yaml), then provisions the full stack and runs its
preprovision and postprovision hooks:

```bash
azd provision
```

Alternatively, deploy the subscription-scoped Bicep template directly:

```bash
az deployment sub create \
  --location eastus2 \
  --template-file ./main.bicep \
  --parameters environmentName=dailydigest \
               location=eastus2 \
               principalId="$(az ad signed-in-user show --query id -o tsv)"
```

The direct deployment creates the Azure resources but does not run azd hooks.
For GitHub MCP and Toolbox setup after a direct deployment, see
[`scripts/README.md`](scripts/README.md) and provide the deployment outputs to
the configuration script.

## Deploy individual modules

Each resource-group-scoped template can also be deployed independently. Create
its resource group first, then follow the module-specific parameters and
examples:

- [Foundry model account and deployments](foundry-models/README.md)
- [Foundry project and hosted-agent runtime](foundry-agents/README.md)
- [AI Gateway and model routing](ai-gateway/README.md)
- [Lifecycle and postprovision scripts](scripts/README.md)
