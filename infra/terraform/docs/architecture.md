# Preparation, contracts and ownership

One Terraform composition root calls three independent capability modules.
It is an alternative infrastructure path, not yet the complete Bicep/azd
hosted-agent workflow. See the [acceptance matrix](evidence-map.md#acceptance-matrix).

## Offline and deployment preparation

From the repository root, use PowerShell 7, Python 3 and Terraform 1.11.4 with
the checked-in AzAPI 2.13.0 locks:

```powershell
pwsh -NoProfile -File infra\terraform\scripts\Test-Offline.ps1

$TerraformRoot = 'infra\terraform'
# Or one directory under infra\terraform\examples.
Copy-Item "$TerraformRoot\terraform.tfvars.example" "$TerraformRoot\terraform.tfvars"
```

Do not overwrite existing deployment inputs. The runner uses mocked providers,
backend-disabled initialization and read-only locks. It makes no Azure calls;
registry access may be needed for uncached providers. Use host-native path
separators on non-Windows systems.

Replace the synthetic subscription and choose unique names. Qualify service
enablement, locations, model versions/SKUs and quota for the actual target.
The full root requires `subscription_id`, `location` and `gateway_location`.
Examples require `subscription_id` and `location`; `existing-models` also needs
its real backend descriptor.

Before Azure-enabled planning, select fresh state and an authorized target.
Do not reuse old wrapper state, backend keys or deployed names. Authenticate a
principal permitted to create the declared resources and scoped roles; keep
credentials out of tfvars, command output and Git. Each independent example
needs unique names and its own state/backend key.

Local state is the single-operator default. Shared use requires a separately
reviewed remote backend with authenticated, locked storage; no backend bootstrap
is included. State, saved plans and `.terraform` data can contain connection
strings even though the published outputs are nonsecret.

After reviewing the target and ownership:

```powershell
terraform "-chdir=$TerraformRoot" init -input=false -lockfile=readonly
terraform "-chdir=$TerraformRoot" plan -input=false
```

These are Azure-enabled commands, not part of the offline check. Review the
current plan before authorizing apply; no automatic deployment is implied.

## Ownership and graph

| Owner | Scope |
|---|---|
| Composition root | Naming/tags, three new workload groups by default, module composition, optional Foundry gateway grants/RemoteTool and outputs |
| [foundry-models](../modules/foundry-models/README.md) | Model account, serialized deployments, backend filters and optional developer grants |
| [ai-gateway](../modules/ai-gateway/README.md) | Gateway/identity, key resource, monitoring/exporter, backend grant, provider/catalog/aliases and selected model callers |
| [foundry-agents](../modules/foundry-agents/README.md) | Account/project, Storage/ACR, monitoring, internal grants and three support connections |
| External owner | Referenced existing model resources, outbound subnet/private connectivity and optional backend pregrant |

The service owns the default gateway workspace. The root configures providers;
child modules only declare requirements. All configuration dependencies are
bundled here.

```text
root -> model account -> serialized deployments -> backend descriptor
root -> gateway + identity
backend descriptor + gateway identity -> backend grant -> provider -> catalog -> aliases
root -> agent account/project -> support grants -> Storage/ACR connections
```

The gateway owns its backend grant to avoid a sibling-module RBAC cycle.
Stable keys, not computed IDs, select resource instances. Role creation does
not establish propagation or runtime authorization.

## Root inputs and outputs

| Input | Behavior |
|---|---|
| `model_deployments`, `model_aliases` | Null selects the bundled [profile](../model-profile.json). Custom deployment keys need compatible aliases. Root null aliases select the profile, unlike the gateway module's per-deployment default. |
| `gateway_access_principals` | Explicit gateway-scoped Models User callers; no tool grant |
| `developer_principal_id`, `developer_principal_type` | Optional model/agent developer grants, not gateway tool access |
| `api2026_resource_group_name` | Optional single **new owned** group; not adoption, consolidation or migration |
| `gateway_backend_subnet_id` | Existing creation-only outbound subnet, delegated to `Microsoft.App/environments` in the gateway region; no private ingress or network provisioning |
| `standalone_backend_public_network_access` | Disabling backends requires the outbound subnet and independently working private connectivity |
| `agent_storage_public_network_access` | Storage-only override; otherwise inherits the global setting, then Enabled. Disabled creates no private endpoint/DNS or working hosted-compute path. |
| `backend_revision` | Deliberately changes backend names/replacement without renaming the gateway; not automatic recovery |

[`outputs.tf`](../outputs.tf) defines the nonsecret version-1
`deployment_contract`: IDs, endpoints, principals, aliases, selected integration
metadata and deferred ownership. It contains no runtime key value, GitHub
credential or invented ToolServer/Toolbox endpoint. Use `gateway_api_versions`
for actual API pins. Historical `2026` compatibility labels, naming salts and
`api2026_resource_group_name` are retained to avoid renaming existing resources;
they are not API-version selectors.

## Optional application integration

These options remain off/null by default. Enabling one does not enable the
others or deploy an application.

| Setting | Managed change |
|---|---|
| `enable_foundry_gateway_model_access = true` | Two root-owned gateway-scoped Models User grants for the agent account/project. Do not duplicate those grants in `gateway_access_principals`. |
| `enable_foundry_gateway_tool_access = true` | One root-owned gateway-scoped Tools User grant for the project only. No account/developer permission expansion or ToolServer creation. |
| `gateway_remote_tool_endpoint` | Explicit service-established HTTPS MCP URL on this gateway; creates the project-owned shared `aigw-github` RemoteTool with managed-identity auth. No guessed URL, credential or Toolbox. |
| `enable_foundry_monitoring_integration = true` | In-place project Insights connection switch to managed identity and account/project publisher grants at the agent Insights scope. No second connection owner. |

A selected RemoteTool waits for the optional tools grant, not for proven
propagation. Model access is independent. The connection API remains
`2025-06-01`, with provider schema validation disabled for its auth contract.
The monitoring option affects **Foundry agent monitoring**, not the gateway's
missing native OpenTelemetry integration. Omitting ApiKey credentials in the
managed-identity body does not establish stored credential erasure.

The [environment adapter](../scripts/export_environment.py) accepts a nonsecret
version-1 contract or an explicitly nonsensitive `terraform output -json`
envelope:

```powershell
python -B infra\terraform\scripts\export_environment.py .\deployment-contract.json
```

It prints an allow-listed JSON mapping for review. It never calls Azure,
Terraform or azd, writes an env file, selects credentials or runs hooks.
For custom profiles, use `--model-alias-key` and `--mini-model-alias-key`.
Both selected aliases must support `/openai/v1/responses`; Chat-Completions-only
aliases are rejected because the shared application uses Responses.

The adapter checks gateway group/ID and agent account/project ID/URL
relationships. Gateway and registry hostname syntax is not independent proof
of resource ownership; service-generated registry hostnames remain valid.
No GitHub credential/repository, Toolbox value or runtime readiness is supplied.
Do not pass state as adapter input.

## Preserved contracts and deliberate differences

Gateway, catalog, aliases, key and telemetry resources now use
`2025-09-01-preview`, aligned with the [upstream gateway Bicep](../../ai-gateway/main.bicep).
Foundry account/project/deployment resources use `2025-04-01-preview`.
The gateway SKU remains omitted. Preview deployment/API availability still
requires target-specific qualification; an earlier 2026 deployment is not proof.
This source change does not migrate or alter that deployment.

The gateway retains create-only headers, backend-replacement semantics and
`prevent_destroy`. This is not an Azure deletion lock. Alias body changes still
require replacement; model deployments serialize on their account.

| Surface | Remaining difference or decision |
|---|---|
| Gateway/MCP safety | Severity inputs remain locally gated pending selected-API qualification. Backend `Microsoft.DefaultV2` is a separate control; neither configuration proves enforcement. |
| Backend filtering | Terraform pins `Microsoft.DefaultV2`; Bicep omits `raiPolicyName`. Omission is not proof of the effective default. |
| Model request rate | The bundled profile requests 100 calls/minute per identity; Bicep has no default request-rate policy. An explicit replacement profile can omit it. |
| Model account | Terraform retains `allowProjectManagement = true`, versus false in Bicep; no live mutation is included. |
| Registry sharing | Terraform's connection is unshared, versus shared in Bicep. Full-hosted behavior still needs resolution and acceptance. |
| Foundry access/monitoring | Explicit opt-ins instead of default full-application wiring; narrower separate model/tool roles instead of broad AI Gateway User grants |
| Insights connection | One project-level Terraform owner, optionally using managed identity; not a claim of identical Bicep account-level topology |
| Gateway telemetry | Legacy ApplicationInsights exporter, payload capture off. Native OpenTelemetry, generated-DCR readiness/scoped publisher role and Portal dashboard acceptance remain outstanding. |
| Tool/application lifecycle | No automatic Terraform ToolServer/Toolbox or azd workflow. Credential selection/upload must be explicit. |

Do not run Bicep mutating hooks against Terraform-owned resources. Exporter
kind migration can require deletion/recreation and is not automatic or approved
by this API-pin change. State adoption, rotation, recovery and teardown need
separately reviewed ownership-aware procedures. Do not remove `prevent_destroy`
or mutate state to bypass a stop.
