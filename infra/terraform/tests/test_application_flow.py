"""Exercise the real offline application bridge with fake azd processes only."""

import contextlib
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from test_environment_adapter import CONTRACT
from test_toolchain import SUBSCRIPTION, TENANT, bootstrap, receipt

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
SPEC = importlib.util.spec_from_file_location("application_flow", SCRIPTS / "application_flow.py")
flow = importlib.util.module_from_spec(SPEC)
with mock.patch.object(sys, "path", [str(SCRIPTS), *sys.path]):
    SPEC.loader.exec_module(flow)

KEY = "synthetic-gateway-runtime-key"
GITHUB_KEY = "synthetic-unselected-github-key"
AGENT = "fixture-digest"
HOST_SHELL = shutil.which("pwsh" if os.name == "nt" else "sh")
RUN_GUARD = subprocess.run


class ApplicationFlowTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(mock.patch.stopall)
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.workspace = self.root / "application"
        self.contract_path = self.root / "contract.json"
        self.bootstrap_path = self.root / "bootstrap.json"
        self.receipt_path = self.root / "tool.receipt.jsonl"
        self.bootstrap = bootstrap(connected=True)
        self.contract = copy.deepcopy(CONTRACT)
        self.contract["gateway"].update(
            id=self.bootstrap["gateway_id"], endpoint=self.bootstrap["gateway_endpoint"],
            monitoring={"configuration_status": "configured"},
        )
        self.contract["integration"] = {
            "gateway_model_access_enabled": True, "gateway_tool_access_enabled": True,
            "registry_connection_shared": True,
            "remote_tool_connection_id": self.bootstrap["remote_tool_connection_id"],
            "remote_tool_endpoint": self.bootstrap["remote_tool_endpoint"],
        }
        self.receipt = receipt(connected=True)
        self.receipt["operation"] = "create-toolbox"
        self.receipt["toolbox"] = flow.tools.toolbox_metadata(self.bootstrap, "digest", "7")
        self.process = mock.patch.object(flow.subprocess, "run",
                                         side_effect=AssertionError("Unexpected CLI invocation")).start()
        mock.patch.object(flow.shutil, "which", return_value="azd.exe").start()
        mock.patch.dict(os.environ, {
            "SELECTED_GATEWAY_KEY": KEY, "GITHUB_TOKEN": GITHUB_KEY,
            "AZURE_CLIENT_SECRET": "synthetic-unselected-client-secret",
            "AZURE_AI_GATEWAY_API_KEY": "synthetic-ambient-gateway-key",
            "AZD_DEBUG": "true", flow.SCHEDULE_GATE: "true",
        }).start()

    def call(self, operation, extra=()):
        args = [operation, "--workspace", str(self.workspace), "--subscription-id", SUBSCRIPTION,
                "--tenant-id", TENANT, *extra]
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                code = flow.main(args)
            except SystemExit as error:
                code = error.code
        output = stdout.getvalue() + stderr.getvalue()
        for secret in (KEY, GITHUB_KEY, "synthetic-ambient-gateway-key"):
            self.assertNotIn(secret, output)
        return code, output

    def prepare(self, extra=()):
        self.contract_path.write_text(json.dumps(self.contract), encoding="utf-8")
        self.bootstrap_path.write_text(json.dumps(self.bootstrap), encoding="utf-8")
        self.receipt_path.write_text(json.dumps(self.receipt) + "\n", encoding="utf-8")
        return self.call("prepare", [
            "--contract", str(self.contract_path), "--bootstrap", str(self.bootstrap_path),
            "--tool-receipt", str(self.receipt_path), "--repository", "example/repository",
            "--agent-name", AGENT, *extra,
        ])

    def spec(self):
        return json.loads((self.workspace / "prepared.json").read_text(encoding="utf-8"))

    def dotenv(self):
        return self.workspace / ".azure" / "fixture" / ".env"

    def records(self, stage="agent"):
        return [json.loads(line) for line in
                (self.workspace / f"{stage}.receipt.jsonl").read_text(encoding="utf-8").splitlines()]

    def fake_cli(self, command, **kwargs):
        self.assertEqual(kwargs["cwd"], self.workspace.resolve())
        self.assertEqual(kwargs["stdin"], subprocess.DEVNULL)
        self.assertEqual(kwargs["stderr"], subprocess.DEVNULL)
        self.assertGreater(kwargs["timeout"], 0)
        environment = kwargs["env"]
        for name in ("SELECTED_GATEWAY_KEY", "GITHUB_TOKEN", "AZURE_CLIENT_SECRET",
                     "AZURE_AI_GATEWAY_API_KEY", "AZD_DEBUG"):
            self.assertNotIn(name, environment)
        if command[1] == "version":
            self.assertNotIn(flow.KEY_VARIABLE, environment)
            return subprocess.CompletedProcess(command, 0, stdout="azd version 1.37.2 (commit fixture)\n")
        if command[1:3] == ["extension", "list"]:
            self.assertNotIn(flow.KEY_VARIABLE, environment)
            return subprocess.CompletedProcess(command, 0, stdout=json.dumps([
                {"id": name, "version": "99.0.0", "installedVersion": version}
                for name, version in flow.EXTENSIONS.items()
            ]))
        self.assertEqual(command[1], "deploy")
        self.assertEqual(command[3:], ["--environment", "fixture", "--no-prompt"])
        self.assertEqual(kwargs["stdout"], subprocess.DEVNULL)
        if command[2] == AGENT:
            self.assertEqual(environment[flow.AGENT_GATE], "true")
            self.assertEqual(environment[flow.SCHEDULE_GATE], "false")
            self.assertEqual(environment[flow.STAGE_VARIABLE], "agent")
            self.assertEqual(self.records()[-1]["status"], "pending")
            prefix = "AGENT_FIXTURE_DIGEST_"
            values = {
                "NAME": AGENT, "VERSION": "1",
                "ENDPOINT": self.bootstrap["project_endpoint"] + f"/agents/{AGENT}/versions/1",
                "RESPONSES_ENDPOINT": self.bootstrap["project_endpoint"] + "/openai/responses?agent=name&api-version=v1",
            }
            with self.dotenv().open("a", encoding="utf-8") as stream:
                stream.writelines(f"{prefix}{key}={value if key == 'VERSION' else json.dumps(value)}\n"
                                  for key, value in values.items())
                stream.write('SERVICE_FIXTURE_DIGEST_IMAGE_NAME="registry.azurecr.io/digest@sha256:0123456789"\n')
        else:
            self.assertEqual(command[2], AGENT + "-daily")
            self.assertEqual(environment[flow.AGENT_GATE], "false")
            self.assertEqual(environment[flow.SCHEDULE_GATE], "true")
            self.assertEqual(environment[flow.STAGE_VARIABLE], "schedule")
            self.assertNotIn(flow.KEY_VARIABLE, environment)
            self.assertEqual(self.records("schedule")[-1]["status"], "pending")
        return subprocess.CompletedProcess(command, 0, stdout=KEY, stderr=GITHUB_KEY)

    def launch_agent(self, authentication=("--managed-identity",)):
        self.process.side_effect = self.fake_cli
        return self.call("deploy-agent", ["--confirm-agent-deployment", *authentication])

    def test_prepare_is_offline_and_copies_only_application_build_files(self):
        self.contract["discarded_secret"] = KEY
        self.assertEqual(self.prepare()[0], 0)
        self.process.assert_not_called()
        self.assertEqual({path.name for path in (self.workspace / "app").iterdir()}, set(flow.APP_FILES))
        for name in flow.APP_FILES:
            self.assertEqual((self.workspace / "app" / name).read_bytes(), (flow.SOURCE / name).read_bytes())
        for path in self.workspace.rglob("*"):
            if path.is_file():
                self.assertNotIn(KEY.encode(), path.read_bytes())
                self.assertNotIn(GITHUB_KEY.encode(), path.read_bytes())
        spec = self.spec()
        self.assertEqual(spec["environment"]["AZD_AGENT_SKIP_ROLE_ASSIGNMENTS"], "true")
        self.assertEqual(spec["environment"]["USE_EXISTING_AI_PROJECT"], "true")
        self.assertNotIn("AZURE_AI_GATEWAY_API_KEY", spec["environment"])
        self.assertNotIn(flow.KEY_VARIABLE, spec["environment"])
        manifest = json.loads((self.workspace / "azure.yaml").read_text())
        self.assertEqual(set(manifest["services"]), {AGENT, AGENT + "-daily"})
        self.assertNotIn("infra", manifest)
        self.assertEqual(set(manifest["hooks"]), {"preprovision", "predown"})
        agent = manifest["services"][AGENT]
        self.assertNotIn("uses", agent)
        self.assertNotIn("environmentVariables", agent)
        self.assertEqual(agent["env"]["AZURE_AI_GATEWAY_API_KEY"], "${" + flow.KEY_VARIABLE + "}")
        routine = manifest["services"][AGENT + "-daily"]
        self.assertEqual(routine["condition"], "${" + flow.SCHEDULE_GATE + "}")
        self.assertEqual(routine["action"]["agentName"], AGENT)
        self.assertIn("example/repository", routine["action"]["input"])
        self.assertEqual(set(routine["triggers"]["default"]), {"type", "cronExpression", "timeZone"})

    def test_prepare_accepts_nonsensitive_contract_envelope(self):
        self.contract = {"deployment_contract": {"sensitive": False, "value": self.contract},
                         "unrelated_secret": {"sensitive": True, "value": KEY}}
        self.assertEqual(self.prepare()[0], 0)
        self.assertNotIn(KEY, (self.workspace / "prepared.json").read_text())

    @unittest.skipUnless(HOST_SHELL, "The host-native shell is not installed.")
    def test_generated_hooks_enforce_operation_and_infrastructure_boundaries(self):
        platform = "windows" if os.name == "nt" else "posix"
        checks = [(flow.guard(), None, False), (flow.guard("agent"), None, False),
                  (flow.guard("agent"), "agent", True), (flow.guard("agent"), "schedule", False),
                  (flow.guard("schedule"), None, False), (flow.guard("schedule"), "agent", False),
                  (flow.guard("schedule"), "schedule", True)]
        for hook, stage, allowed in checks:
            with self.subTest(stage=stage, allowed=allowed, hook=hook[platform]["run"]):
                environment = flow.child_environment()
                if stage is not None:
                    environment[flow.STAGE_VARIABLE] = stage
                command = [HOST_SHELL]
                if os.name == "nt":
                    command += ["-NoProfile", "-NonInteractive", "-Command"]
                else:
                    command += ["-c"]
                result = RUN_GUARD(
                    [*command, hook[platform]["run"]], env=environment, stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15, check=False,
                )
                self.assertEqual(result.returncode == 0, allowed)
        self.process.assert_not_called()

    def test_prepare_forwards_custom_alias_selection(self):
        aliases = self.contract["models"]["aliases"]
        aliases["custom-primary"] = aliases.pop("primary-router")
        aliases["custom-mini"] = aliases.pop("mini-router")
        aliases["custom-primary"]["alias_name"] = "custom-primary-route"
        aliases["custom-mini"]["alias_name"] = "custom-mini-route"
        self.assertEqual(self.prepare([
            "--model-alias-key", "custom-primary", "--mini-model-alias-key", "custom-mini",
        ])[0], 0)
        values = self.spec()["environment"]
        self.assertEqual(values["AZURE_AI_GATEWAY_MODEL"], "custom-primary-route")
        self.assertEqual(values["AZURE_AI_GATEWAY_MINI_MODEL"], "custom-mini-route")

    def test_prepare_rejects_mismatched_repository_context_and_connection(self):
        for target, key, value in (
            ("contract", "subscription_id", TENANT),
            ("bootstrap", "project_endpoint", "https://other.services.ai.azure.com/api/projects/project"),
            ("bootstrap", "remote_tool_connection_id", None),
            ("integration", "remote_tool_endpoint", "https://gateway.example.invalid/other/mcp"),
            ("integration", "registry_connection_shared", False),
            ("integration", "gateway_tool_access_enabled", False),
            ("configuration", "repository", "other/repository"),
        ):
            with self.subTest(target=target, key=key):
                source = {"contract": self.contract, "bootstrap": self.bootstrap,
                          "integration": self.contract["integration"],
                          "configuration": self.receipt["configuration"]}[target]
                previous = source[key]
                source[key] = value
                self.assertNotEqual(self.prepare()[0], 0)
                self.assertFalse(self.workspace.exists())
                source[key] = previous
        self.process.assert_not_called()

    def test_prepare_rejects_unconfirmed_unversioned_or_wrong_toolbox(self):
        for change in (
            {"status": "unconfirmed"}, {"toolbox": {"name": "digest"}},
            {"toolbox": {**self.receipt["toolbox"], "endpoint": "https://other.example.invalid/mcp"}},
            {"toolserver": {**self.receipt["toolserver"], "endpoint": "https://gateway.example.invalid/other/mcp"}},
        ):
            with self.subTest(change=tuple(change)):
                previous = copy.deepcopy(self.receipt)
                self.receipt.update(change)
                self.assertNotEqual(self.prepare()[0], 0)
                self.assertFalse(self.workspace.exists())
                self.receipt = previous

    def test_prepare_stops_on_pending_telemetry_and_interpolated_values(self):
        self.contract["gateway"]["monitoring"]["configuration_status"] = "pending"
        self.assertNotEqual(self.prepare()[0], 0)
        self.contract["gateway"]["monitoring"]["configuration_status"] = "configured"
        self.contract["location"] = "${SELECTED_GATEWAY_KEY}"
        self.assertNotEqual(self.prepare()[0], 0)
        self.assertFalse(self.workspace.exists())

    def test_prepare_never_overwrites_or_creates_build_context_inside_repository(self):
        self.assertEqual(self.prepare()[0], 0)
        before = (self.workspace / "prepared.json").read_bytes()
        self.assertNotEqual(self.prepare()[0], 0)
        self.assertEqual(before, (self.workspace / "prepared.json").read_bytes())
        self.workspace = flow.SOURCE / "must-not-create-application-flow-test"
        self.assertNotEqual(self.prepare()[0], 0)
        self.assertFalse(self.workspace.exists())

    def test_explicit_confirmation_and_authentication_are_required_before_cli(self):
        self.assertEqual(self.prepare()[0], 0)
        for extra in ([], ["--managed-identity"], ["--confirm-agent-deployment"],
                      ["--confirm-agent-deployment", "--managed-identity", "--gateway-key-env", "SELECTED_GATEWAY_KEY"],
                      ["--confirm-agent-deployment", "--managed-identity", "--tenant-id", SUBSCRIPTION],
                      ["--confirm-agent-deployment", "--managed-identity", "--subscription-id", TENANT]):
            with self.subTest(extra=extra):
                self.assertNotEqual(self.call("deploy-agent", extra)[0], 0)
        self.process.assert_not_called()
        self.assertFalse((self.workspace / "agent.receipt.jsonl").exists())

    def test_managed_identity_needs_model_grant(self):
        self.contract["integration"]["gateway_model_access_enabled"] = False
        self.assertEqual(self.prepare()[0], 0)
        self.assertNotEqual(self.launch_agent()[0], 0)
        self.process.assert_not_called()

    def test_managed_identity_deploys_only_agent_without_ambient_credentials(self):
        self.assertEqual(self.prepare()[0], 0)
        self.assertEqual(self.launch_agent()[0], 0)
        self.assertEqual(len(self.process.call_args_list), 3)
        self.assertEqual(self.process.call_args.kwargs["env"][flow.KEY_VARIABLE], "")
        self.assertEqual([record["status"] for record in self.records()], ["pending", "cli-completed"])
        self.assertFalse((self.workspace / "schedule.receipt.jsonl").exists())

    def test_selected_key_reaches_only_agent_process_not_files_or_inspections(self):
        self.assertEqual(self.prepare()[0], 0)
        self.assertEqual(self.launch_agent(("--gateway-key-env", "SELECTED_GATEWAY_KEY"))[0], 0)
        self.assertEqual(self.process.call_args.kwargs["env"][flow.KEY_VARIABLE], KEY)
        self.assertEqual(self.records()[-1]["authentication"], "api-key")
        for path in self.workspace.rglob("*"):
            if path.is_file():
                self.assertNotIn(KEY.encode(), path.read_bytes())

    def test_rejects_missing_key_literal_and_tool_credential_selection(self):
        self.assertEqual(self.prepare()[0], 0)
        for selected in ("ABSENT_GATEWAY_KEY", KEY, "GITHUB_TOKEN", "PATH", flow.KEY_VARIABLE):
            with self.subTest(selected=selected):
                self.assertNotEqual(self.launch_agent(("--gateway-key-env", selected))[0], 0)
        self.process.assert_not_called()

    def test_old_prerelease_and_unreviewed_cli_versions_stop_before_intent(self):
        self.assertEqual(self.prepare()[0], 0)
        for version in ("1.35.1", "1.37.0-beta.1", "1.38.0"):
            with self.subTest(version=version):
                self.process.side_effect = lambda command, **kwargs: subprocess.CompletedProcess(
                    command, 0, stdout=f"azd version {version} (commit fixture)")
                self.assertNotEqual(self.call("deploy-agent", ["--confirm-agent-deployment", "--managed-identity"])[0], 0)
                self.assertFalse((self.workspace / "agent.receipt.jsonl").exists())
        self.assertEqual(self.process.call_count, 3)

    def test_catalog_version_cannot_substitute_for_installed_dependency(self):
        self.assertEqual(self.prepare()[0], 0)
        for installed in (None, "1.0.0-beta.18", "1.0.1"):
            with self.subTest(installed=installed):
                def fake(command, **kwargs):
                    if command[1] == "version":
                        return self.fake_cli(command, **kwargs)
                    inventory = [{"id": name, "version": "1.0.0", "installedVersion": version}
                                 for name, version in flow.EXTENSIONS.items()]
                    inventory[0]["installedVersion"] = installed
                    return subprocess.CompletedProcess(command, 0, stdout=json.dumps(inventory))
                self.process.side_effect = fake
                self.assertNotEqual(self.call("deploy-agent", ["--confirm-agent-deployment", "--managed-identity"])[0], 0)
                self.assertFalse((self.workspace / "agent.receipt.jsonl").exists())

    def test_missing_azd_is_not_installed_automatically(self):
        self.assertEqual(self.prepare()[0], 0)
        with mock.patch.object(flow.shutil, "which", return_value=None):
            self.assertNotEqual(self.launch_agent()[0], 0)
        self.process.assert_not_called()

    def test_modified_build_file_manifest_or_extra_file_stops_before_cli(self):
        self.assertEqual(self.prepare()[0], 0)
        for path in (self.workspace / "app" / "main.py", self.workspace / "azure.yaml",
                     self.workspace / "app" / ".env"):
            with self.subTest(path=path.name):
                before = path.read_bytes() if path.exists() else None
                path.write_bytes(b"synthetic-drift")
                self.assertNotEqual(self.launch_agent()[0], 0)
                if before is None:
                    path.unlink()
                else:
                    path.write_bytes(before)
        infrastructure = self.workspace / "infra"
        infrastructure.mkdir()
        (infrastructure / "main.hooks.yaml").write_text(
            "predeploy:\n  shell: sh\n  run: echo should-not-run\n", encoding="utf-8")
        self.assertNotEqual(self.launch_agent()[0], 0)
        self.process.assert_not_called()

    def test_drift_during_tooling_inspection_stops_before_deployment_intent(self):
        self.assertEqual(self.prepare()[0], 0)
        def fake(command, **kwargs):
            result = self.fake_cli(command, **kwargs)
            if command[1:3] == ["extension", "list"]:
                (self.workspace / "app" / "main.py").write_text("synthetic drift", encoding="utf-8")
            return result
        self.process.side_effect = fake
        self.assertNotEqual(self.call("deploy-agent", ["--confirm-agent-deployment", "--managed-identity"])[0], 0)
        self.assertEqual(self.process.call_count, 2)
        self.assertFalse((self.workspace / "agent.receipt.jsonl").exists())

    def test_linked_application_file_is_rejected(self):
        self.assertEqual(self.prepare()[0], 0)
        original = flow.linked
        with mock.patch.object(flow, "linked", side_effect=lambda path: path.name == "main.py" or original(path)):
            self.assertNotEqual(self.launch_agent()[0], 0)
        self.process.assert_not_called()

    def test_modified_initial_dotenv_or_config_stops_before_cli(self):
        self.assertEqual(self.prepare()[0], 0)
        for path in (self.dotenv(), self.dotenv().with_name("config.json")):
            before = path.read_bytes()
            path.write_bytes(before + b" ")
            self.assertNotEqual(self.launch_agent()[0], 0)
            path.write_bytes(before)
        self.process.assert_not_called()

    def test_schedule_requires_confirmation_and_successful_agent_receipt(self):
        self.assertEqual(self.prepare()[0], 0)
        self.assertNotEqual(self.call("enable-schedule")[0], 0)
        self.assertNotEqual(self.call("enable-schedule", ["--confirm-enable-schedule"])[0], 0)
        self.process.assert_not_called()
        self.assertFalse((self.workspace / "schedule.receipt.jsonl").exists())

    def test_schedule_is_separate_and_never_redeploys_agent_or_receives_key(self):
        self.assertEqual(self.prepare()[0], 0)
        self.assertEqual(self.launch_agent(("--gateway-key-env", "SELECTED_GATEWAY_KEY"))[0], 0)
        self.assertEqual(self.call("enable-schedule", ["--confirm-enable-schedule"])[0], 0)
        deployments = [call.args[0][2] for call in self.process.call_args_list if call.args[0][1] == "deploy"]
        self.assertEqual(deployments, [AGENT, AGENT + "-daily"])
        self.assertEqual(self.records("schedule")[-1]["status"], "cli-completed")
        self.process.reset_mock()
        self.assertNotEqual(self.launch_agent()[0], 0)
        self.assertNotEqual(self.call("enable-schedule", ["--confirm-enable-schedule"])[0], 0)
        self.process.assert_not_called()

    def test_schedule_rejects_changed_agent_environment_or_receipt(self):
        self.assertEqual(self.prepare()[0], 0)
        self.assertEqual(self.launch_agent()[0], 0)
        self.process.reset_mock()
        receipt_path = self.workspace / "agent.receipt.jsonl"
        for path in (self.dotenv(), self.dotenv().with_name("config.json"), receipt_path):
            with self.subTest(path=path.name):
                before = path.read_bytes()
                path.write_bytes(before.rstrip(b"\n") + b" ")
                self.assertNotEqual(self.call("enable-schedule", ["--confirm-enable-schedule"])[0], 0)
                path.write_bytes(before)
        self.process.assert_not_called()

    def test_wrong_receipt_binding_cannot_authorize_schedule(self):
        self.assertEqual(self.prepare()[0], 0)
        self.assertEqual(self.launch_agent()[0], 0)
        records = self.records()
        for record in records:
            record["prepared_sha256"] = "0" * 64
        (self.workspace / "agent.receipt.jsonl").write_text(
            "".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")
        self.process.reset_mock()
        self.assertNotEqual(self.call("enable-schedule", ["--confirm-enable-schedule"])[0], 0)
        self.process.assert_not_called()

    def test_failure_retains_uncertain_intent_and_never_retries_or_enables_schedule(self):
        self.assertEqual(self.prepare()[0], 0)
        def fake(command, **kwargs):
            if command[1] == "deploy":
                return subprocess.CompletedProcess(command, 1, stdout=KEY, stderr=GITHUB_KEY)
            return self.fake_cli(command, **kwargs)
        self.process.side_effect = fake
        args = ["--confirm-agent-deployment", "--gateway-key-env", "SELECTED_GATEWAY_KEY"]
        self.assertNotEqual(self.call("deploy-agent", args)[0], 0)
        self.assertEqual([record["status"] for record in self.records()], ["pending", "unconfirmed"])
        self.assertEqual(self.process.call_count, 3)
        self.assertNotEqual(self.call("deploy-agent", args)[0], 0)
        self.assertNotEqual(self.call("enable-schedule", ["--confirm-enable-schedule"])[0], 0)
        self.assertEqual(self.process.call_count, 3)

    def test_timeout_output_is_withheld_and_receipt_stays_unconfirmed(self):
        self.assertEqual(self.prepare()[0], 0)
        def fake(command, **kwargs):
            if command[1] == "deploy":
                raise subprocess.TimeoutExpired(command, kwargs["timeout"], output=KEY, stderr=GITHUB_KEY)
            return self.fake_cli(command, **kwargs)
        self.process.side_effect = fake
        self.assertNotEqual(self.call("deploy-agent", ["--confirm-agent-deployment", "--managed-identity"])[0], 0)
        self.assertEqual(self.records()[-1]["status"], "unconfirmed")

    def test_success_without_matching_registered_agent_is_not_completion(self):
        self.assertEqual(self.prepare()[0], 0)
        def fake(command, **kwargs):
            if command[1] == "deploy":
                return subprocess.CompletedProcess(command, 0)
            return self.fake_cli(command, **kwargs)
        self.process.side_effect = fake
        self.assertNotEqual(self.call("deploy-agent", ["--confirm-agent-deployment", "--managed-identity"])[0], 0)
        self.assertEqual(self.records()[-1]["status"], "unconfirmed")

    def test_unexpected_key_persistence_stops_completion_without_printing_it(self):
        self.assertEqual(self.prepare()[0], 0)
        def fake(command, **kwargs):
            result = self.fake_cli(command, **kwargs)
            if command[1] == "deploy":
                with self.dotenv().open("a", encoding="utf-8") as stream:
                    stream.write(f"AZURE_AI_GATEWAY_API_KEY={json.dumps(KEY)}\n")
            return result
        self.process.side_effect = fake
        self.assertNotEqual(self.call("deploy-agent", [
            "--confirm-agent-deployment", "--gateway-key-env", "SELECTED_GATEWAY_KEY",
        ])[0], 0)
        self.assertEqual(self.records()[-1]["status"], "unconfirmed")
        self.assertNotIn(KEY, (self.workspace / "agent.receipt.jsonl").read_text())

    def test_receipt_must_be_durable_before_deployment_process_starts(self):
        self.assertEqual(self.prepare()[0], 0)
        self.process.side_effect = self.fake_cli
        with mock.patch.object(flow.tools.os, "fsync", side_effect=OSError("synthetic disk failure")):
            self.assertNotEqual(self.call("deploy-agent", ["--confirm-agent-deployment", "--managed-identity"])[0], 0)
        self.assertEqual(self.process.call_count, 2)


if __name__ == "__main__":
    unittest.main()
