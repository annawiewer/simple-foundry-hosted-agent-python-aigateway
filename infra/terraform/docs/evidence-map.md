# Validation and acceptance

**Status: November 7, 2026. Shared/default registry, normal container source
build and version 5 digest are accepted.** The Terraform path demonstrated
infrastructure, integrated ACR build, hosted deployment, gateway/model routing,
all three real GitHub tools and correlated native telemetry. The normal build
uses a tag independently bound to its digest, not a digest-pinned reference.
The earlier immutable-image version 3 and manual daily-routine dispatch remain
accepted separately. The routine is disabled; wall-clock firing is unproven.

The goal is the same technical demonstration as Bicep, not identical deployment
commands or lifecycle ownership. Both paths use the shared application and
gateway contracts. The results below distinguish source support, configuration
readback and observed runtime behavior; successful inference alone does not
prove every policy's rejection threshold.

## Acceptance matrix

| Area | Established evidence | Boundary / not established by this check |
|---|---|---|
| Terraform offline suite | November 7 canonical run: 88 native mocked plans with semantic checks, four isolated mocked applies for deferred registry readback postconditions, 147 Python contracts, five locked root validations, formatting and PowerShell syntax. Adapter handoff assertions are checks within plans, not additional runs. | Not Azure availability or runtime behavior. Default ownership remains 37 Azure resources, including 11 scoped role assignments, plus one non-owning registry PATCH action; opt-in runtime bindings do not change empty-map behavior. |
| Application/container CI | Published-baseline CI passed. The added [CI steps](../../../.github/workflows/ci.yml) build and smoke the actual prepared Terraform context, not a second hand-written Dockerfile. Local frozen application tests and the prepared Linux AMD64 image's smoke assertions passed. | Local evidence does not establish hosted CI success for a particular commit; check that commit's workflow result separately. Local ARM-to-AMD64 emulation required a diagnostic-only longer startup allowance; the repository smoke timeout was not changed. |
| Normal source-build deployment | With registry sharing/default true, integrated ACR run `dt4` built the seven shared files for Linux AMD64 and deployed version 5. The helper produced a genuine `cli-completed` receipt. Independent reads matched the configured tag to the run's digest before and after the successful digest. See the [normal route](application-flow.md#default-build-and-deploy-the-source). | Tagged reference, not image immutability. Existing-environment qualification with existing permissions; no fresh-from-empty certification or claim about other build/registry modes. |
| Digest-pinned existing-image route | Earlier ACR run `dt2` built the same seven shared application files for Linux AMD64. Unique run/tag readback and independent registry-manifest lookup agreed on the immutable digest deployed as version 3. See the [optional build recipe](application-flow.md#build-the-selected-source-in-the-existing-registry). | An independently built, source-bound image, not an unexplained prebuilt prerequisite. This earlier run used project-local registry sharing and does not replace the later shared-mode proof. |
| Integrated application infrastructure | Authoritative state contains 42 Azure resource owners, including 14 scoped role assignments, plus one non-owning registry PATCH action and one GET data entry. Two runtime grants were previously ownership-checked and adopted without Azure mutations. The registry repair's ordinary plan reported no pending changes; final source-runtime checks preserved the resulting state byte-for-byte. | Selected `2025-09-01-preview` gateway deployment only. Registry sharing is now accepted true; RemoteTool sharing remains explicitly project-local despite its source default true. Other regions/modes and omitted catalog `apiFormat` remain unqualified. |
| Shared/default registry repair | At 21:17:22 UTC on November 7, the sole owner followed by native non-owning PATCH and independent GET retained both flags true at project/account endpoints. An ordinary plan exited 0 with no pending resource/output changes. After the new source-build digest, both flags, the existing versions/principal, all 14 roles, tools, exact-agent tenant authorization and disabled routine were preserved. | Target-specific repair and runtime qualification, not proof of a universal service defect or fresh-from-empty lifecycle. The earlier version 3 digest used project-local sharing; its evidence was not relabeled. |
| Agent and gateway telemetry | The new source-build digest correlated 28 agent and 149 gateway spans with the exact-session console. All three executed-tool spans matched the session, version 5, call IDs and repository arguments; two model and five GitHub backend calls returned HTTP 200. The earlier routine run correlated 28 agent and 146 gateway spans. | Not a zero-error trace: an earlier MCP request returned 499 with `AuthorizationServiceError`, before model/tool execution. Its cause is not established. Policy execution is not rejection proof; Portal-dashboard behavior, all-signal completeness and exporter migration remain unqualified. |
| Native telemetry source | Two-stage managed ingestion, OTLP endpoints, gateway-identity DCR publishing, a bounded GET-only helper and native/legacy/pending mock plans. See the [usage and migration boundary](native-telemetry.md). | Configuration alone remains insufficient; the preceding row provides separate delivery evidence for this deployment. Exporter migration and other target/endpoint combinations remain unqualified. |
| Model content-safety source | Same-run mock assertions cover the exact four-category body, omission and coexistence with other policies. The bundled root selects Medium; explicit profiles allow Low/Medium/High or null. Standalone defaults and backend Microsoft.DefaultV2 are unchanged. See [configuration and opt-outs](../README.md#model-content-safety). | Mocks do not prove service acceptance or enforcement; the selected-API readback below is narrower than complete policy/runtime qualification. |
| Selected-2025 model readback | A November 7 disposable-model check returned all four requested Medium safety severities. Model creation, removal and absence were verified. | Requested-body qualification remains incomplete, including omitted `apiFormat`. This was not a runtime safety-enforcement or MCP-safety test. |
| Selected-2025 ToolServer control plane | An isolated November 7 check created, updated, read and deleted a ToolServer using public Learn MCP and synthetic nonsecret headers. Nonsecret configuration, stable endpoint identity, known null header placeholders on ordinary GET and deletion were verified. | Not real credential rotation, secret-value storage/delivery, server-side atomic conditional semantics or runtime safety enforcement. This isolated check did not invoke substantive tools or certify the production runner's full lifecycle. |
| GitHub toolchain source | Explicit-credential runner, Terraform-owned RemoteTool handoff and direct Foundry Toolbox creation/inspection. Forty-six mocked tests cover lifecycle guards, uncertain writes, redaction and Windows/POSIX selected-credential exclusion. See [ownership limits](toolchain.md). | Hosted execution separately proves real tool consumption, not live rotation/revocation, diagnostics-wide secret handling or competing-writer semantics. Creation is not atomic. |
| Application-flow source | The [app-only path](application-flow.md) binds applied handoffs, copies only shared runtime/build files, disables automatic role repair and gates agent/schedule operations independently. Fifty-seven focused tests passed after the process-local user-agent regression. Normal integrated remote build and the optional digest-pinned route both have separate live evidence on azd 1.37.2 / extensions 1.0.0. | No claim for every stable 1.37.x release. The helper's local deadline does not enforce an ACR cloud-build ceiling. Actual generic `azd show` returned mappings only; deployed endpoint evidence came from `azd ai agent show`. |
| Actual-agent runtime grants | Exact-principal live readback confirmed gateway Models User and agent-Insights Monitoring Metrics Publisher. Both are now Terraform-owned through [`hosted_agent_principals`](application-flow.md#3-bind-the-deployed-agent-identity), preserving the existing agent principal. | No direct agent Tools User or broad Contributor grant was added. Tenant authorization remains separate; the existing exact-agent exclusion was verified, not modified. |
| Current-source hosted digest | Version 5 completed all three read-only tools in a version-bound session. Scanned counts were 0 PRs, 0 issues and 20 workflow runs, with no failed workflows observed. The 100-word digest explicitly qualified bounded observations and truncation metadata. Version 3's earlier acceptance remains preserved. | Not an exhaustive repository census or populated-result live UX coverage. Truncation and unavailable-versus-empty behavior have focused regression coverage, not exhaustive service qualification. |
| Daily routine | Configured `0 9 * * *`, `America/Los_Angeles`; one explicit dispatch completed against the same version/image/principal. Exact dispatch, session and response IDs matched successful agent/model/tool telemetry. Independent readback confirmed the routine disabled afterward. | Manual dispatch is not an observed 09:00 wall-clock firing. The pinned CLI expects `value` while live history returned `data`; the [bounded GET fallback](application-flow.md#verify-the-routine-and-pause-a-demonstration) recovered the run without redispatch. |
| Shared routine compatibility | The root [Bicep manifest](../../../azure.yaml) now uses supported `agentName`, `cronExpression` and `timeZone`, matching the Terraform authoring path. The regression failed before these three spelling corrections and passed afterward; agent binding, schedule and prompt are preserved. | This is an inherited compatibility repair, not a new Terraform-only feature or proof of a fresh full Bicep deployment. |
| Model routing | The accepted on-demand and manual-routine digests resolved `gpt-latest` to `gpt-6.1-sol-2026-09-29`, including the new version 5 run; benign direct mini calls resolved to `gpt-5.4-mini-2026-03-17`. Both IaC choices retain the configured priority tiers. | Priority is preference, not guaranteed error-triggered failover. The [official routing lab](https://github.com/Azure/aigateway/blob/6204dd56a94d4b54bfb4493974d70b39de93c18f/labs/22-model-routing/README.md#how-it-works) documents preferred-backend errors returning without retrying lower tiers. |
| Bounded governance probe | With a temporary mini token limit of 1, one request succeeded and the next returned 429. Its trace identifies `policy tokenLimit` / `OpenAITokenLimitExceeded`, with no backend call. Exact original model properties and unchanged Terraform state were independently verified after restoration. | API-key caller only, not agent-MI rejection. Token throttling persisted into the cost phase and after restoration; cost rejection was not established and rate testing stopped. The benign safety prompt passed, not blocked. |
| Governance probe recovery | One request after Retry-After returned HTTP 200 at 16:34:53 UTC. Its 12 correlated gateway spans show the intended mini backend and all four original policy configurations. Independent checks confirmed restored properties, unchanged state, active current-source version 3, exact runtime grants and the paused routine. | Seven total probe/recovery requests; recovery made no policy changes, key rotation or counter reset. Successful recovery does not establish cost/rate rejection, safety blocking or the service's internal throttle-reset mechanism. |
| Application demonstration vs. lifecycle | Infrastructure, source-built hosted digest, routine configuration/dispatch and native observability are demonstrated with separate infrastructure, tool and application owners. | No unattended Terraform `azd up` wrapper, full credential lifecycle, scheduler-time firing, recovery/teardown certification or blanket enforcement claim is supplied. |

Storage public access `Disabled` does not provide private connectivity or
establish hosted-agent readiness.

The prepared Linux AMD64 context built locally with normal TLS verification
and a build-scoped CDN mapping; no shared-host DNS, trust or proxy change was
made. A separate native ARM64 attempt encountered TLS `HandshakeFailure` and
remains unqualified. The accepted hosted release used the independently
verified ACR-built Linux AMD64 image.

## Shared-registry source-build qualification

This closes the earlier registry/source-build evidence gap for the existing
deployment. The implementation retains the sole
[`registry_connection` owner](../modules/foundry-agents/main.tf#L111-L137),
orders a non-owning PATCH with both flags true, then requires an
[independent GET postcondition](../modules/foundry-agents/main.tf#L139-L172).
The [sharing output](../modules/foundry-agents/outputs.tf#L10-L14) waits for that
readback but remains a configured value, not image-pull proof. The separate
[`manifest`](../scripts/application_flow.py#L146-L193) and
[`deploy`](../scripts/application_flow.py#L539-L615) path
supplied the runtime evidence below without provisioning again.

| Time on November 7, 2026 (UTC) | Observation |
|---|---|
| 21:17:22 | Shared/default connection readback and ordinary no-change plan accepted. |
| 22:56:56-22:58:45 | Approved integrated source deployment completed; exact run `dt4` succeeded and version 5 was independently identified. |
| 23:06:34-23:07:15 | Version-bound digest completed all three tools; console, agent and gateway evidence correlated. |
| 23:19:41 | Independent post-inference readback preserved versions 3/4/5, principal, scoped roles, tenant authorization, tools, disabled routine, shared/default registry and exact Terraform state bytes. The tag still matched the build digest. |

This was not a fresh environment: existing deployment/build permissions,
project registry access, the two adopted runtime grants and exact-agent tenant
authorization were prerequisites. No permission, capacity or schedule change
was made for the source qualification.

The first instrumented launch built successfully but remained **unconfirmed**
locally because added `--debug` logging created an unexpected extension file.
Its receipt was preserved. A separately approved corrective launch archived and
byte-verified only its own generated diagnostic before retiring it; workspace
and receipt guards stayed unchanged. The ordinary
[`deploy` helper](../scripts/application_flow.py#L539-L615) does not add `--debug`;
this diagnostic handling is not an extra product deployment step.

The accepted trace retains the early MCP 499/`AuthorizationServiceError`.
Completed SSE call items also repeated argument JSON; actual execution was
verified independently from protected tool telemetry with matching call IDs,
session, version and bounded repository arguments. Neither observation was
silently normalized into an error-free claim. All four policy types executed,
but this successful digest proves no new rejection threshold.

Raw captures, prior stopped outcomes and the hash-bound
`final-acceptance.safe.json` receipt remain private. Final acceptance is a new
record; it does not rewrite the original response receipt or earlier failures.
Actual timer firing, cost-limit rejection and Medium safety blocking remain
separate qualification work.

## Run the checks

Use the [canonical offline/preparation route](architecture.md#offline-and-deployment-preparation).
[`Test-Offline.ps1`](../scripts/Test-Offline.ps1) initializes with backend disabled
and read-only locks, then checks formatting, validation, structure, native plans,
semantic resource relationships, Python contracts and PowerShell syntax.
It does not deploy or require Azure credentials; uncached providers need network
access. Passing tests describe their assertions, not missing parity features.

| Test owner | Responsibility |
|---|---|
| [`root.tftest.hcl`](../tests/root.tftest.hcl) | Composition, aliases, input guards, full-root defaults, safety settings and opt-in hosted-identity roles with independent switches and exclusive ownership |
| [`gateway.tftest.hcl`](../tests/gateway.tftest.hcl) | Standalone gateway, frontend, exporter destination, callers and safety enum rejection |
| [`telemetry.tftest.hcl`](../tests/telemetry.tftest.hcl) | Native readiness, scoped publisher/exporter and rejection of stale or mismatched handoffs |
| [`models.tftest.hcl`](../tests/models.tftest.hcl) | Model profile, deployment guards and gateway-only safety metadata without changing the backend filter |
| [`agents.tftest.hcl`](../tests/agents.tftest.hcl) | Independent support resources, network inputs and monitoring connection |
| [`examples.tftest.hcl`](../tests/examples.tftest.hcl) | Four standalone roots, external-pregrant configuration and existing-model safety opt-in |
| [`examples-telemetry.tftest.hcl`](../tests/examples-telemetry.tftest.hcl) | Native handoff forwarding through both gateway-bearing examples |
| [`check_contracts.py`](../tests/check_contracts.py) | API bodies, exact grants, routes, sole ownership and dependency edges |
| [`test_environment_adapter.py`](../tests/test_environment_adapter.py) | Nonsecret allow-list, Responses compatibility and resource/endpoint relationships |
| [`test_live_readback.py`](../tests/test_live_readback.py) | GET-only scope, omissions, safe receipts and no overwrite |
| [`test_telemetry_readiness.py`](../tests/test_telemetry_readiness.py) | Readiness polling, CLI/ARM context, endpoint validation, bounds, redaction and explicit no-overwrite handoffs |
| [`test_toolchain.py`](../tests/test_toolchain.py) | Explicit ownership/credentials, complete request bodies, conditional rotation, uncertain outcomes, Toolbox versions, redaction and isolated handoffs |
| [`test_application_flow.py`](../tests/test_application_flow.py) | Offline snapshot generation, context-bound handoffs, app-only manifests, independent deployment gates, installed versions, isolated credentials, drift detection and single-attempt receipts |
| [`prepare_application_ci.py`](../tests/prepare_application_ci.py) | Synthetic offline handoffs through the real application `prepare` entry point; CI builds and smokes the resulting isolated context |
| [`test_github_mcp_middleware.py`](../../../tests/test_github_mcp_middleware.py) | Bounded scan metadata, saturation/continuation handling and coverage captured before filtering |
| [`test_agent_runtime.py`](../../../tests/test_agent_runtime.py) | Shared runtime/client behavior and root routine-authoring compatibility |

## Remaining qualification boundaries

The accepted demonstrations do not establish the broader guarantees below.
Each requires separate, explicitly scoped authorization and validation:

- Actual scheduler-time firing, subsequent releases, recovery and teardown.
- Real credential rotation/revocation, diagnostics-wide secret handling,
  negative authorization and policy rejection scenarios not established above.
- Other regions, build/registry modes and exporter migration.

Use [read-only field qualification](live-readback.md) alongside a current
ordinary plan, not as a substitute for runtime tests. Omitted properties remain
unknown; successful inference does not make them independently verified.
See [ownership and differences](architecture.md#preserved-contracts-and-deliberate-differences)
and the [tool/credential boundary](tool-credential-boundary.md) before deployment.
