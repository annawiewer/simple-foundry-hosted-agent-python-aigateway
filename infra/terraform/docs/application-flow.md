# Guided Terraform application deployment

This opt-in path joins the Terraform infrastructure and tool handoffs to the
shared hosted agent, then separately enables its daily schedule. The root
`azure.yaml` and its Bicep workflow stay unchanged. Terraform still owns the
infrastructure; this is **not** a replacement `azd up` or Terraform apply wrapper.

**One on-demand hosted digest was accepted on November 7, 2026**, using azd
1.37.2, the pinned extensions, project-local registry sharing
(`share_foundry_registry_connection = false`) and an immutable prebuilt image
through the explicit platform-default ACR path. All three GitHub tools and the
intended gateway/model path succeeded with correlated telemetry. Every
deployment requires separate target-specific approval; these examples do not
authorize changes to an existing deployment. The [evidence map](evidence-map.md)
separates that result from untested build, credential and recurring scenarios.

## The complete sequence

| Step | Owner and action |
|---|---|
| 1. Infrastructure | Follow the [preparation guide](architecture.md#offline-and-deployment-preparation); review and separately authorize each fresh Terraform plan/apply. |
| 2. Telemetry | Finish the [native telemetry handoff](native-telemetry.md) and fresh second-stage plan/apply, or deliberately retain the supported legacy mode. Pending telemetry stops application preparation. |
| 3. GitHub tools | Follow the [tool guide](toolchain.md): explicit-credential ToolServer creation, fresh Terraform RemoteTool connection plan/apply, then Toolbox creation/readback. |
| 4. Prepare the app | Run the offline `prepare` operation below with the applied contract, connected bootstrap and configured Toolbox receipt. |
| 5. Launch the agent | After separate authorization, select its authentication mode and run `deploy-agent`. No routine is deployed by this step. |
| 6. Bind and verify the runtime identity | Independently read the exact deployed agent version's principal; review its opt-in Terraform role bindings and any required tenant authorization, then [verify one on-demand digest](#verify-one-on-demand-digest) and its traces. |
| 7. Enable the schedule | Only after runtime acceptance, explicitly run `enable-schedule`. This activates real scheduled model/tool use and was not part of the accepted on-demand run. |

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

This is the reviewed **source compatibility baseline**; live acceptance used
azd **1.37.2** with these **1.0.0** extensions, not every stable 1.37.x release
or deployment mode. Version checks
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
developer-RBAC repair; it does not grant missing permissions. Project tool
access must already be enabled. The contract must include the owned registry
connection ID matching the project and exported connection name. Both boolean
sharing choices are accepted; sharing is not a substitute for project ownership
or registry pull permissions. See [project-local compatibility](architecture.md#project-local-registry-compatibility).
Managed-identity model access also requires a grant for the actual deployed
agent identity, not merely the account/project grants; see the
[postdeployment identity handoff](#3-bind-the-deployed-agent-identity).

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
Re-export older contracts that lack `agents.registry_connection_id`; do not
invent that field or substitute a parent-account/other-project connection.
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
The pinned hosted extension may save `ENABLE_HOSTED_AGENTS=true` and
`ENABLE_CAPABILITY_HOST=false` during predeploy. Only those exact additional
boolean values are accepted; they do not prove activation, relax the original
saved context, or turn an unconfirmed receipt into success. Other global
outputs, including conditional `AI_PROJECT_*` settings, remain rejected.
Hashes are drift detection, **not** signatures, ownership locks or protection
against someone deliberately rewriting the workspace and receipts.

### Optional existing image

By default, preparation still selects the existing ACR remote-build path.
To deploy an image already built in the contract's registry, add
`--prebuilt-image` to the **prepare** command for a new workspace:

```powershell
python -B $ApplicationFlow prepare `
  --workspace $ApplicationWorkspace `
  --subscription-id $Subscription --tenant-id $Tenant `
  --contract $Contract --bootstrap $ConnectedBootstrap --tool-receipt $BoxReceipt `
  --repository '<owner/repository>' --agent-name '<unique-lowercase-agent-name>' `
  --prebuilt-image '<declared-registry-host>/<repository>@sha256:<64-lowercase-hex-digest>'
if ($LASTEXITCODE -ne 0) { throw 'Application preparation stopped.' }
```

Use the digest returned by successful image-build/registry readback, not a CI
success flag or a mutable tag. The image host must match the contract's exact
`agents.registry_endpoint`, not a hostname inferred from the registry ARM name.
Foreign registries, tag-only references, credentials, URLs, query strings and
malformed digests are rejected before the workspace is created.

This selects `docker.imagePassthrough=true`, the literal pinned `image` and the
owned project connection **name** in the generated agent service's
`registryConnectionId`; it omits `remoteBuild`. The full ARM ID is still required
and checked against the exact project and connection name in the Terraform
contract. It is not a `--from-package` override. The seven shared
application files are still copied unchanged into `<workspace>\app`:
`Dockerfile`, `.dockerignore`, `pyproject.toml`, `uv.lock`, `main.py`,
`repo_digest_agent.py`, and `github_mcp_middleware.py`. No infrastructure,
connection, role or routine is created by preparation.

For an explicitly reviewed platform-default ACR path, also pass
`--use-default-acr` with `--prebuilt-image`. This opt-in omits only
`registryConnectionId`; it retains the exact-registry image validation, full
connection ARM-ID ownership check and no-role-assignment safeguards. It does
not grant pull access or prove which identity the hosted service will use.
Verify image retrieval and the actual runtime identity independently. Existing
named-connection and remote-build behavior remain unchanged without this flag.

The selection is recorded in `prepared.json`, validated against the saved
registry, and included in manifest integrity checks and the deployment's
prepared fingerprint. Do not edit a prepared image selection in place.
Existing image-less workspaces remain compatible. Prebuilt workspaces whose
manifests contain the full registry connection ARM ID must be prepared again in
a new workspace; preserve their original manifests, local state and receipts.
Run the same `deploy-agent`
command below; neither deployment nor schedule activation accepts an image
override. Build success, image existence, pull permissions and the actual
deployed image still require independent evidence; offline preparation does
not query the registry or certify the image's contents.

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

## 3. Bind the deployed agent identity

Read the exact deployed name/version independently from the project data plane:

```http
GET <project-endpoint>/agents/<agent-name>/versions/<version>?api-version=v1
```

Use `instance_identity.principal_id`, not an application/client ID, the Foundry
account identity or the project identity. Recheck it after a version/identity
change; deployment success alone does not establish runtime authorization.
The helper deliberately retains `AZD_AGENT_SKIP_ROLE_ASSIGNMENTS=true`.

Add a separately reviewed nonsecret input file to the **same root and workspace**,
retaining all original inputs and applied telemetry/tool handoffs:

```hcl
hosted_agent_principals = {
  digest = "<verified-agent-instance-principal-uuid>"
}
```

The map defaults to empty, normalizes UUID case and rejects duplicate principals
and account/project identities. Labels are stable Terraform address keys.
The root adds only these selected bindings:

| Role | Exact scope | Controlling input |
|---|---|---|
| AI Gateway Models User | This AI Gateway | `enable_foundry_gateway_model_access` |
| Monitoring Metrics Publisher | The agent Application Insights component | `enable_foundry_monitoring_integration` |

No hosted-agent Tools User, Contributor or subscription/resource-group grant is
added. Toolbox tool access continues through the separately authorized project
identity. Do not list the same Models User binding in `gateway_access_principals`
while hosted model access is enabled. Monitoring-only bindings may coexist with
a separately owned model caller.

Review a fresh refresh-enabled plan with **all** existing inputs plus this file,
then separately authorize apply and read back the exact role scopes/principal.
Changing/removing a label, principal or integration flag can remove permissions;
do not treat that as an automatic release or identity-migration operation.

**Existing grants need explicit ownership review.** The accepted environment's
two runtime grants were created operationally and remain outside its protected
Terraform state. This source update does not import them or rewrite that state.
If adopting matching grants into the existing authoritative state, use explicit
imports to these addresses rather than creating duplicate owners:

```hcl
import {
  to = azapi_resource.hosted_agent_runtime_access["models-digest"]
  id = "<gateway-resource-id>/providers/Microsoft.Authorization/roleAssignments/<existing-assignment-uuid>?api-version=2022-04-01"
}
import {
  to = azapi_resource.hosted_agent_runtime_access["monitoring-digest"]
  id = "<agent-insights-resource-id>/providers/Microsoft.Authorization/roleAssignments/<existing-assignment-uuid>?api-version=2022-04-01"
}
```

Import reads explicitly select the role-assignment API used by this root.
Independently verify the existing assignment's name, principal, role and scope
against the configuration's deterministic UUIDv5 name. Stop on a mismatch,
replacement or unrelated change; do not copy/fork state or force adoption.
These are illustrative import blocks, not an instruction to apply them to the
accepted environment.

Tenant authorization is a separate prerequisite. The accepted run needed an
owner-approved exception for exactly the deployed Agent Identity in an enabled
Conditional Access policy. Terraform does not change tenant policies, and RBAC
cannot substitute for that authorization. Do not copy the exception broadly.

### Verify one on-demand digest

Use the same pinned azd/extensions and approved login/profile as deployment.
The helper does not change your shell's directory or selected azd environment.
Read the prepared bindings and inspect the deployed service explicitly:

```powershell
$Prepared = Get-Content -LiteralPath (Join-Path $ApplicationWorkspace 'prepared.json') -Raw |
  ConvertFrom-Json
azd ai agent show $Prepared.agent_name `
  --cwd $ApplicationWorkspace --environment $Prepared.environment.AZURE_ENV_NAME `
  --output json --no-prompt
if ($LASTEXITCODE -ne 0) { throw 'Agent readback failed; do not invoke.' }
```

Match the returned project, name and version to the completed
`agent.receipt.jsonl` and the independent version readback above. Copy the
displayed **Responses invocation endpoint** for that agent; the receipt's
`agent.endpoint` is a version-resource URL, not an invocation URL.
Keep the repository from `prepare`, available as
`$Prepared.environment.GITHUB_REPOSITORY`.

**Obtain separate approval before the next command:** it creates a real
session/conversation and runs model and GitHub-tool requests. Use an empty
private directory outside the prepared workspace so invocation context cannot
change the deployment snapshot required by `enable-schedule`. The explicit
endpoint/version selects the target, not an ambient azd environment:

```powershell
$AgentVersion = '<independently-verified-version>'
$ResponsesEndpoint = '<verified-responses-invocation-endpoint>'
$VerificationWorkspace = Join-Path $Private 'on-demand-check'
New-Item -ItemType Directory -Path $VerificationWorkspace -ErrorAction Stop | Out-Null

azd ai agent invoke `
  --agent-endpoint $ResponsesEndpoint --version $AgentVersion `
  --new-session --new-conversation --timeout 300 --debug-latency=false `
  --cwd $VerificationWorkspace --no-prompt --output raw `
  "Create a concise daily repo digest for $($Prepared.environment.GITHUB_REPOSITORY)." |
  Out-File -LiteralPath (Join-Path $VerificationWorkspace 'response.txt') `
    -Encoding utf8 -NoClobber -ErrorAction Stop
if ($LASTEXITCODE -ne 0) { throw 'Invocation failed or is unconfirmed; preserve evidence and stop.' }
```

Keep the response, returned session/request/trace IDs and UTC run window private.
Confirm the resolved agent version and a completed response, not merely HTTP
200, CLI exit zero or an active hosted version. Inspect the agent trace for
successful calls to all three GitHub tools and truthful results; empty results
must agree with the selected repository. In the agent and gateway Application
Insights resources, correlate that run's IDs/time window with the intended
gateway/model and GitHub backend requests. Missing or contradictory evidence
means acceptance is incomplete; do not enable the schedule or blindly retry
after a timeout. No redeployment or `azd up` is needed for this check.

The November 7 run completed all three read-only GitHub tools; its empty result
sets correctly produced a no-change digest. It did not activate a schedule.

## 4. Separately enable the daily schedule

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
| Explicit endpoint and version-bound on-demand invocation | [invoke command](https://github.com/Azure/azure-dev/blob/1273b0ddd9a04b09352f67632a6f1e3952fc5df0/cli/azd/extensions/azure.ai.agents/internal/cmd/invoke.go) |
| Routine authoring | [camelCase parser](https://github.com/Azure/azure-dev/blob/1273b0ddd9a04b09352f67632a6f1e3952fc5df0/cli/azd/extensions/azure.ai.routines/internal/pkg/routines/authoring.go) |
