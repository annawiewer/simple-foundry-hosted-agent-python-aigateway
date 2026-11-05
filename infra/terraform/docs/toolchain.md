# GitHub tools for the Terraform application path

The optional [tool runner](../scripts/configure_tools.py) connects the GitHub
tool service to the Terraform-created Foundry project. It is separate from
Terraform and azd so GitHub credentials never enter Terraform arguments, state
or plans. The original Bicep application path is unchanged.

**This is source-tested automation, not live acceptance.** Creating a ToolServer
uploads the explicitly selected credential to Azure; creating a Toolbox writes
to Foundry. Review and authorize the actual target and credential separately.
Do not run these commands against the earlier protected deployment or reuse
saved plans. The [acceptance matrix](evidence-map.md) distinguishes offline
coverage from provisioning, credential handling and real tool invocation.

## Owners and limits

| Component | Sole writer |
|---|---|
| Gateway, Foundry project, roles and `aigw-github` RemoteTool connection | Terraform |
| Complete `github` ToolServer, policies and selected GitHub credential | This explicitly invoked runner |
| One named Toolbox and its initial version | This explicitly invoked runner |
| Application/azd environment, runtime gateway key, agent and routine | Not changed by this runner |

Never run the Bicep configuration hooks over these resources. Do not add a
Terraform ToolServer stub or put credentials in tfvars, JSON inputs or receipts.
The runner does not call `gh`, `listSecrets`, azd, role-assignment APIs, inference
or tool invocation. It does not install dependencies, change CLI context,
register providers, delete resources, adopt existing resources or migrate state.

**Exclusive ownership is a prerequisite, not a service lock.** The selected
2025 ToolServer API does not enforce `If-None-Match` on creation. A preceding
GET cannot prevent another writer racing the PUT. Toolbox creation is also a
GET followed by a non-idempotent version POST. The operator must exclude
competing Bicep, Terraform, hook and manual writers before confirming ownership.
Existing names are rejected, even if they look compatible. Credential rotation
uses the fresh specific ETag and rejects drift; live ETag enforcement still
requires qualification.

Every invocation requires a new append-only `.jsonl` receipt in an existing
private directory. A durable intent is written before a mutation. Keep the
latest receipt, including failures: it binds the owner, configuration, target,
ETag and known Toolbox version. Receipts are not secrets or Terraform state,
but contain deployment metadata and should remain outside Git.

## Before running

Use the full application root, Python 3 and an existing Azure CLI login for the
explicit subscription, tenant and public Azure cloud. No extra Python package
or gateway CLI extension is required. The root must already be deployed under
reviewed ownership, with project tool access enabled.
The caller also needs existing ToolServer management and Foundry Toolbox
data-plane permissions. The runner does not grant them automatically.

Select a repository-restricted, read-only GitHub credential through your approved
secret-handling process. Populate a named environment variable without putting
the value in shell history. The runner reads only the variable explicitly named
by `--credential-env`; it never retrieves the current GitHub CLI login.
`--confirm-read-only-credential` is an operator attestation, **not an automated
permissions audit**. Neither a token prefix nor `X-MCP-Readonly` proves least
privilege. The configured tools are `list_pull_requests`, `list_issues` and
`actions_list`; the credential must restrict which repositories they can read.

The runner sets Medium gateway tool content safety. Optional
`--allow-client-cidr` arguments select an MCP-only IP allow list; repeat the flag
for multiple IPv4/IPv6 ranges. Omitting it allows all caller IPs at that policy
layer. The model-only Terraform `model_allowed_client_cidrs` input is deliberately
not reused. Rotation preserves the complete original tool configuration rather
than changing policies, tools, backend or IP rules.

## 1. Export the applied bootstrap

These are illustrative PowerShell commands for a separately approved deployment.
Set the paths and IDs for that deployment; use host-native paths on other systems.

```powershell
$TerraformRoot = (Resolve-Path '.\infra\terraform').Path
$Runner = Join-Path $TerraformRoot 'scripts\configure_tools.py'
$Private = 'C:\private\my-new-deployment' # An existing private directory.
$Subscription = '<approved-subscription-uuid>'
$Tenant = '<approved-tenant-uuid>'
$Bootstrap = Join-Path $Private 'tools.bootstrap.json'

$Document = terraform "-chdir=$TerraformRoot" output -json gateway_toolchain_bootstrap
if ($LASTEXITCODE -ne 0) { throw 'Bootstrap export failed.' }
$Document | Out-File -LiteralPath $Bootstrap -Encoding utf8 -NoClobber
```

Use this named, nonsecret output, not a state file or the entire Terraform output.
The helper verifies its API, IDs, workspace, project endpoint and selected CLI
subscription/tenant. It will not switch your account for you.

## 2. Create the GitHub ToolServer

After explicit approval to upload the selected credential:

```powershell
$ServerReceipt = Join-Path $Private 'toolserver.created.jsonl'
$ToolVariables = Join-Path $Private 'tools.ready.tfvars.json'

python -B $Runner create-toolserver `
  --bootstrap $Bootstrap --subscription-id $Subscription --tenant-id $Tenant `
  --repository '<owner/repository>' `
  --credential-env SELECTED_GITHUB_MCP_TOKEN `
  --confirm-read-only-credential --confirm-exclusive-owner `
  --receipt $ServerReceipt --tfvars $ToolVariables
if ($LASTEXITCODE -ne 0) { throw 'Stop and inspect the retained receipt.' }
```

This performs one PUT only after the precise missing-ToolServer response. It
then uses bounded GETs to check the owner and complete nonsecret configuration.
It requires credential headers to be absent/empty on ordinary GET. Returned
header values, including masked values, stop the flow for separate qualification.
The full PUT response is not projected, and raw HTTP/CLI errors are not logged.

Only the service-returned `properties.mcpEndpointUrl`, on the declared gateway
origin, is exported as `gateway_remote_tool_endpoint`. Its path and case are
preserved; the runner does not invent a route. No handoff is emitted on failed
readback. `configured` means matching nonsecret readback, not a working MCP call,
effective credential permissions or clean cloud diagnostic logs.

## 3. Let Terraform create its connection

Review a fresh plan using **all original inputs** plus the new explicit
`tools.ready.tfvars.json`. Retain any existing native-telemetry handoff and other
overrides. Do not let an omitted input undo earlier integration or monitoring.
The planned change should be the existing root-owned RemoteTool connection and
any other deliberately reviewed changes, not a second ToolServer owner.

After separately authorizing and applying that current configuration, export
`gateway_toolchain_bootstrap` again to a new `tools.connected.json` file using
the same guarded export pattern. That new output must identify the applied
`aigw-github` connection and the verified tool endpoint.

## 4. Create the Toolbox and review its runtime values

```powershell
$ConnectedBootstrap = Join-Path $Private 'tools.connected.json'
$BoxReceipt = Join-Path $Private 'toolbox.created.jsonl'
$RuntimeValues = Join-Path $Private 'tools.runtime.review.json'

python -B $Runner create-toolbox `
  --bootstrap $ConnectedBootstrap --subscription-id $Subscription --tenant-id $Tenant `
  --previous-receipt $ServerReceipt --toolbox-name repo-digest `
  --confirm-exclusive-owner --receipt $BoxReceipt --environment-json $RuntimeValues
if ($LASTEXITCODE -ne 0) { throw 'Stop and inspect the retained receipt.' }
```

Before creating anything, the runner rechecks the ToolServer and the actual
Terraform-managed RemoteTool authentication, audience and target. It makes one
Foundry version POST, retains the returned version, and checks its default
version, ownership metadata and single MCP tool entry. It uses the same
connection reference and `require_approval: never` entry as the shared
[`toolbox.yaml`](../../../toolbox.yaml); that setting relies on your separately
reviewed read-only credential and tool restriction.

The Toolbox endpoint follows the canonical Foundry versioned route using the
validated project, name and service-returned version. This is different from the
ToolServer endpoint, which is taken directly from its GET response.
The review JSON contains only `TOOLBOX_NAME`, `TOOLBOX_ENDPOINT` and
`GITHUB_REPOSITORY`. It is not automatically imported into azd or the application.
No role is granted and no application key is retrieved. Hosted deployment and
the opt-in Terraform azd flow remain subsequent work.

## Rotation and uncertain outcomes

For rotation, explicitly select the replacement read-only credential and use
the **latest** receipt, preferably the Toolbox receipt so its version is retained:

```powershell
python -B $Runner rotate-credential `
  --bootstrap $ConnectedBootstrap --subscription-id $Subscription --tenant-id $Tenant `
  --previous-receipt $BoxReceipt `
  --credential-env SELECTED_REPLACEMENT_GITHUB_TOKEN `
  --confirm-read-only-credential --confirm-exclusive-owner `
  --receipt (Join-Path $Private 'toolchain.rotated.jsonl')
if ($LASTEXITCODE -ne 0) { throw 'Stop and inspect the retained receipt.' }
```

Rotation requires the current readback/ETag to match the receipt and resends the
whole owned configuration with the new credential. Changed policies, extra
sources, missing/conflicting ETags or a changed frontend endpoint cause a stop.
It never reads the old secret, retries a write or creates another Toolbox version.
After runtime verification, revoke the old GitHub credential through its issuer;
this helper does not revoke or roll back credentials.

If a request times out, is interrupted or cannot be verified, **do not rerun
create**. The server might already have applied it. Use `inspect-toolserver` or
`inspect-toolbox` with the failed receipt and a new receipt path. These operations
make only Azure GETs, plus normal Azure CLI authentication; they do not retrieve
GitHub credentials or perform automatic repair.

```powershell
python -B $Runner inspect-toolserver `
  --bootstrap $ConnectedBootstrap --subscription-id $Subscription --tenant-id $Tenant `
  --previous-receipt (Join-Path $Private 'toolchain.rotated.jsonl') `
  --receipt (Join-Path $Private 'toolchain.inspected.jsonl')
```

A partial last journal line is treated as unconfirmed; a complete earlier intent
must exist. Wrong owners/configuration, unknown resources, changed Toolbox
defaults or missing receipts require manual review, not implicit adoption.
Use `inspect-toolbox` with the latest retained Toolbox handle to verify it after
rotation. Optional `--tfvars` and `--environment-json` handoffs are exclusive
new files; no automatic Terraform variable file is accepted. A failed handoff
write is recoverable by inspection, not by repeating the cloud mutation.
The total deadline is 300 seconds by default, configurable up to 600 seconds.
ToolServer readiness is limited to 30 GETs. No deletion or teardown is automated.

See the [contract sources and remaining acceptance gates](tool-credential-boundary.md)
before any live qualification.
