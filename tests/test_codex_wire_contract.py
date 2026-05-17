"""Payload-shape contract tests against vendored Codex App Server schemas."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from jsonschema.validators import validator_for

from server.delegation_controller import DelegationController
from server.models import PendingServerRequest
from server.runtime import (
    AppServerRuntimeSession,
    _build_read_only_sandbox_policy,
    build_workspace_write_sandbox_policy,
)


_REQUIRED_SCHEMAS = (
    "ClientRequest.json",
    "CommandExecutionRequestApprovalResponse.json",
    "FileChangeRequestApprovalResponse.json",
    "ToolRequestUserInputResponse.json",
)


def _validator_for(schema: dict[str, Any]):
    """Build the jsonschema validator the fixture's own ``$schema`` declares."""

    cls = validator_for(schema)
    cls.check_schema(schema)
    return cls(schema)


def _assert_valid(schema: dict[str, Any], payload: dict[str, Any]) -> None:
    errors = sorted(
        _validator_for(schema).iter_errors(payload),
        key=lambda err: list(err.path),
    )
    assert errors == [], f"payload invalid: {errors}"


class CapturingClient:
    def __init__(self) -> None:
        self.requests: list[tuple[str, dict[str, Any]]] = []
        self.responses: list[tuple[str | int, dict[str, Any]]] = []
        self.notifications: list[dict[str, Any]] = []

    def request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        self.requests.append((method, params))
        if method == "initialize":
            return {
                "codexHome": "/tmp/codex",
                "platformFamily": "unix",
                "platformOs": "macos",
                "userAgent": "codex-cli 0.117.0",
            }
        if method == "account/read":
            return {"account": {"type": "openai"}, "requiresOpenaiAuth": False}
        if method in {"thread/start", "thread/fork", "thread/resume"}:
            return {"thread": {"id": "thread-1"}}
        if method == "thread/read":
            return {"thread": {"turns": []}}
        if method == "turn/start":
            self.notifications.append(
                {
                    "method": "turn/completed",
                    "params": {
                        "turnId": "turn-1",
                        "turn": {"id": "turn-1", "status": "completed"},
                    },
                }
            )
            return {"turn": {"id": "turn-1"}}
        if method == "turn/interrupt":
            return {}
        raise AssertionError(f"unexpected method {method!r}")

    def next_notification(self, timeout: float | None = None) -> dict[str, Any]:
        assert self.notifications, (
            "CapturingClient notification queue drained: _run_turn requested "
            "more notifications than the stub queued. The turn loop contract "
            "changed - queue the notifications the new flow expects."
        )
        return self.notifications.pop(0)

    def respond(self, request_id: str | int, result: dict[str, Any]) -> None:
        self.responses.append((request_id, result))

    def close(self) -> None:
        return None


def _session_with_client(
    tmp_path: Path, client: CapturingClient
) -> AppServerRuntimeSession:
    session = object.__new__(AppServerRuntimeSession)
    session._repo_root = tmp_path  # type: ignore[attr-defined]
    session._client = client  # type: ignore[attr-defined]
    return session


def _pending_request(kind: str) -> PendingServerRequest:
    return PendingServerRequest(
        request_id=f"req-{kind}",
        runtime_id="runtime-1",
        collaboration_id="collab-1",
        codex_thread_id="thread-1",
        codex_turn_id="turn-1",
        item_id="item-1",
        kind=cast(Any, kind),
        requested_scope={},
    )


def _controller_response_payload(
    *,
    decision: str,
    kind: str,
    answers: dict[str, tuple[str, ...]] | None = None,
) -> dict[str, Any]:
    controller = object.__new__(DelegationController)
    return controller._build_response_payload(
        decision=decision,
        answers=answers,
        request=_pending_request(kind),
    )


def test_contract_fixtures_present() -> None:
    """A missing fixture dir or file must fail here, never skip the gate."""

    from server.codex_compat import TESTED_CODEX_VERSION

    fixtures_dir = (
        Path(__file__).parent
        / "fixtures"
        / "codex-app-server"
        / TESTED_CODEX_VERSION
    )
    assert fixtures_dir.is_dir(), (
        f"vendored schema dir missing for TESTED_CODEX_VERSION="
        f"{TESTED_CODEX_VERSION!r}: {fixtures_dir} - an ST2 version bump must "
        "regenerate fixtures before the contract gate can run."
    )
    missing = [
        name for name in _REQUIRED_SCHEMAS if not (fixtures_dir / name).exists()
    ]
    assert missing == [], f"required vendored schemas missing: {missing}"


def test_client_request_validator_rejects_known_bad_payload(schema_loader) -> None:
    """Negative control: prove the validator has teeth."""

    validator = _validator_for(schema_loader("ClientRequest.json"))
    bad = {"jsonrpc": 2.0, "method": 12345}
    errors = list(validator.iter_errors(bad))
    assert errors, (
        "ClientRequest schema accepted a malformed payload; "
        "the contract gate is toothless"
    )


def test_runtime_client_request_payloads_validate(
    schema_loader, tmp_path: Path
) -> None:
    client = CapturingClient()
    session = _session_with_client(tmp_path, client)

    session.initialize()
    session.read_account()
    thread_id = session.start_thread()
    session.fork_thread(thread_id)
    session.resume_thread(thread_id)
    session.read_thread(thread_id)
    session.run_advisory_turn(
        thread_id=thread_id,
        prompt_text="hello",
        output_schema={"type": "object"},
    )
    session.run_execution_turn(
        thread_id=thread_id,
        prompt_text="do work",
        sandbox_policy=_build_read_only_sandbox_policy(),
    )
    session.run_execution_turn(
        thread_id=thread_id,
        prompt_text="do work",
        sandbox_policy=build_workspace_write_sandbox_policy(tmp_path),
    )
    session.interrupt_turn(thread_id=thread_id, turn_id="turn-1")

    validator = _validator_for(schema_loader("ClientRequest.json"))
    for method, params in client.requests:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params,
        }
        errors = sorted(
            validator.iter_errors(payload), key=lambda err: list(err.path)
        )
        assert errors == [], f"{method} payload invalid: {errors}"

    turn_start_sandboxes = [
        params.get("sandboxPolicy")
        for method, params in client.requests
        if method == "turn/start"
    ]
    assert any(
        isinstance(sp, dict) and sp.get("type") == "workspaceWrite"
        for sp in turn_start_sandboxes
    ), (
        "no workspace-write turn/start payload captured: HL1 must validate "
        "the sandboxPolicy shape the real delegation path sends "
        "(build_workspace_write_sandbox_policy), not only the read-only shape"
    )


def test_command_approval_response_payloads_validate(schema_loader) -> None:
    schema = schema_loader("CommandExecutionRequestApprovalResponse.json")
    approved = _controller_response_payload(
        decision="approve",
        kind="command_approval",
    )
    denied = _controller_response_payload(
        decision="deny",
        kind="command_approval",
    )

    assert approved == {"decision": "accept"}
    assert denied == {"decision": "decline"}
    _assert_valid(schema, approved)
    _assert_valid(schema, denied)


def test_file_change_response_payloads_validate(schema_loader) -> None:
    schema = schema_loader("FileChangeRequestApprovalResponse.json")
    approved = _controller_response_payload(
        decision="approve",
        kind="file_change",
    )
    denied = _controller_response_payload(
        decision="deny",
        kind="file_change",
    )

    assert approved == {"decision": "accept"}
    assert denied == {"decision": "decline"}
    _assert_valid(schema, approved)
    _assert_valid(schema, denied)


def test_user_input_response_payloads_validate(schema_loader) -> None:
    schema = schema_loader("ToolRequestUserInputResponse.json")
    approved = _controller_response_payload(
        decision="approve",
        kind="request_user_input",
        answers={"question-1": ("yes",)},
    )
    denied = _controller_response_payload(
        decision="deny",
        kind="request_user_input",
    )

    assert approved == {"answers": {"question-1": {"answers": ["yes"]}}}
    assert denied == {"answers": {}}
    _assert_valid(schema, approved)
    _assert_valid(schema, denied)
