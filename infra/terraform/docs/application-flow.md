# Guided Terraform application deployment

This opt-in path joins the Terraform infrastructure and tool handoffs to the
shared hosted agent, then separately enables its daily schedule. The root
`azure.yaml` and its Bicep workflow stay unchanged. Terraform still owns the
infrastructure; this is **not** a replacement `azd up` or Terraform apply wrapper.

**Source/offline coverage is not live qualification.** These instructions are
for a separately approved fresh deployment, not the earlier protected state.
The [acceptance matrix](evidence-map.md) records the remaining hosted, credential,
governance and telemetry gates.

## The complete sequence

| Step | Owner and action |
|---|---|
| 1. Infrastructure | Follow the [preparation guide](architecture.md#offline-and-deployment-preparation); review and separately authorize each fresh Terraform plan/apply. |
| 2. Telemetry | Finish the [native telemetry handoff](native-telemetry.md) and fresh second-stage plan/apply, or deliberately retain the supported legacy mode. Pending telemetry stops application preparation. |
| 3. GitHub tools | Follow the [tool guide](toolchain.md): explicit-credential ToolServer creation, fresh Terraform RemoteTool connection plan/apply, then Toolbox creation/readback. |
| 4. Prepare the app | Run the offline `prepare` operation below with the applied contract, connected bootstrap and configured Toolbox receipt. |
| 5. Launch the agent | After separate authorization, select its authentication mode and run `deploy-agent`. No routine is deployed by this step. |
| 6. Enable the schedule | Only after reviewing the agent outcome, explicitly run `enable-schedule`. This activates real scheduled model/tool use. |

Keep **all original Terraform inputs and every applied telemetry/tool handoff**
on subsequent plans. Never reuse saved plans, run Bicep mutation hooks against
these resources or let azd provision the Terraform-owned infrastructure.

## Prerequisites and boundaries

Use Python **3.10+** for this standard-library helper; the copied application
keeps its existing Python 3.13 container and frozen `uv.lock`.
The generated project targets **stable azd 1.37.x**, with exactly **1.0.0**
installed for each of:

- `azure.ai.agents`
- `azure.ai.routines`
- `azure.ai.inspector`
- `azure.ai.projects`
- `azure.ai.connections`
- `azure.ai.toolboxes`

This is the reviewed **source compatibility baseline**, not a claim that those
binaries or a hosted deployment have passed live acceptance. Version checks
use `installedVersion`, never a newer version merely advertised in the catalog.
Older betas, missing dependencies and unreviewed newer versions stop before a
deployment intent. Tool installation/upgrades and an existing azd login must
be handled separately; the helper does not install, log in or switch accounts.
It preserves the caller's CLI profile-directory settings, not ambient
service-principal secrets or GitHub credentials.

The target is the already-provisioned public-cloud project in the supplied
subscription/tenant. The caller needs its existing deployment/build/data-plane
permissions and working network access. The helper sets
`AZD_AGENT_SKIP_ROLE_ASSIGNMENTS=true` to disable the agent extension's automatic
developer-RBAC repair; it does not grant missing permissions. Registry sharing
and project tool access must already be enabled. Managed-identity model access
also requires the corresponding Terraform grant.

Use a private parent directory outside the repository, with appropriate OS
access controls. The helper creates a new child directory but does not certify
Windows ACLs. Use an exclusively owned agent name; its routine name will be
`<agent-name>-daily`. Independently verify that these names are appropriate and
that no routine is already active for the agent before confirming deployment.
The helper does **not** check remote name absence, atomically lock resources,
pause an existing schedule or prevent another actor from changing the agent.
azd may create a new version of an existing named agent and upsert an existing
named routine. Confirmation includes acceptance of that target/name ownership.

## 1. Export and prepare offline

After the final reviewed infrastructure and tool stages, export only the named
nonsecret contract to a new file. The bootstrap and receipt below come from
the tool guide, not from invented endpoint values.

```powershell
$TerraformRoot = (Resolve-Path '.\infra\terraform').Path
$ApplicationFlow = Join-Path $TerraformRoot 'scripts\application_flow.py'
$Private = 'C:\private\my-new-deployment' # Existing, access-controlled directory.
$Subscription = '<approved-subscription-uuid>'
$Tenant = '<approved-tenant-uuid>'
$Contract = Join-Path $Private 'deployment.applied.json'
$ConnectedBootstrap = Join-Path $Private 'tools.connected.json'
$BoxReceipt = Join-Path $Private 'toolbox.created.jsonl' # Or latest configured inspection/rotation receipt.
$ApplicationWorkspace = Join-Path $Private 'hosted-application'

$Document = terraform "-chdir=$TerraformRoot" output -json deployment_contract
if ($LASTEXITCODE -ne 0) { throw 'Contract export failed.' }
$Document | Out-File -LiteralPath $Contract -Encoding utf8 -NoClobber

python -B $ApplicationFlow prepare `
  --workspace $ApplicationWorkspace `
  --subscription-id $Subscription --tenant-id $Tenant `
  --contract $Contract --bootstrap $ConnectedBootstrap --tool-receipt $BoxReceipt `
  --repository '<owner/repository>' --agent-name '<unique-lowercase-agent-name>'
if ($LASTEXITCODE -ne 0) { throw 'Application preparation stopped.' }
```

`prepare` itself makes no CLI or Azure call. It reuses the environment adapter
and tool receipt validators, checks matching context/connection/Toolbox version
and repository, and rejects incomplete outcomes. For custom model profiles,
pass `--model-alias-key` and `--mini-model-alias-key`; both must advertise Responses.
These are local consistency checks, not current Azure readback, endpoint
ownership proof, role propagation or working network/credential verification.

The new workspace contains:

| Artifact | Purpose |
|---|---|
| `azure.yaml` | JSON-form YAML containing only the hosted agent and gated routine, with provision/down guards |
| `app` | Exactly the seven shared Docker/runtime/lock files needed for the hosted build |
| `.azure` | A new azd environment with only the validated nonsecret seed values |
| `prepared.json` | Nonsecret bindings and hashes to detect accidental changes |

State, tfvars, credentials, receipts, `.git`, infrastructure, mutation hooks and
dependencies are not copied into `app`. The helper does not create an
`azure.ai.project`, connection, Toolbox or memory-store service. It supplies
`FOUNDRY_PROJECT_ENDPOINT` and the existing-project marker; it does not create
another registry owner or opt into registry-reuse provisioning.

Do not edit the prepared snapshot, add files/hooks or run raw `azd up`, `down`
or a bulk deploy there. Both services are disabled unless their process-only
gate is set by the selected helper operation; service hooks also check that
operation. The saved environment must not contain those gates or a runtime key.
Hashes are drift detection, **not** signatures, ownership locks or protection
against someone deliberately rewriting the workspace and receipts.

## 2. Explicitly deploy the agent

Choose **one** authentication mode after independent approval:

```powershell
python -B $ApplicationFlow deploy-agent `
  --workspace $ApplicationWorkspace `
  --subscription-id $Subscription --tenant-id $Tenant `
  --managed-identity --confirm-agent-deployment
if ($LASTEXITCODE -ne 0) { throw 'Stop. Preserve the application receipt and review the remote outcome.' }
```

Or, if a runtime gateway key is deliberately required, populate a dedicated
process environment variable through your approved secret-handling mechanism.
Do not put its value in shell history or the command line:

```powershell
python -B $ApplicationFlow deploy-agent `
  --workspace $ApplicationWorkspace `
  --subscription-id $Subscription --tenant-id $Tenant `
  --gateway-key-env SELECTED_GATEWAY_RUNTIME_KEY --confirm-agent-deployment
if ($LASTEXITCODE -ne 0) { throw 'Stop. Preserve the application receipt and review the remote outcome.' }
```

The helper never retrieves a gateway key or GitHub credential. A selected
gateway key reaches **only the agent-deployment child process**, not tooling
inspection or schedule deployment. Core service `env` expansion delivers it to
the intended Foundry agent configuration; the helper does not write it into
its files, receipts or azd dotenv, or place it in subprocess arguments.
Raw deploy stdout/stderr are discarded. This is still a **secret-delivery
operation**: these safeguards do not certify every azd/extension cache, log or
cloud diagnostic. Qualify those separately and protect the private workspace.
Unexpected dotenv entries stop completion rather than being echoed or cleaned up.

Only the selected agent service is deployed. The helper never invokes the agent
or GitHub tools to test it. A `cli-completed` receipt requires azd success plus
matching locally registered agent name/version/endpoint. It is not independent
GET readback, image-pull proof, successful model/tool use or hosted identity
acceptance. The original shared application determines runtime behavior.

## 3. Separately enable the daily schedule

Review the agent receipt and complete the intended runtime checks under their
own approval before enabling automation:

```powershell
python -B $ApplicationFlow enable-schedule `
  --workspace $ApplicationWorkspace `
  --subscription-id $Subscription --tenant-id $Tenant `
  --confirm-enable-schedule
if ($LASTEXITCODE -ne 0) { throw 'Stop. Preserve the schedule receipt and review its remote state.' }
```

This deploys only `<agent-name>-daily`, not the agent again. It requires a complete
matching agent receipt and unchanged recorded azd state. The definition is enabled
when this operation applies it: **09:00 `America/Los_Angeles`**, using the repository
explicitly selected in `prepare`, unlike the unchanged Bicep manifest's fixed
repository prompt. It does not invoke an immediate test run.
The routine references the agent name, not a permanently pinned agent version;
later external changes are not detected by these local receipts.

The routine uses the stable camelCase authoring fields `agentName`,
`cronExpression` and `timeZone`. The root Bicep manifest is deliberately not
rewritten as part of this opt-in path.

## Stops, receipts and later lifecycle work

Each operation gets one exclusive append-only journal:
`agent.receipt.jsonl` or `schedule.receipt.jsonl`. A durable `pending` record
precedes the deploy process; success records `cli-completed`. Failure,
interruption, timeout or mismatched completion metadata records `unconfirmed`
when possible. A partial journal also blocks progression.

**Never delete or edit a receipt, regenerate a workspace or blindly rerun a
mutation to get past a stop.** A cloud operation or its remote build can continue
after a local timeout. The helper makes no second deployment attempt and does
not automatically enable the schedule, recover, roll back, rotate credentials,
update an existing release or delete resources. Retain all artifacts, separately
inspect the remote outcome and review the next action. An already completed
workspace is also single-attempt, not an unattended release pipeline.

The total command deadline defaults to 900 seconds and accepts
`--timeout-seconds` from 30 to 1800. Prerequisite failure before an intent is not
a deployment attempt; a separately approved tool installation can resolve that
specific prerequisite. Do not equate any source/offline success with full parity.

## Reviewed azd source contracts

Source inspection is pinned to Azure/azure-dev commit
`1273b0ddd9a04b09352f67632a6f1e3952fc5df0`, not a moving branch:

| Contract | Canonical source |
|---|---|
| Core service selection and deployment | [deploy action](https://github.com/Azure/azure-dev/blob/1273b0ddd9a04b09352f67632a6f1e3952fc5df0/cli/azd/internal/cmd/deploy.go) and [service importer](https://github.com/Azure/azure-dev/blob/1273b0ddd9a04b09352f67632a6f1e3952fc5df0/cli/azd/pkg/project/importer.go) |
| Process fallback and service gates | [environment](https://github.com/Azure/azure-dev/blob/1273b0ddd9a04b09352f67632a6f1e3952fc5df0/cli/azd/pkg/environment/environment.go) and [service config](https://github.com/Azure/azure-dev/blob/1273b0ddd9a04b09352f67632a6f1e3952fc5df0/cli/azd/pkg/project/service_config.go) |
| Automatic role repair opt-out | [developer RBAC check](https://github.com/Azure/azure-dev/blob/1273b0ddd9a04b09352f67632a6f1e3952fc5df0/cli/azd/extensions/azure.ai.agents/internal/project/developer_rbac_check.go) |
| Existing-project gate | [ACR feature](https://github.com/Azure/azure-dev/blob/1273b0ddd9a04b09352f67632a6f1e3952fc5df0/cli/azd/extensions/azure.ai.agents/internal/synthesis/acr_feature.go) |
| Agent environment and completion | [hosted service target](https://github.com/Azure/azure-dev/blob/1273b0ddd9a04b09352f67632a6f1e3952fc5df0/cli/azd/extensions/azure.ai.agents/internal/project/service_target_agent.go) |
| Routine authoring | [camelCase parser](https://github.com/Azure/azure-dev/blob/1273b0ddd9a04b09352f67632a6f1e3952fc5df0/cli/azd/extensions/azure.ai.routines/internal/pkg/routines/authoring.go) |
