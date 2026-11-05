# Source-to-module evidence map

This is an infrastructure foundation with separately qualified application
integration increments, not full parity with the Bicep-backed hosted-agent
sample. Use the current summary below; the subsequent dated checkpoints explain
its provenance and must not be combined into inflated test or acceptance counts.

## Current acceptance: November 5, 2026

| Area | Latest established evidence | Remaining boundary |
|---|---|---|
| Terraform offline contracts | **PASS:** 55 native mocked runs, semantic inspection of those same 55 plans, and 25 Python tests (14 adapter, eleven readback). All 15 positive root handoffs feed the real adapter, including Responses-only and custom aliases. Five locked roots initialize and validate; formatting, structure and script parsing pass. | No Azure deployment or runtime acceptance. The 15 handoffs are checks within the 55 plans, not extra runs. |
| Project gateway tool access | **Implemented/offline qualified:** independent default-off project-only Tools User grant; exact gateway scope, separate model-role ownership and combined/RemoteTool dependency checks. A separate read-only ARM GET confirmed the built-in role definition and its standalone-gateway data action. | No tools assignment, ToolServer, credential delivery or runtime allow/deny was performed. Definition availability in the inspected target does not establish availability everywhere. |
| Latest deployed configuration | **Qualified:** monitoring-enabled graph has 37 successful resource GETs, ten exact scoped roles, 250 matching compared leaves and an ordinary exact-input no-change plan. | Five requested properties are omitted by GET; full requested-body status is `INCOMPLETE`. Storage uses the explicit policy-aligned `Disabled` override, not an accepted private hosted-compute path. |
| Actual application model client | **PASS:** one local request through the unchanged shared application client returned HTTP 200 for the primary alias on Responses. Api-Key only; at most 32 output tokens, `store=false`, no tools, streaming, redirects or SDK retries. | Not a deployed hosted agent, managed-identity invocation, mini-alias application call, Toolbox or real GitHub operation. This is separate from the four earlier raw-API requests. |
| Application and container CI | **PASS at `232e73c`:** Bicep builds, Bash lifecycle/model-registration checks, 18 application unit tests, unchanged frozen image build and actual container smoke. Smoke covers Terraform exclusion, readiness, both Responses modes and mocked Toolbox initialization/discovery. | Mocks do not establish real tool access or hosted deployment. Local package-download TLS remains unresolved; successful CI proves the image path, not that local issue's cause. |
| Complete Bicep/azd workflow | **Not accepted:** existing Bicep/application/`azure.yaml` defaults are preserved. | ToolServer/Toolbox and explicit credential delivery, automatic Terraform azd integration, hosted agent/routine, intended-identity authorization, governance enforcement and lifecycle gates remain open. |

The adapter now requires Responses support on both selected aliases and rejects
inconsistent gateway group/ID and agent account/project ID/URL relationships.
Version-1 compatibility and the 16-field mapping (17 with gateway location)
remain intact. The tool-access flag is additive contract metadata, not a new
application environment field.
Native positive fixtures were corrected to use the configured resource names;
the checker does not rewrite plan outputs to make them pass. Gateway and registry
hostname ownership still needs independent provenance, not string syntax alone.

Offline CI remains credential-free. These local/live observations and the
exact-commit application CI result have different scopes; none should be
relabeled complete hosted-agent acceptance. Protected receipts are retained
outside the contribution.

## Fresh contribution: bounded live proof

**Dated foundation checkpoint: November 4, 2026.** The 33-resource and 41-case
observations in this section precede the later opt-in and adapter increments.

The self-contained three-group root was deployed into a separately authorized,
isolated Sweden Central environment using Terraform 1.11.4 and locked AzAPI
2.13.0. No historical state or resource was adopted. Model versions/capacities
and APIs remain those of the bundled profile.

| Check | Result and boundary |
|---|---|
| Offline extraction/regression | **PASS:** 41 native mocked plans and 41 semantic inspections; five roots initialized and validated with read-only locks. Formatting, lifecycle/structure and script syntax checks passed on Windows. The four examples have offline coverage, not independent live acceptance. |
| Fresh creation | **PASS:** 33 resources across three new workload groups, including six scoped roles. No existing environment was changed. |
| Resource and role readback | **PASS:** all 33 resources returned successful ARM GETs; all six roles matched exact principal, role definition and resource scope. |
| Independent requested-body comparison | **Qualified:** returned requested fields and placement/identity metadata matched, allowing ARM ID/location/identity-type case normalization. Six paths were not returned by GET: three catalog `apiFormat` properties, exporter `kind`, and the project insights/registry connection `credentials` objects. These values are not independently readback-proven; runtime successes do not establish every omitted property. |
| Policy alignment and idempotence | **PASS with explicit input:** inherited management-group Modify policies disabled Storage public access. Set `agent_storage_public_network_access = "Disabled"`; the validated correction changed only Storage ACL Allow to Deny, with public access remaining Disabled. The dependent connection resolved without a change. Ordinary exact-input plan then exited 0 with no changes. Model/agent accounts and ACR remained Enabled. |
| Bounded key-auth runtime | **PASS:** both aliases returned HTTP 200 on Chat Completions and Responses with expected envelopes; missing and invalid keys returned HTTP 401. Credentials were acquired outside Terraform and held only in process memory. |
| Gateway request telemetry | **PASS:** a direct `AppRequests` query matched all four original request `OperationId` values and the exact expected AppInsights component. An earlier broad `search *` query returned a false negative; no exporter redesign or extra inference was needed. No payload capture was enabled. |
| Applicable upstream checks | At this checkpoint, 18 application unit tests and the Bicep model-registration contract passed. The unchanged upstream Bash lifecycle test hit its two-second transition bound on Windows; Linux/GitHub Actions and container smoke had not yet run. Their later successful CI result is recorded in the current summary above. |

This is the root with a Storage-only override, **not acceptance of unchanged
network defaults in every policy environment**, a private Storage data path,
hosted-agent readiness, model-policy enforcement or controlled failover.
Storage remains inaccessible through ordinary public data-plane access;
the override creates no private endpoint/DNS/network or hosted compute.
No `ignore_changes`, policy exemption, role expansion or old-state migration
was used to obtain the no-change result. Recovery, rotation and teardown remain
separate gates.

Detailed receipts remain in protected deployment/session storage. The checks
above are a dated observation, not a claim that the offline CI deploys Azure
resources. The subsequently packaged [GET-only runner](live-readback.md)
reproduced the qualified 33-resource comparison with 237 compared leaves,
including identity metadata, and the same six GET omissions; exit 3
`INCOMPLETE` is intentional, not full configured-body acceptance.

## Separate opt-in integration increment

**Dated model-access checkpoint: November 5, 2026 CET.** At this increment the
canonical offline suite passed **49 native mocked runs and semantic inspections,
plus 18 Python tests** (seven adapter and eleven readback cases).
All five roots validated with the same locks; formatting, structure and
PowerShell parsing passed. These are the results at that checkpoint, not the
current suite counts or a relabeling of the earlier 41-case extraction.

| Feature | Implemented and tested boundary |
|---|---|
| Account/project gateway model access | Optional root-owned exact-scope Models User grants, off by default; stable account/project keys and duplicate-owner guard. Default 33/six graph remains. **Live verified:** two new roles applied, zero existing resources changed/destroyed; all eight roles read back at exact principal/definition/resource scope in the 35-resource graph. Ordinary exact-input plan exited 0/no changes. Runtime identity authentication is not accepted. |
| RemoteTool connection | Optional explicit caller-established HTTPS endpoint on the deployed gateway, independent of model-access grants. Configuration/mock coverage only; no actual ToolServer/Toolbox URL is invented or deployed. |
| Nonsecret environment adapter | Explicit version-1/full-output allow-list to JSON, including original contract compatibility, custom alias guards and secret exclusion. Actual updated deployment outputs produced 17 independently checked nonsecret fields. No env mutation, secret retrieval, automatic azd hook or app deployment. |
| Read-only qualification runner | Explicit subscription/tenant, GET-only requested-subset comparison, safe new receipts and honest omitted-value status. Unit tests cover scope, CLI lifecycle, numeric representation, omissions and secret exclusion. **Live:** all 35 GETs succeeded, 243 compared leaves agree, same six omitted paths; overall `INCOMPLETE`, not green for full configuration. |

The live increment was observed on November 5, 2026 CET (November 4 UTC).
Only `enable_foundry_gateway_model_access = true` was added to the previously
accepted Storage-aligned inputs. RemoteTool stayed null; no invented endpoint,
ToolServer, credential or application deployment was used. All 27 frozen
configuration-file hashes still matched after acceptance. The dated 33-resource
baseline above is retained rather than retroactively relabeled as this run.

ToolServer/Toolbox/credential write contracts remain gated by the
[independent contract investigation](tool-credential-boundary.md). A newer
published schema was not silently substituted into the tested deployment.

## Separate monitoring configuration increment

**Dated monitoring checkpoint: November 5, 2026 CET.** The canonical suite then
passed **53 native mocked runs and semantic inspections, plus 18 Python tests**,
five locked root validations, formatting, structure and PowerShell parsing.
Four focused module/root/combined/independent-example cases cover the default-off
in-place Insights auth switch and exact publisher grants.
The default graph is still 33 resources/six roles. These results do not replace
the dated 41-case foundation or 49-case model-access evidence above.

The support module implements the unchanged upstream
`infra/foundry-agents/main.bicep` `ProjectManagedIdentity` connection body and
account/project Monitoring Metrics Publisher grants. It updates the sole
existing project-owned connection in place, retaining its address/API/parent/name.
Default false preserves its ApiKey body. A separate account connection owner
was rejected before apply after read-only inspection exposed matching existing
connection bodies/creation times through both routes. Mirrored backing is an
inference about backing ownership, not a fully specified service contract.
Topology and runtime selection are not asserted identical to Bicep.
No application instrumentation or local-auth policy is
changed. This configuration is not hosted-agent tracing or Entra-only proof.

**Separate live qualification, November 5, 2026 CET (November 4 UTC):**
the newly validated, hash-bound plan applied **two added roles, one connection
update, zero destroyed resources**. The resulting graph has **37 resources and
ten exact scoped roles**. An ordinary exact-input plan exited 0/no changes.
All 37 ARM GETs succeeded; 250 compared leaves agreed. Five requested paths
remain omitted: three catalog `apiFormat` fields, exporter `kind` and registry
connection `credentials`. Overall requested-body status remains `INCOMPLETE`;
the old project Insights credentials omission no longer applies because that
object is no longer requested. This is not proof of stored credential erasure.

Independent account and project GETs both returned the intended
`ProjectManagedIdentity` body/metadata and retained their resource IDs after the
single Terraform-owned update. Both routes reset `systemData.createdAt` to the
update time. Therefore the Terraform plan had no replacement, but preservation
of service-internal backing identity is not established. The dual-route update
is evidence for the single-owner design, not an unrestricted alias guarantee.
All 27 source/staged hashes matched; the actual adapter still produced the
same 17 nonsecret fields. RemoteTool stayed null; no tool, credential, app,
local-auth policy or runtime-tracing operation was performed.

## Provenance and acceptance boundary

The source implementation is `samples/terraform` at commit
`25aabd247ac76395af11f542848edf16fc99c324` of
`annawiewer/ai-gateway_test`. The comparison baseline is this sample at
`4ac828155315607141ed4e1ea692c766fff4c123`. Source filenames below identify
provenance; they are not external configuration dependencies.

Historical source CI was credential-free/offline/mocked: 97 root cases, 22
wrapper runs, four nested-plan inspections, 27 Python tests, 34 model-script
cases, 153 API2026 acceptance cases, 88 deployment cases and 14 portal cases.
These are overlapping test families, **not extracted-destination test results
or a cloud acceptance count**. Portal fixtures do not prove portal operation.

Retained live proof used an opt-in **one-resource-group private-backend lab**.
It does not accept the new default three-group root, even where API bodies are
preserved. Module extraction changes addresses and dependencies; the fresh
checks above were established separately, not inherited from this lab.

| Retained historical evidence | Established scope | Not established |
|---|---|---|
| Configuration readback, November 4 | Nine configuration checks passed: scope/context, placement, private lab, models/routes, backend safety binding, connections, roles and exporter topology. Overall result was **INCOMPLETE**. | Complete runtime, policy enforcement, telemetry or hosted-agent acceptance. |
| Runtime key checks | Both `gpt-latest` and `gpt-mini-latest` returned HTTP 200 on Chat Completions and Responses; missing/invalid keys returned HTTP 401. | Alternate-tier failover, tools or hosted runtime. |
| Lab user-assigned managed identity | Both aliases and APIs returned HTTP 200; a valid ungranted identity returned HTTP 403. This preceded final monitoring corrections. | Foundry project/account identity invocation; private gateway ingress. |
| Ordinary no-change plan | Historical lab had no changes across 90 managed resources and 17 roles; six historical states were unchanged at that check. | New module-address migration, fresh default-root idempotence, recovery or teardown. |
| Telemetry observation | Fresh mini inference succeeded. Bounded queries did not establish fresh correlated gateway delivery; two signal-owner queries failed. | Delivery or its failure cause. Storage logs, DNS/TLS and exporter configuration are not gateway telemetry proof. |

No raw receipts, private deployment identifiers, credentials, state, plans or
unsanitized output are distributed here.

## Capability and test-family ownership

Links identify the new configuration owner, not a transfer of live acceptance.

| Source capability / files | Historical test families | New owner | Retained proof / qualification |
|---|---|---|---|
| Naming and placement: `main.tf`, `api2026gateway/main.tf` | `infrastructure.tftest.hcl`, `api2026gateway.tftest.hcl`, wrapper integration/input guards | [Composition root](../README.md) | Historical lab used one group. Fresh three-group creation and no-change planning are separately verified above, with the Storage-only override. |
| Account, pinned model profile, serialized deployments and backend filter binding: `foundry-models.tf`, wrapper `model-profile.json` | Infrastructure and API2026 profile/configuration tests | [foundry-models](../modules/foundry-models/README.md) | Historical account/deployments and backend `Microsoft.DefaultV2` binding read back; region/quota/model availability must be checked for a new target. |
| Gateway, workspace, runtime-key resource, retention guard: `ai-gateway.tf`, `ai-gateway-backend.tf` | Infrastructure, API2026 and wrapper tests | [ai-gateway](../modules/ai-gateway/README.md) | Historical configuration and bounded key/lab-identity inference only. Key resource ownership does not deliver a credential to an application. |
| Gateway backend grant, MI provider, catalog and aliases: `rbac.tf`, `model-routing.tf` | API2026 routing, alias compatibility and additive caller tests; model-script fixtures | [ai-gateway](../modules/ai-gateway/README.md) | Grant precedes provider; aliases route through catalog resources. Positive inference does not exercise all failover tiers. |
| Token, monthly-cost, optional request-rate and CIDR policies: `model-routing.tf` | API2026 positive/negative policy and CIDR guards | [ai-gateway](../modules/ai-gateway/README.md) | Configuration features retained; offline checks do **not** prove enforcement. Do not equate backend filtering with gateway/MCP content safety. |
| ApplicationInsights exporter and destination: `monitoring.tf` | API2026 monitoring preconditions and acceptance fixtures | [ai-gateway](../modules/ai-gateway/README.md) | Keep the separately pinned telemetry API and disabled payload capture. Historical delivery was unproven; fresh four-request, expected-component delivery is separately verified above. This does not prove hosted-agent tracing. |
| Account/project, Storage/ACR, internal roles and support connections: `foundry-agents.tf`, `rbac.tf`, `monitoring.tf` | Infrastructure/configuration acceptance fixtures | [foundry-agents](../modules/foundry-agents/README.md) | Historical support configuration, not image build, hosted-agent operation, tracing delivery or default project-to-gateway authorization. |
| Opt-in caller and developer grants: `rbac.tf` | Infrastructure caller validation and API2026 lab identity tests | Gateway module owns explicit Models User callers; root owns selected Foundry model/tool grants; models/agents own their developer grants | Explicit grants retain narrow scopes. A successful role PUT is not proof of propagation or the intended Foundry identity's runtime authorization. |

### Destination offline checks

The [canonical runner](../scripts/Test-Offline.ps1) checks the extracted
implementation, not historical wrapper addresses. Its actual test owners are:

| Destination family | Scoped responsibility |
|---|---|
| [`root.tftest.hcl`](../tests/root.tftest.hcl) | Default/custom/single-group composition, alias protocol intersection, policy/route/input guards and independently selected model/tool/monitoring grants |
| [`gateway.tftest.hcl`](../tests/gateway.tftest.hcl) | Standalone gateway module, nullable frontend, exporter destination and caller guards |
| [`models.tftest.hcl`](../tests/models.tftest.hcl) | Model module and deployment-profile guards |
| [`agents.tftest.hcl`](../tests/agents.tftest.hcl) | Independent support module, backend-access/Storage-only controls and optional exact monitoring connection/grants |
| [`examples.tftest.hcl`](../tests/examples.tftest.hcl) | Four runnable roots, external-pregrant mode, independent Storage-only and monitoring opt-ins |
| [`check_contracts.py`](../tests/check_contracts.py) | Bundled dependencies/ownership/lifecycle structure and semantic inspection of mocked API bodies, grants, routes and support resources |
| [`test_environment_adapter.py`](../tests/test_environment_adapter.py) | Explicit allow-listed version-1 environment mapping, Responses and cross-reference guards, secret exclusion and no mutation |
| [`test_live_readback.py`](../tests/test_live_readback.py) | GET-only safe receipts, explicit context/scope, omission status, numeric equivalence and no overwrite |

The runner also performs locked backend-disabled initialization,
formatting/validation and PowerShell parsing. These are offline checks only;
the 41-case extraction, 49-case integration and 53-case monitoring checkpoints
are distinguished above. The adapter increment retained 53 native plans,
checked 13 root handoffs within them and raised the Python suite from 18 to 25.
The current tools-grant increment adds two native cases, for 55 plans and
15 root handoffs; the 25 Python tests are unchanged.
They do not turn source live proof
into extracted-destination acceptance. The old private/legacy
scenario suites are not silently included in these families.

## Excluded extensions and missing integration

Exclusion from this extraction does not erase historical capability or proof.

| Area | Status and boundary |
|---|---|
| Owned private-backend lab, probe VM/UAMIs, private endpoints/DNS, NSG fixtures and private Blob diagnostics | Source optional extensions, not bundled lab automation here. Historical private-backend and Blob allow/deny proof remains valid within that lab. This does not imply gateway private ingress or a running private hosted agent. |
| Legacy gateway contracts, alternate network profiles, external-network diagnostics and private hosted-agent scenario framework | Deliberately outside this API2026 structural baseline. Source tests for these scenarios must not be relabeled as destination coverage. |
| Gateway/MCP `contentSafety` | The contribution keeps gateway safety disabled pending selected-API qualification; that local rejection is not proof of service non-support. Backend `Microsoft.DefaultV2` is a different surface, not equivalent MCP/gateway protection or enforcement proof. |
| RemoteTool, GitHub MCP ToolServer, Toolbox and GitHub credential workflow | RemoteTool is now an opt-in explicit-endpoint configuration, not accepted tool runtime. ToolServer, Toolbox and credential delivery remain missing. No stub resource, token path or implicit personal CLI credential upload is supplied; see the independent contract boundary above. |
| Terraform-backed azd adapter, hosted image/Responses agent, scheduled routine | Explicit nonsecret environment JSON mapping and bounded local application-client key auth are accepted within the limits above. The shared image builds and passes mocked container smoke in CI. Automatic Terraform azd integration and deployment of the hosted agent/routine remain unimplemented/unaccepted. Existing Bicep/app/`azure.yaml` behavior remains unchanged. Do not run Bicep recovery hooks against Terraform-owned resources. |
| Controlled failover, policy exhaustion/denial, intended Foundry identity authorization, hosted-agent tracing and rotation/recovery/complete teardown | Unaccepted gates. Fresh key runtime, gateway request telemetry and a no-change foundation plan do not prove them. |

The fresh checks above used a selected target and approved bounds. Further
acceptance still needs intended Foundry identity allow/deny and independently
scoped full runtime/lifecycle gates. Historical receipts must not be relabeled
as destination acceptance.
