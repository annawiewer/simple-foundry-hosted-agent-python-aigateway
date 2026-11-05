"""Explicit-credential GitHub tool lifecycle, separate from Terraform and azd.

Mutations require exclusive ownership. Create is NOT atomic: the selected
ToolServer API does not enforce If-None-Match. Never run competing writers.
Only nonsecret receipts/handoffs are persisted; mutations are never retried.
"""

import argparse
import copy
import hashlib
import ipaddress
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from urllib.parse import urlsplit

from export_environment import arm_id, endpoint

ARM = "https://management.azure.com"
API = "2025-09-01-preview"
CONNECTION_API = "2025-06-01"
AUDIENCE = "https://azure-api.net/aigateway"
GITHUB_MCP = "https://api.githubcopilot.com/mcp/"
TOOLS = "list_pull_requests,list_issues,actions_list"
MAX_BYTES = 1024 * 1024
UUID = r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}"
RESOURCE_NAME = r"[A-Za-z0-9][A-Za-z0-9_.-]*"
BINDING_KEYS = {
    "subscription_id", "gateway_id", "workspace_id", "gateway_endpoint",
    "api_version", "project_id", "project_endpoint",
}
BOOTSTRAP_KEYS = BINDING_KEYS | {
    "version", "tool_access_enabled", "remote_tool_connection_id", "remote_tool_endpoint",
}
SERVER_ACTIONS = {"create-toolserver", "rotate-credential", "inspect-toolserver"}
BOX_ACTIONS = {"create-toolbox", "inspect-toolbox"}
WRITE_ACTIONS = {"create-toolserver", "rotate-credential", "create-toolbox"}


class ToolchainError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ToolchainError(message)


def remaining(deadline, limit=30):
    seconds = deadline - time.monotonic()
    require(seconds > 0, "Deadline reached. Inspect the receipt; do not blindly repeat a mutation.")
    return min(limit, seconds)


def read_text(path):
    with path.open("rb") as stream:
        value = stream.read(MAX_BYTES + 1)
    require(len(value) <= MAX_BYTES, "Input exceeds the bounded size; contents withheld.")
    return value.decode("utf-8-sig")


def origin(value):
    return urlsplit(endpoint(value)).netloc.lower().removesuffix(":443")


def mcp_endpoint(value, bootstrap):
    endpoint(value)
    require(origin(value) == origin(bootstrap["gateway_endpoint"])
            and urlsplit(value).path not in ("", "/")
            and "%" not in urlsplit(value).path,
            "The returned MCP endpoint must be credential-free and on this gateway; no route is guessed.")
    return value


def validate_bootstrap(value, subscription):
    require(re.fullmatch(UUID, subscription) is not None, "An explicit subscription UUID is required.")
    require(isinstance(value, dict) and set(value) == BOOTSTRAP_KEYS
            and type(value["version"]) is int and value["version"] == 1
            and value["api_version"] == API
            and type(value["tool_access_enabled"]) is bool,
            "Use the applied version-1 gateway_toolchain_bootstrap output, not state or credentials.")
    require(value["subscription_id"].lower() == subscription.lower(), "Bootstrap subscription mismatch.")
    gateway = arm_id(value["gateway_id"], rf"Microsoft\.ApiManagement/aigateways/{RESOURCE_NAME}", subscription)
    project = arm_id(
        value["project_id"],
        rf"Microsoft\.CognitiveServices/accounts/{RESOURCE_NAME}/projects/{RESOURCE_NAME}", subscription,
    )
    require(value["workspace_id"].lower() == (gateway + "/workspaces/default").lower(),
            "Only the declared gateway's default workspace is supported.")
    require(urlsplit(endpoint(value["gateway_endpoint"])).path in ("", "/"),
            "The gateway bootstrap endpoint must be an origin.")
    require(endpoint(value["project_endpoint"]) ==
            f"https://{project.split('/')[-3].lower()}.services.ai.azure.com/api/projects/{project.split('/')[-1]}",
            "The project endpoint must match the declared public-cloud project.")
    connection = value["remote_tool_connection_id"]
    target = value["remote_tool_endpoint"]
    require((connection is None) == (target is None), "The RemoteTool handoff is incomplete.")
    if connection is not None:
        require(connection.lower() == (project + "/connections/aigw-github").lower(),
                "The RemoteTool must be the Terraform-owned aigw-github connection.")
        mcp_endpoint(target, value)
    return value


def configuration(repository, cidrs, owner=None):
    require(isinstance(repository, str) and
            re.fullmatch(rf"{RESOURCE_NAME}/{RESOURCE_NAME}", repository) is not None,
            "Select the repository explicitly as owner/repository.")
    require(isinstance(cidrs, list), "MCP caller CIDRs must be a list.")
    networks = [ipaddress.ip_network(cidr, strict=False) for cidr in cidrs]
    require(all(network.prefixlen > 0 for network in networks), "MCP caller CIDRs cannot use a zero prefix.")
    owner = str(uuid.uuid4()) if owner is None else owner
    require(isinstance(owner, str) and re.fullmatch(UUID, owner) is not None, "Invalid ownership receipt.")
    return {"owner_id": owner, "repository": repository,
            "allowed_client_cidrs": sorted({str(network) for network in networks})}


def server_body(config, credential=None):
    policy = {"type": "contentSafety", **{
        category + "Severity": "Medium" for category in ("hate", "selfHarm", "sexual", "violence")
    }}
    policies = [policy]
    if config["allowed_client_cidrs"]:
        policies.append({"type": "ipFilter", "action": "Allow", "cidrRanges": config["allowed_client_cidrs"]})
    headers = {"X-MCP-Readonly": ["true"], "X-MCP-Tools": [TOOLS]}
    if credential is not None:
        headers["Authorization"] = ["Bearer " + credential]
    return {"properties": {
        "displayName": "GitHub repository digest",
        "description": "Read-only GitHub tools for repository digests. Owner: terraform-toolchain/" + config["owner_id"],
        "type": "mcp", "failureMode": "failClosed", "policies": policies,
        "endpoints": [{"namespace": "github", "kind": "mcp",
                       "mcp": {"url": GITHUB_MCP, "transport": "streamableHttp"},
                       "credentials": {"type": "header", "headers": headers}}],
    }}


def config_hash(config):
    document = {"configuration": config, "body": server_body(config)}
    return hashlib.sha256(json.dumps(document, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def binding(bootstrap, tenant):
    return {**{key: bootstrap[key] for key in BINDING_KEYS}, "tenant_id": tenant}


def read_receipt(path, bootstrap, tenant):
    text = read_text(path)
    complete = text.split("\n")[:-1]
    require(complete, "No complete receipt record. Do not adopt an existing resource.")
    records = [json.loads(line) for line in complete]
    immutable = None
    for record in records:
        require(isinstance(record, dict) and set(record) <= {
            "version", "operation", "status", "binding", "configuration",
            "configuration_hash", "mutation_attempted", "toolserver", "toolbox",
        }, "Invalid receipt shape; contents withheld.")
        config = record["configuration"]
        require(isinstance(config, dict) and set(config) == {"owner_id", "repository", "allowed_client_cidrs"},
                "Invalid nonsecret configuration receipt.")
        require(config == configuration(config["repository"], config["allowed_client_cidrs"], config["owner_id"]),
                "Receipt CIDRs must be normalized.")
        require(type(record["version"]) is int and record["version"] == 1
                and record["operation"] in SERVER_ACTIONS | BOX_ACTIONS
                and record["status"] in {"prepared", "pending", "configured", "unconfirmed"}
                and type(record["mutation_attempted"]) is bool
                and record["binding"] == binding(bootstrap, tenant)
                and record["configuration_hash"] == config_hash(config),
                "Receipt context or configuration mismatch; no adoption or update.")
        if "toolserver" in record:
            server = record["toolserver"]
            require(isinstance(server, dict) and set(server) == {"etag", "endpoint"},
                    "Only verified nonsecret ToolServer metadata belongs in a receipt.")
            valid_etag(server["etag"])
            mcp_endpoint(server["endpoint"], bootstrap)
        if "toolbox" in record:
            box = record["toolbox"]
            require(isinstance(box, dict) and set(box) in (
                {"name"}, {"name", "version", "endpoint"},
            ), "Only verified nonsecret Toolbox metadata belongs in a receipt.")
            selected_name = toolbox_name(box["name"])
            if "version" in box:
                require(box == toolbox_metadata(bootstrap, selected_name, box["version"]),
                        "Toolbox receipt endpoint does not match the project and version.")
        current = (record["binding"], config, record["configuration_hash"], record["operation"])
        require(immutable is None or immutable == current, "Receipt changes its ownership or operation.")
        immutable = current
    result = copy.deepcopy(records[-1])
    if not text.endswith("\n"):
        result["status"] = "unconfirmed"
    return result


def safe_json(document, secrets):
    result = json.dumps(document, sort_keys=True)
    require(not any(secret and secret in result for secret in secrets),
            "Response metadata failed credential-exclusion checks; values withheld.")
    return result


def record_status(stream, record, status, secrets):
    record["status"] = status
    stream.write(safe_json(record, secrets) + "\n")
    stream.flush()
    os.fsync(stream.fileno())


def new_output(path, inputs, tfvars=False):
    require(not path.exists() and path.parent.is_dir()
            and path.resolve() not in {item.resolve() for item in inputs if item is not None},
            "Choose distinct new output files in an existing private directory; overwrite is forbidden.")
    if tfvars:
        require(path.name.lower().endswith(".tfvars.json")
                and not path.name.lower().endswith(".auto.tfvars.json")
                and path.name.lower() != "terraform.tfvars.json",
                "Use an explicitly loaded .tfvars.json handoff, never automatic variable files.")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Client:
    def __init__(self, base, token, deadline):
        self.base, self.token, self.deadline = base.rstrip("/"), token, deadline
        self.opener = urllib.request.build_opener(NoRedirect())

    def call(self, method, path, api, body=None, etag=None):
        require(method in {"GET", "PUT", "POST"} and path.startswith("/") and not path.startswith("//")
                and not any(part in path for part in ("?", "#", "\\", "%"))
                and all(part not in (".", "..") for part in path.split("/")),
                "Request is outside the bounded toolchain transport.")
        headers = {"Authorization": "Bearer " + self.token, "Accept": "application/json"}
        if etag is not None:
            headers["If-Match"] = valid_etag(etag)
        if body is not None:
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(
            self.base + path + "?api-version=" + api,
            data=None if body is None else json.dumps(body).encode(), headers=headers, method=method,
        )
        try:
            response = self.opener.open(request, timeout=remaining(self.deadline))
        except urllib.error.HTTPError as error:
            with error:
                # Only the precise ToolServer-not-found response authorizes creation.
                data = error.read(MAX_BYTES + 1) if error.code == 404 else b""
                require(len(data) <= MAX_BYTES, "HTTP error response exceeds the bounded size.")
                try:
                    document = json.loads(data) if data else None
                except ValueError:
                    document = None
                return error.code, document, None
        except (urllib.error.URLError, TimeoutError):
            return 0, None, None
        with response:
            data = response.read(MAX_BYTES + 1)
            require(len(data) <= MAX_BYTES, "HTTP response exceeds the bounded size; contents withheld.")
            # A ToolServer PUT can echo submitted secrets; never project its body.
            document = None if method == "PUT" or not data else json.loads(data)
            return response.status, document, response.headers.get("ETag")


def azure_json(arguments, deadline, credential_env):
    executable = shutil.which("az")
    require(executable is not None, "Azure CLI is required; no login or installation is automatic.")
    environment = dict(os.environ)
    if credential_env:
        environment.pop(credential_env, None)
    result = subprocess.run(
        [executable, *arguments, "--only-show-errors", "-o", "json"],
        capture_output=True, text=True, check=False, timeout=remaining(deadline, 60), env=environment,
    )
    require(result.returncode == 0, "Azure CLI context/authentication failed; details withheld.")
    document = json.loads(result.stdout)
    require(isinstance(document, dict), "Azure CLI returned an invalid context; details withheld.")
    return document


def azure_token(resource, args, deadline):
    token = azure_json(
        ["account", "get-access-token", "--resource", resource, "--subscription", args.subscription_id],
        deadline, args.credential_env,
    )
    require(str(token.get("subscription", "")).lower() == args.subscription_id.lower()
            and str(token.get("tenant", "")).lower() == args.tenant_id.lower()
            and token.get("tokenType") == "Bearer"
            and isinstance(token.get("accessToken"), str) and token["accessToken"]
            and not re.search(r"\s|[\x00-\x1f\x7f]", token["accessToken"]),
            "Token context does not match the explicit subscription and tenant.")
    return token["accessToken"]


def valid_etag(value):
    require(isinstance(value, str) and re.fullmatch(r'(?:W/)?"[!#-\x7e]{1,256}"', value) is not None,
            "A specific usable ETag is required; missing or wildcard concurrency guards are forbidden.")
    return value


def server_readback(document, header_etag, bootstrap, config):
    require(isinstance(document, dict) and isinstance(document.get("id"), str)
            and document["id"].lower() == (bootstrap["workspace_id"] + "/toolServers/github").lower()
            and isinstance(document.get("properties"), dict), "ToolServer readback identity is invalid.")
    body_etag = document.get("etag")
    require(not body_etag or not header_etag or body_etag == header_etag, "Conflicting ToolServer ETags.")
    etag = valid_etag(body_etag or header_etag)
    actual = copy.deepcopy(document["properties"])
    state = actual.pop("provisioningState", None)
    actual.pop("state", None)
    returned_endpoint = actual.pop("mcpEndpointUrl", None)
    require(state not in ("Failed", "Canceled", "Cancelled", "Deleting"), "ToolServer provisioning failed.")
    endpoints = actual.get("endpoints")
    require(isinstance(endpoints, list) and len(endpoints) == 1 and isinstance(endpoints[0], dict),
            "ToolServer endpoint ownership changed.")
    endpoints[0].pop("id", None)
    credentials = endpoints[0].get("credentials")
    require(isinstance(credentials, dict) and credentials.get("headers") in (None, {}),
            "Ordinary ToolServer GET exposed header values; no handoff or further mutation.")
    credentials.pop("headers", None)
    expected = server_body(config)["properties"]
    expected["endpoints"][0]["credentials"].pop("headers")
    require(actual == expected, "ToolServer policy, endpoint or ownership drift; no overwrite.")
    if state not in (None, "Succeeded") or not returned_endpoint:
        return None
    return {"etag": etag, "endpoint": mcp_endpoint(returned_endpoint, bootstrap)}


def wait_server(client, bootstrap, config, deadline):
    for attempt in range(30):
        status, document, etag = client.call("GET", bootstrap["workspace_id"] + "/toolServers/github", API)
        remaining(deadline)
        if status == 200:
            result = server_readback(document, etag, bootstrap, config)
            if result is not None:
                return result
        else:
            require(status in (0, 404, 408, 429, 500, 502, 503, 504),
                    "ToolServer GET failed; no retry for authorization or redirect errors.")
        if attempt < 29:
            time.sleep(remaining(deadline, 2))
    raise ToolchainError("ToolServer readiness limit reached. Preserve the receipt and use inspect-toolserver.")


def get_server(client, bootstrap, config):
    status, document, etag = client.call("GET", bootstrap["workspace_id"] + "/toolServers/github", API)
    require(status == 200, "ToolServer GET failed; no mutation.")
    result = server_readback(document, etag, bootstrap, config)
    require(result is not None, "ToolServer is not ready; no mutation.")
    return result


def mark_mutation(stream, record, secrets):
    record["mutation_attempted"] = True
    record_status(stream, record, "pending", secrets)


def configure_server(args, bootstrap, record, previous, client, credential, stream, secrets, deadline):
    identifier = bootstrap["workspace_id"] + "/toolServers/github"
    if args.operation == "create-toolserver":
        status, document, _ = client.call("GET", identifier, API)
        error = document.get("error", document) if isinstance(document, dict) else None
        require(status == 404 and isinstance(error, dict)
                and error.get("code") == "ResourceNotFound" and error.get("message") == "ToolServer not found.",
                "Creation requires the exact missing-ToolServer response; existing resources are never adopted.")
        etag = None
    else:
        current = get_server(client, bootstrap, record["configuration"])
        if args.operation == "inspect-toolserver":
            record["toolserver"] = current
            return
        require(previous["status"] == "configured" and current == previous.get("toolserver"),
                "The ToolServer changed since the receipt. Inspect it before explicitly retrying rotation.")
        etag = current["etag"]
    mark_mutation(stream, record, secrets)
    status, _, _ = client.call("PUT", identifier, API, server_body(record["configuration"], credential), etag)
    require(status in (200, 201, 202),
            "ToolServer mutation did not complete successfully. No retry; preserve the receipt and inspect.")
    record["toolserver"] = wait_server(client, bootstrap, record["configuration"], deadline)
    require(args.operation != "rotate-credential"
            or record["toolserver"]["endpoint"] == previous["toolserver"]["endpoint"],
            "The MCP endpoint changed during rotation. Inspect and review the connection handoff before proceeding.")


def toolbox_body(record):
    return {
        "description": "Read-only GitHub MCP through AI Gateway",
        "metadata": {"terraform_toolchain_owner": record["configuration"]["owner_id"],
                     "terraform_toolchain_configuration": record["configuration_hash"]},
        "tools": [{"type": "mcp", "server_label": "aigw-github", "project_connection_id": "aigw-github",
                   "require_approval": "never"}],
    }


def toolbox_name(value):
    require(isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", value) is not None,
            "Use a simple, explicit Toolbox name of at most 64 characters.")
    return value


def toolbox_metadata(bootstrap, selected_name, version):
    toolbox_name(selected_name)
    require(isinstance(version, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", version) is not None,
            "Toolbox returned an invalid version; preserve the receipt.")
    return {"name": selected_name, "version": version,
            "endpoint": bootstrap["project_endpoint"].rstrip("/")
            + f"/toolboxes/{selected_name}/versions/{version}/mcp?api-version=v1"}


def verify_connection(client, bootstrap, server):
    identifier = bootstrap["project_id"] + "/connections/aigw-github"
    require(bootstrap["remote_tool_connection_id"] is not None
            and bootstrap["remote_tool_endpoint"] == server["endpoint"],
            "Apply the explicit ToolServer handoff through Terraform, then export a fresh bootstrap.")
    status, document, _ = client.call("GET", identifier, CONNECTION_API)
    require(status == 200 and isinstance(document, dict)
            and str(document.get("id", "")).lower() == identifier.lower(),
            "The Terraform-owned RemoteTool connection is unavailable.")
    properties = document.get("properties", {})
    require(isinstance(properties, dict) and all(properties.get(key) == value for key, value in {
        "category": "RemoteTool", "authType": "ProjectManagedIdentity",
        "audience": AUDIENCE, "target": server["endpoint"], "isSharedToAll": True,
    }.items()) and isinstance(properties.get("metadata"), dict)
            and properties["metadata"].get("type") == "custom_MCP"
            and not properties.get("credentials"),
            "RemoteTool readback differs from the intended managed-identity connection; no Toolbox write.")


def inspect_toolbox(client, bootstrap, record, expected_version=None):
    selected_name = toolbox_name(record["toolbox"]["name"])
    status, toolbox, _ = client.call("GET", "/toolboxes/" + selected_name, "v1")
    require(status == 200 and isinstance(toolbox, dict) and toolbox.get("name") == selected_name,
            "Toolbox is unavailable or mismatched; no adoption.")
    version = toolbox.get("default_version")
    metadata = toolbox_metadata(bootstrap, selected_name, version)
    require(expected_version is None or version == expected_version, "Toolbox default version drift.")
    status, result, _ = client.call("GET", f"/toolboxes/{selected_name}/versions/{version}", "v1")
    expected = toolbox_body(record)
    require(status == 200 and isinstance(result, dict)
            and result.get("name") == selected_name and result.get("version") == version
            and all(result.get(key) == value for key, value in expected.items())
            and not result.get("skills") and not result.get("policies"),
            "Toolbox tools, owner, configuration or governance drift; no overwrite.")
    return metadata


def configure_toolbox(args, bootstrap, record, previous, arm, foundry, stream, secrets):
    current = get_server(arm, bootstrap, record["configuration"])
    require(current == previous.get("toolserver"), "ToolServer changed; inspect it before configuring Toolbox.")
    verify_connection(arm, bootstrap, current)
    record["toolserver"] = current
    if args.operation == "create-toolbox":
        selected_name = toolbox_name(record["toolbox"]["name"])
        status, _, _ = foundry.call("GET", "/toolboxes/" + selected_name, "v1")
        require(status == 404, "Toolbox already exists or could not be checked; no adoption or new version.")
        mark_mutation(stream, record, secrets)
        status, result, _ = foundry.call("POST", f"/toolboxes/{selected_name}/versions", "v1", toolbox_body(record))
        require(status in (200, 201) and isinstance(result, dict),
                "Toolbox creation is unconfirmed. Never blindly repeat the non-idempotent POST; inspect first.")
        version = result.get("version")
        require(result.get("name") == selected_name, "Toolbox returned an unexpected name; preserve the receipt.")
        record["toolbox"] = toolbox_metadata(bootstrap, selected_name, version)
        record_status(stream, record, "pending", secrets)
    else:
        version = previous["toolbox"].get("version")
    record["toolbox"] = inspect_toolbox(foundry, bootstrap, record, version)


class SafeParser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, "Invalid toolchain arguments; values withheld. Use --help.\n")


def arguments(argv):
    parser = SafeParser(description=__doc__)
    parser.add_argument("operation", choices=sorted(SERVER_ACTIONS | BOX_ACTIONS))
    parser.add_argument("--bootstrap", required=True, type=pathlib.Path)
    parser.add_argument("--subscription-id", required=True)
    parser.add_argument("--tenant-id", required=True)
    parser.add_argument("--receipt", required=True, type=pathlib.Path)
    parser.add_argument("--previous-receipt", type=pathlib.Path)
    parser.add_argument("--repository")
    parser.add_argument("--allow-client-cidr", action="append", default=[])
    parser.add_argument("--credential-env")
    parser.add_argument("--confirm-read-only-credential", action="store_true")
    parser.add_argument("--confirm-exclusive-owner", action="store_true")
    parser.add_argument("--toolbox-name")
    parser.add_argument("--tfvars", type=pathlib.Path)
    parser.add_argument("--environment-json", type=pathlib.Path)
    parser.add_argument("--timeout-seconds", type=int, default=300, choices=range(1, 601), metavar="1-600")
    return parser.parse_args(argv)


def prepare(args):
    require(re.fullmatch(UUID, args.tenant_id) is not None, "An explicit tenant UUID is required.")
    bootstrap = validate_bootstrap(json.loads(read_text(args.bootstrap)), args.subscription_id)
    require(args.operation not in WRITE_ACTIONS or
            (args.confirm_exclusive_owner and bootstrap["tool_access_enabled"]),
            "Writes require enabled project tool access and explicit exclusive-owner confirmation.")
    needs_credential = args.operation in {"create-toolserver", "rotate-credential"}
    require((args.credential_env is not None) == needs_credential
            and args.confirm_read_only_credential == needs_credential,
            "Only create/rotation accepts an explicitly selected, confirmed repository-restricted read-only credential.")
    if needs_credential:
        require(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", args.credential_env) is not None,
                "Select the credential by environment-variable name, never a command-line value.")
    require((args.environment_json is None or args.operation in BOX_ACTIONS)
            and (args.tfvars is None or args.operation in SERVER_ACTIONS),
            "Use the handoff type appropriate to this operation.")
    require(args.operation not in BOX_ACTIONS or bootstrap["remote_tool_connection_id"] is not None,
            "Apply the ToolServer handoff through Terraform and export a fresh bootstrap before Toolbox setup.")
    inputs = [args.bootstrap, args.previous_receipt]
    outputs = [path for path in (args.receipt, args.tfvars, args.environment_json) if path is not None]
    require(len({path.resolve() for path in outputs}) == len(outputs), "Output paths must be distinct.")
    for path in outputs:
        new_output(path, inputs, tfvars=path == args.tfvars)
    previous = None
    if args.operation == "create-toolserver":
        require(args.previous_receipt is None and args.toolbox_name is None,
                "Creation does not adopt an existing receipt or Toolbox.")
        config = configuration(args.repository, args.allow_client_cidr)
    else:
        require(args.previous_receipt is not None and args.repository is None and not args.allow_client_cidr,
                "Use the previous ownership receipt; configuration changes are not credential rotation.")
        previous = read_receipt(args.previous_receipt, bootstrap, args.tenant_id)
        config = previous["configuration"]
        if args.operation in {"rotate-credential", "create-toolbox"}:
            require(previous["status"] == "configured", "Inspect an unconfirmed operation before any further mutation.")
    record = {
        "version": 1, "operation": args.operation, "status": "prepared",
        "binding": binding(bootstrap, args.tenant_id), "configuration": config,
        "configuration_hash": config_hash(config), "mutation_attempted": False,
    }
    if previous and "toolserver" in previous:
        record["toolserver"] = previous["toolserver"]
    if previous and "toolbox" in previous:
        record["toolbox"] = previous["toolbox"]
    if args.operation == "create-toolbox":
        record["toolbox"] = {"name": toolbox_name(args.toolbox_name)}
    elif args.operation == "inspect-toolbox":
        require(args.toolbox_name is None and "toolbox" in previous, "Inspect Toolbox using its own creation receipt.")
        record["toolbox"] = previous["toolbox"]
    else:
        require(args.toolbox_name is None, "Toolbox naming is only accepted on create-toolbox.")
    return bootstrap, record, previous


def main(argv=None):
    args = arguments(argv)
    secrets = []
    try:
        bootstrap, record, previous = prepare(args)
        deadline = time.monotonic() + args.timeout_seconds
        credential = None
        if args.credential_env:
            credential = os.environ.get(args.credential_env, "")
            require(re.fullmatch(r"[A-Za-z0-9._~-]{8,4096}", credential) is not None,
                    "Selected credential is missing or malformed; no credential lookup is automatic.")
            secrets.append(credential)
        with args.receipt.open("x", encoding="utf-8", newline="\n") as stream:
            try:
                record_status(stream, record, "prepared", secrets)
                account = azure_json(["account", "show"], deadline, args.credential_env)
                require(str(account.get("id", "")).lower() == args.subscription_id.lower()
                        and str(account.get("tenantId", "")).lower() == args.tenant_id.lower()
                        and account.get("environmentName") == "AzureCloud",
                        "Azure CLI must already match the explicit subscription, tenant and public cloud.")
                token = azure_token(ARM + "/", args, deadline)
                secrets.append(token)
                arm = Client(ARM, token, deadline)
                if args.operation in SERVER_ACTIONS:
                    configure_server(args, bootstrap, record, previous, arm, credential, stream, secrets, deadline)
                else:
                    token = azure_token("https://ai.azure.com", args, deadline)
                    secrets.append(token)
                    foundry = Client(bootstrap["project_endpoint"], token, deadline)
                    configure_toolbox(args, bootstrap, record, previous, arm, foundry, stream, secrets)
                remaining(deadline)
                record_status(stream, record, "configured", secrets)
                if args.tfvars:
                    with args.tfvars.open("x", encoding="utf-8") as destination:
                        destination.write(safe_json({"gateway_remote_tool_endpoint": record["toolserver"]["endpoint"]}, secrets) + "\n")
                if args.environment_json:
                    environment = {"TOOLBOX_NAME": record["toolbox"]["name"],
                                   "TOOLBOX_ENDPOINT": record["toolbox"]["endpoint"],
                                   "GITHUB_REPOSITORY": record["configuration"]["repository"]}
                    with args.environment_json.open("x", encoding="utf-8") as destination:
                        destination.write(safe_json(environment, secrets) + "\n")
            except BaseException:
                try:
                    record_status(stream, record, "unconfirmed", secrets)
                except (OSError, ValueError):
                    pass
                raise
        print("CONFIGURED: nonsecret receipt and requested handoffs written. Runtime acceptance remains separate.")
        return 0
    except ToolchainError as error:
        print(str(error), file=sys.stderr)
    except (OSError, ValueError, KeyError, TypeError, AttributeError, subprocess.TimeoutExpired, KeyboardInterrupt):
        print("Toolchain operation failed; sensitive details withheld. Preserve the receipt and inspect before retrying.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
