"""Subprocess-backed tests for JsonRpcClient transport behavior."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from server.jsonrpc_client import JsonRpcClient


def _write_echo_server(tmp_path: Path, *, mode: str = "echo") -> Path:
    script = tmp_path / "echo_jsonrpc.py"
    script.write_text(
        f"""
import json
import sys

mode = {mode!r}
if mode == "malformed-first":
    print("not json", flush=True)
elif mode == "notify-first":
    print(json.dumps({{"jsonrpc": "2.0", "method": "note", "params": {{"value": 1}}}}), flush=True)

for line in sys.stdin:
    message = json.loads(line)
    if message.get("method") == "mismatch":
        print(json.dumps({{"jsonrpc": "2.0", "id": 999, "result": {{}}}}), flush=True)
        continue
    print(json.dumps({{"jsonrpc": "2.0", "id": message["id"], "result": {{"method": message["method"], "params": message.get("params", {{}})}}}}), flush=True)
    sys.stdout.flush()
""".lstrip(),
        encoding="utf-8",
    )
    return script


def test_request_round_trip(tmp_path: Path) -> None:
    script = _write_echo_server(tmp_path)
    client = JsonRpcClient([sys.executable, str(script)], request_timeout=2.0)
    try:
        result = client.request("ping", {"x": 1})
    finally:
        client.close()
    assert result == {"method": "ping", "params": {"x": 1}}


def test_request_buffers_notification_before_response(tmp_path: Path) -> None:
    script = _write_echo_server(tmp_path, mode="notify-first")
    client = JsonRpcClient([sys.executable, str(script)], request_timeout=2.0)
    try:
        result = client.request("ping", {})
        notification = client.next_notification(timeout=0.1)
    finally:
        client.close()
    assert result == {"method": "ping", "params": {}}
    assert notification["method"] == "note"


def test_malformed_stdout_line_is_dropped(tmp_path: Path) -> None:
    script = _write_echo_server(tmp_path, mode="malformed-first")
    client = JsonRpcClient([sys.executable, str(script)], request_timeout=2.0)
    try:
        result = client.request("ping", {})
    finally:
        client.close()
    assert result["method"] == "ping"


def test_unexpected_response_id_raises(tmp_path: Path) -> None:
    script = _write_echo_server(tmp_path)
    client = JsonRpcClient([sys.executable, str(script)], request_timeout=2.0)
    try:
        with pytest.raises(RuntimeError, match="unexpected response id"):
            client.request("mismatch", {})
    finally:
        client.close()
