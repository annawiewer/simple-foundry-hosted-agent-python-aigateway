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
Gateway telemetry defaults to a pending first stage. Follow the
[native telemetry guide](native-telemetry.md) to obtain the explicit readiness
handoff and complete a fresh second-stage plan with the same root/workspace
and original inputs. Do not use the initial plan as a completed exporter plan.

## Ownership and graph

| Owner | Scope |
|---|---|
| Composition root | Naming/tags, three new workload groups, module composition, default Foundry gateway grants, optional RemoteTool and outputs |
| [foundry-models](../modules/foundry-models/README.md) | Model account, serialized deployments, backend filters and optional developer grants |
| [ai-gateway](../modules/ai-gateway/README.md) | Gateway/identity, key resource, monitoring/exporter, backend grant, provider/catalog/aliases and selected model callers |
| [foundry-agents](../modules/foundry-agents/README.md) | Account/project, Storage/ACR, monitoring, internal grants and three support connections |
| Explicit [tool runner](toolchain.md), outside Terraform | Whole GitHub ToolServer/credential lifecycle and one Foundry Toolbox; no overlapping connection writer |
| External owner | Referenced existing model resources, outbound subnet/private connectivity and optional backend pregrant |

The service owns the default gateway workspace. The root configures providers;
child modules only declare requirements. All configuration dependencies are
bundled here.

```text
root -> model account -> serialized deployments -> backend descriptor
root -> gateway + identity
gateway monitoring -> GET-only readiness handoff -> fresh plan -> DCR grant -> exporter
backend descriptor + gateway identity -> backend grant -> provider -> catalog -> aliases
root -> agent account/project -> support grants -> Storage/ACR connections
tool runner -> ToolServer -> explicit endpoint handoff -> Terraform RemoteTool -> tool runner Toolbox
```

The gateway owns its backend grant to avoid a sibling-module RBAC cycle.
Stable keys, not computed IDs, select resource instances. Role creation does
not establish propagation or runtime authorization.

## Root inputs and outputs

| Input | Behavior |
|---|---|
| `model_deployments`, `model_aliases` | Null selects the bundled [profile](../model-profile.json). Custom deployment keys need compatible aliases. Root null aliases select the profile, unlike the gateway module's per-deployment default. |
| `gateway_access_principals` | Explicit gateway-scoped Models User callers; no tool grant |
| `gateway_telemetry_mode`, `gateway_native_telemetry` | Default `OpenTelemetry` with null handoff leaves export pending. The [staged path](native-telemetry.md) creates the DCR publisher/exporter; explicit `ApplicationInsights` retains legacy compatibility. |
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
The separate root-only `gateway_toolchain_bootstrap` output carries the exact
gateway/project and selected connection metadata to the opt-in tool runner.
No new tool resource, role or default behavior is introduced by this output.

## Optional application integration

The application root enables model access, project-only tool access, Foundry
monitoring and registry sharing by default. Each can be disabled independently.
Reusable modules and standalone examples retain their minimal defaults.
These settings do not deploy an application or provision its tools.

| Setting | Root default | Managed change |
|---|---|---|
| `enable_foundry_gateway_model_access` | `true` | Two root-owned gateway-scoped Models User grants for the agent account/project. Do not duplicate those grants in `gateway_access_principals`. |
| `enable_foundry_gateway_tool_access` | `true` | One root-owned gateway-scoped Tools User grant for the project only. No account/developer tool permission or ToolServer creation. |
| `enable_foundry_monitoring_integration` | `true` | In-place project Insights connection switch to managed identity and account/project publisher grants at the agent Insights scope. No second connection owner. |
| `share_foundry_registry_connection` | `true` | Mark the existing project-managed-identity registry connection shared, matching Bicep. Registry admin stays disabled; project AcrPull stays registry-scoped. |
| `gateway_remote_tool_endpoint` | `null` | Explicit service-established HTTPS MCP URL on this gateway; creates the project-owned shared `aigw-github` RemoteTool with managed-identity auth. No guessed URL, credential or Toolbox. |

**Upgrading an existing root:** omitted switches now select five additional
scoped grants and managed-identity/shared-connection bodies. Review a fresh plan
against the original inputs; names and Terraform resource addresses are unchanged.
To omit these application integrations, explicitly set:

```hcl
enable_foundry_gateway_model_access   = false
enable_foundry_gateway_tool_access    = false
enable_foundry_monitoring_integration = false
share_foundry_registry_connection     = false
```

These switches do not disable the bundled root profile's `Medium` gateway model
content safety. To retain previous policy omission, supply a complete deployment
map with null severities; see [content-safety defaults and opt-outs](../README.md#model-content-safety).

Changing these values on an already configured deployment can remove grants or
change connection authentication/sharing. No state adoption or automatic
migration is included. The nonsecret contract reports the selected settings,
including `integration.registry_connection_shared`.

A selected RemoteTool waits for the selected tools grant, not for proven
propagation. Model access is independent. The connection API remains
`2025-06-01`, with provider schema validation disabled for its auth contract.
The monitoring option affects **Foundry agent monitoring**, not the gateway's
separate native OpenTelemetry stages. Omitting ApiKey credentials in the
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
| Gateway/MCP safety | The bundled root selects `Medium` on all models; explicit profiles allow overrides/omission and standalone defaults remain opt-in. The external tool runner also requests Medium for MCP. Selected-API enforcement remains unqualified. Backend `Microsoft.DefaultV2` is a separate control. |
| Backend filtering | Terraform pins `Microsoft.DefaultV2`; Bicep omits `raiPolicyName`. Omission is not proof of the effective default. |
| Model request rate | The bundled profile requests 100 calls/minute per identity; Bicep has no default request-rate policy. An explicit replacement profile can omit it. |
| Model account | Terraform retains `allowProjectManagement = true`, versus false in Bicep; no live mutation is included. |
| Registry sharing | Shared by default in the application root, matching Bicep; standalone support remains unshared. Hosted image pulls still need runtime acceptance. |
| Foundry access/monitoring | Enabled by default in the application root, with narrower separate model/tool roles instead of broad AI Gateway User grants |
| Insights connection | One project-level Terraform owner, using managed identity by default in the application root; not a claim of identical Bicep account-level topology |
| Gateway telemetry | Native OpenTelemetry is a two-stage Terraform path with an external GET-only readiness helper, not the Bicep mutation hook. Explicit legacy mode remains available; selected-API provisioning, delivery and Portal dashboard acceptance remain outstanding. |
| Tool/application lifecycle | An external explicit-credential runner now creates/inspects tools and rotates their credential without Terraform secret state. It requires exclusive ownership; creation is not atomic. Automatic azd orchestration and full live acceptance remain outstanding. |

Do not run Bicep mutating hooks against Terraform-owned resources. Exporter
kind migration can require deletion/recreation and is not automatic or approved
by these source changes. State adoption, live credential rotation/recovery and
teardown need separately reviewed ownership-aware procedures. Do not remove `prevent_destroy`
or mutate state to bypass a stop.
