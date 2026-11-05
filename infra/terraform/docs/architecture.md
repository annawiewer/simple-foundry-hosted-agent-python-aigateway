# Contracts, preparation and ownership

This root packages the historical API2026 gateway/model foundation. It does not
migrate the old wrapper or implement the full Bicep-backed application workflow.
See the [evidence map](evidence-map.md) for separate historical and fresh proof
boundaries.

## Offline and deployment preparation

Use this one route from the repository root in PowerShell 7. Examples use the
same route, changing only `$TerraformRoot` to the chosen example directory.
Use Terraform 1.11.4, Python 3 and the checked-in AzAPI 2.13.0 locks; do not
upgrade providers as part of initialization.

```powershell
pwsh -NoProfile -File infra\terraform\scripts\Test-Offline.ps1

$TerraformRoot = 'infra\terraform'
# For example: 'infra\terraform\examples\gateway-only'
Copy-Item "$TerraformRoot\terraform.tfvars.example" "$TerraformRoot\terraform.tfvars"
```

The runner is credential-free, not necessarily air-gapped: it initializes
with backend disabled and read-only locks, checks formatting/validation, and
runs provider-mocked contract tests. It does not deploy, invoke models or prove
Azure/telemetry/application behavior. Keep the synthetic test inputs separate
from real deployment inputs. On a non-Windows host use host-native separators;
only claim platforms actually exercised by the current validation result.

Edit the copied file locally. Replace the synthetic subscription, choose a
unique environment name, and qualify service enablement, regions, model
versions/SKUs and quota. The full root requires `subscription_id`, `location`
and `gateway_location`; examples require `subscription_id` and `location`.
Examples intentionally place their component and monitoring in one region.
Existing-models also requires its actual backend descriptor.

Before any Azure-enabled initialization/plan:

- Select a **fresh** environment and state location; never reuse an old wrapper
  state, backend key or deployed resource names.
- Choose authenticated AzAPI credentials and a principal permitted to create
  the declared resources and scoped role assignments. No token/key belongs in
  checked-in tfvars, backend files, command output or examples.
- Review ownership, cost and destructive boundaries. Local state is the
  supplied single-operator default. For shared/long-lived use, separately
  provide a reviewed remote-backend declaration/configuration backed by
  pre-existing authenticated, locked storage; this contribution supplies no
  backend bootstrap or backend block. Three workload groups do not require
  three states.
- Protect local state, plans and `.terraform` data. AppInsights connection
  strings occur in managed payloads; nonsecret outputs do **not** make state
  or saved plans secret-free.

After that review and explicit target authorization, the Terraform-native
preparation commands are:

```powershell
terraform "-chdir=$TerraformRoot" init -input=false -lockfile=readonly
terraform "-chdir=$TerraformRoot" plan -input=false
```

These are Azure-enabled planning instructions, **not** part of the offline
check or evidence of acceptance. Review the plan before separately authorizing
apply. No automatic apply, credential retrieval or billable probe is provided.
Each example needs its own state/backend key and unique names.

## Ownership and graph

| Owner | Managed scope |
|---|---|
| Root | Naming/tags and three new workload groups by default; calls the three modules; owns optional Foundry gateway grants/RemoteTool reference and publishes outputs |
| `foundry-models` | New model account, serialized deployments, backend filter bindings, optional developer roles |
| `ai-gateway` | Gateway/system MI, runtime-key resource, monitoring/exporter, optional backend grant/provider/catalog/aliases, explicitly selected caller roles |
| `foundry-agents` | Account/project identities, Storage/ACR, monitoring, internal roles and three support connections; optional in-place Insights identity-auth switch and publisher grants |
| External owner | Referenced model account/deployments, existing outbound subnet/private connectivity, optional pregrant |

The service owns the gateway's default workspace. Child modules declare
provider requirements; the initialized root configures the provider and lock.
Root and examples have no dependency on the old source repository.

```text
root groups -> models account -> serialized deployments -> backend descriptor
root groups -> gateway + system identity
backend descriptor + gateway identity -> backend grant -> provider -> catalog -> aliases
root groups -> agent account/project -> support grants -> Storage/ACR connections
```

The grant is deliberately gateway-owned: it orders the provider without a
sibling-module cycle. Computed IDs are values, not `for_each` keys. RBAC resource
completion is not authorization propagation; runtime readiness remains a gate.
The agents module is independent; by default the root grants neither its
account/project gateway invocation nor direct model-backend access.

## Root inputs and outputs

- `model_deployments = null` and `model_aliases = null` select the bundled
  [profile](../model-profile.json), including primary three-tier and direct-mini
  aliases. At this root, null aliases do **not** mean per-deployment aliases.
  Custom deployment keys therefore need a compatible explicit alias map.
- `gateway_access_principals` explicitly opts callers into gateway-scoped Models
  User access. `developer_principal_id`/`developer_principal_type` opt into
  developer grants on the model/agent support resources, not tool access.
- `api2026_resource_group_name` optionally creates **one new owned group** for
  all workloads. It neither adopts an existing group nor reproduces the owned
  private lab, and is not a consolidation/migration switch.
- `gateway_backend_subnet_id` references an existing creation-only **outbound**
  subnet. The module checks `Microsoft.App/environments` delegation and gateway
  region; it does not provision network/DNS/private endpoints or private ingress.
  `standalone_backend_public_network_access = "Disabled"` requires that subnet
  and separately owned working private connectivity. Null keeps backend public
  access enabled and monitoring access unspecified.
- `agent_storage_public_network_access` optionally overrides **only agent
  Storage** (`Enabled`/`Disabled`); null inherits the global backend setting,
  then defaults to `Enabled`. Disabling Storage alone does not require a
  gateway subnet and does not change model/agent accounts, ACR or monitoring.
  It changes Storage access configuration, not private connectivity or runtime
  reachability; the module retains its configured `AzureServices` bypass.
  The fresh live check used this explicit `Disabled` override to align with
  inherited Storage policy, then verified an ordinary no-change plan. It does
  not prove private Storage access or hosted-agent readiness.
- `backend_revision` deliberately changes backend names/replaces resources
  without renaming the gateway; it is not an automatic recovery switch.

`deployment_contract` version 1 is an allow-listed infrastructure handoff:
environment/subscription/location, group names, gateway ID/endpoint/principal/
workspace/API versions/key-resource ID/monitoring IDs, model account/endpoint/
deployment IDs/alias metadata, and agent account/project principals/endpoints/
support and monitoring IDs.
It declares deferred integration and lifecycle ownership. Additive integration
metadata reports the selected access/connection configuration; a supplied
RemoteTool endpoint is not service readiness proof. It contains **no key value,
GitHub token or fabricated ToolServer/Toolbox endpoint**.
Convenience outputs expose the same component IDs/endpoints and configuration
metadata. See [`outputs.tf`](../outputs.tf) for exact shapes.

## Optional application integration

These settings do not change the default 33-resource/six-role graph or the
independence of the three child modules:

- `enable_foundry_gateway_model_access = true` adds two root-owned Models User
  assignments at the exact gateway scope, for the account and project managed
  identities. Both are off by default. Stable account/project keys and direct
  resource references avoid a sibling-module cycle. Do not select the same
  identities again in `gateway_access_principals`; a precondition rejects
  duplicate ownership. Role creation does not prove runtime authorization.
- `gateway_remote_tool_endpoint = null` creates no connection. An explicitly
  selected credential-free HTTPS endpoint on this deployed gateway creates the
  root-owned `aigw-github` project connection, independently of model access.
  Supply a separately established runtime URL: no MCP path is inferred.
  The connection uses upstream `RemoteTool`/`ProjectManagedIdentity`, audience
  `https://azure-api.net/aigateway`, `custom_MCP` metadata and project sharing.
  Its separately pinned `2025-06-01` connection API disables provider schema
  validation for that auth contract; mocks do not establish service acceptance.
  It does not create ToolServer, credentials or Toolbox.
- `enable_foundry_monitoring_integration = true` independently updates the existing
  project-owned `AppInsights` connection to `ProjectManagedIdentity` in place and
  adds two support-module resources: account/project Monitoring Metrics Publisher
  grants at the exact agent Insights scope. Both grants precede the connection;
  no broad module dependency or gateway dependency is introduced. Defaults stay
  unchanged. The standalone support example exposes
  `enable_monitoring_integration`. The connection retains its project parent,
  name, Terraform address and `2025-06-01` API, using Bicep's managed-identity body
  with provider schema validation disabled for its auth
  discriminator. Its metadata uses the existing managed Insights connection
  string, never a new secret action or public output.

The monitoring option deliberately retains one Terraform connection owner and
registry-sharing defaults. Account/project GET routes exposed matching existing
connection bodies and creation times before the proposed second owner was
rejected. The subsequent single-owner update was reflected through both routes
under their existing resource IDs; both service creation timestamps reset.
This supports the single-owner design, not a complete backing-identity or
alias-semantics guarantee.
The opt-in changes auth/metadata and omits ApiKey credentials; it does not prove
credential erasure, identical Bicep topology, Entra-only ingestion or hosted-agent
tracing. Root contract metadata exposes only the selected flag and nullable real
project connection ID.
Monitoring alone gives 35 resources/eight roles; with model access, 37/ten;
with the explicit RemoteTool as well, 38/ten. No network, Insights local-auth,
application or Bicep configuration is changed.

The [explicit adapter](../scripts/export_environment.py) accepts either a
nonsecret `deployment_contract` version-1 object or a `terraform output -json`
envelope with an explicitly nonsensitive contract:

```powershell
python -B infra\terraform\scripts\export_environment.py .\deployment-contract.json
```

It prints only an allow-listed JSON environment mapping for manual review.
It never calls Terraform/Azure/azd, changes the environment, writes an env file
or runs lifecycle hooks. Original version-1 contracts remain supported. Custom
profiles can select `--model-alias-key` and `--mini-model-alias-key`; the chosen
primary and mini aliases must both advertise `/openai/v1/responses`. The
installed shared application's `OpenAIChatClient` sends Responses requests to
`/default/models/openai/v1/responses`. Responses-only aliases are accepted;
Chat-Completions-only aliases are rejected. The bundled aliases advertise both
protocols, so this corrects custom-profile compatibility rather than proving a
default-profile runtime failure.

The adapter checks the existing agent account ID, the project's ARM parent and
its URL's account/project names against the independent IDs, using the current
agents module's account-name subdomain convention. It also checks the gateway
resource group against its ARM ID. Resource identity comparisons are
case-insensitive; the version-1 input shape and exported field set are unchanged.
Registry hostnames and gateway origins are syntax-checked, not independently
bound to their ARM IDs: these fields do not prove that relationship. In
particular, service-owned hash-qualified registry hostnames remain valid; no
`<registry-name>.azurecr.io` equality rule is imposed. Authoritative binding
requires a richer, independently sourced resource-readback/provenance contract,
not a second copy of the supplied hostname.

The mapping supplies established infrastructure IDs, locations, groups,
project/registry endpoints, gateway origin and aliases, **not secrets,
GitHub repository/credentials, Toolbox values or runtime readiness**. Do not
export state as adapter input. The existing app's managed-identity path remains
an acceptance gate. Its inherited key path uses `Api-Key`, whereas the bounded
fresh key probes used `Authorization: Bearer`; exporting nonsecret settings
does not fix or accept that key-auth integration. No app/Bicep/`azure.yaml`
behavior is changed here.

The November 5 (CET) increment applied only the two opt-in model-access roles:
zero existing resources changed or destroyed, all 35 resources/eight scoped
roles read back, and the same exact-input ordinary plan returned no changes.
The adapter produced 17 verified nonsecret fields from the actual updated
outputs. RemoteTool remained null and no environment/azd settings were mutated.
This proves role configuration and output interoperability, **not** managed-
identity invocation, tool access or the inherited application key path.

See [tool and credential ownership](tool-credential-boundary.md) before any
future tool setup. Use the [read-only qualification runner](live-readback.md)
to distinguish observable field agreement from GET-omitted values; neither
the adapter nor a role/connection PUT constitutes full application acceptance.

## Preserved contracts and deliberate differences

- Terraform requirements remain `>= 1.11.0, < 2.0.0`; the tested baseline is
  1.11.4, with AzAPI `~> 2.13.0` locked at 2.13.0.
- Standalone gateway/catalog/aliases/key API is `2026-09-01-preview`;
  ApplicationInsights exporter intentionally retains `2025-09-01-preview`.
  Foundry account/project/deployments use `2025-04-01-preview`.
- Gateway create uses a create-only header, backend changes trigger replacement,
  and `prevent_destroy` stops unreviewed gateway destruction. This is not an
  Azure deletion lock. Alias body changes require replacement because the
  source contract does not support an AzAPI PUT update as equivalent to PATCH.
- Deployment operations serialize per account. Storage/ACR connections wait
  for their actual grants; no whole-module dependency or provisioner hides
  ordering.
- Backend deployments bind `Microsoft.DefaultV2`. Unsupported gateway
  `content_safety_severity` is rejected. This is not equivalent to upstream
  gateway/MCP safety. Configured token/cost/request/IP controls and failover
  routes are retained, but enforcement/failover remain unproven.
- Agent AppInsights uses a project-local, unshared ApiKey connection; registry
  connection is unshared. Upstream monitoring publisher/auth/sharing topology
  is not silently claimed equivalent.
- ApplicationInsights exporter has payload capture disabled. No OTLP exporter
  substitution or telemetry redesign is introduced. Fresh gateway request
  delivery was verified for four exact traces and the expected component;
  hosted-agent tracing remains unproven.

Do not run existing Bicep cleanup/recovery hooks against these Terraform-owned
resources. Migration, credential rotation, interrupted deployment recovery and
full teardown need separately reviewed ownership-aware procedures. Do not remove
`prevent_destroy`, mutate state or delete out of band to bypass an approval stop.
