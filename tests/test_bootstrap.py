"""Tests for plugin bootstrap wiring and session identity publication."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

# Bootstrap script is not a package module — import its functions directly.
_bootstrap_path = (
    Path(__file__).resolve().parent.parent / "scripts" / "codex_runtime_bootstrap.py"
)
_hook_path = (
    Path(__file__).resolve().parent.parent / "scripts" / "publish_session_id.py"
)
_hooks_config_path = Path(__file__).resolve().parent.parent / "hooks" / "hooks.json"
_regenerate_schema_path = (
    Path(__file__).resolve().parent.parent / "scripts" / "regenerate_schema.sh"
)


def _import_bootstrap():
    """Import bootstrap module from scripts/ path."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "codex_runtime_bootstrap", _bootstrap_path
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _patch_bootstrap_run(
    monkeypatch: pytest.MonkeyPatch,
    mod: object,
    tmp_path: Path,
) -> list[object]:
    runs: list[object] = []
    monkeypatch.setattr(mod, "default_plugin_data_path", lambda: tmp_path)

    def fake_run(self: object) -> None:
        runs.append(self)

    monkeypatch.setattr(mod.McpServer, "run", fake_run)
    return runs


class TestReadSessionId:
    """Tests for _read_session_id from the bootstrap script."""

    def test_reads_published_session_id(self, tmp_path: Path) -> None:
        (tmp_path / "session_id").write_text("sess-abc-123", encoding="utf-8")
        mod = _import_bootstrap()
        assert mod._read_session_id(tmp_path) == "sess-abc-123"

    def test_strips_whitespace(self, tmp_path: Path) -> None:
        (tmp_path / "session_id").write_text("  sess-abc  \n", encoding="utf-8")
        mod = _import_bootstrap()
        assert mod._read_session_id(tmp_path) == "sess-abc"

    def test_raises_when_file_missing(self, tmp_path: Path) -> None:
        mod = _import_bootstrap()
        with pytest.raises(RuntimeError, match="session identity not yet available"):
            mod._read_session_id(tmp_path)

    def test_raises_when_file_empty(self, tmp_path: Path) -> None:
        (tmp_path / "session_id").write_text("", encoding="utf-8")
        mod = _import_bootstrap()
        with pytest.raises(RuntimeError, match="session identity file is empty"):
            mod._read_session_id(tmp_path)


class TestBuildDialogueFactory:
    """Tests for _build_dialogue_factory from the bootstrap script."""

    def test_factory_returns_dialogue_controller(self, tmp_path: Path) -> None:
        (tmp_path / "session_id").write_text("sess-test", encoding="utf-8")
        mod = _import_bootstrap()

        from server.control_plane import ControlPlane
        from server.journal import OperationJournal

        journal = OperationJournal(tmp_path)
        # Use a minimal control plane with a no-op compat checker
        control_plane = ControlPlane(
            plugin_data_path=tmp_path,
            journal=journal,
            compat_checker=lambda: type(
                "R",
                (),
                {
                    "codex_version": None,
                    "passed": False,
                    "errors": (),
                    "available_methods": frozenset(),
                },
            )(),
        )

        factory = mod._build_dialogue_factory(
            plugin_data_path=tmp_path,
            control_plane=control_plane,
            journal=journal,
        )
        controller = factory()

        from server.dialogue import DialogueController

        assert isinstance(controller, DialogueController)

    def test_factory_raises_when_session_id_missing(self, tmp_path: Path) -> None:
        mod = _import_bootstrap()

        from server.control_plane import ControlPlane
        from server.journal import OperationJournal

        journal = OperationJournal(tmp_path)
        control_plane = ControlPlane(
            plugin_data_path=tmp_path,
            journal=journal,
            compat_checker=lambda: type(
                "R",
                (),
                {
                    "codex_version": None,
                    "passed": False,
                    "errors": (),
                    "available_methods": frozenset(),
                },
            )(),
        )

        factory = mod._build_dialogue_factory(
            plugin_data_path=tmp_path,
            control_plane=control_plane,
            journal=journal,
        )
        with pytest.raises(RuntimeError, match="session identity not yet available"):
            factory()


class TestBootstrapRetentionPrune:
    def test_bootstrap_logs_info_summary_when_prune_succeeds_with_zero_malformed(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        mod = _import_bootstrap()
        runs = _patch_bootstrap_run(monkeypatch, mod, tmp_path)

        with caplog.at_level("INFO"):
            mod.main()

        assert len(runs) == 1
        assert "audit prune complete:" in caplog.text
        assert "audit_quarantined_to=None" in caplog.text
        assert "outcomes_quarantined_to=None" in caplog.text

    def test_bootstrap_warns_summary_when_prune_succeeds_with_nonzero_audit_malformed(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        mod = _import_bootstrap()
        _patch_bootstrap_run(monkeypatch, mod, tmp_path)
        audit_path = tmp_path / "audit" / "events.jsonl"
        audit_path.parent.mkdir(parents=True)
        audit_path.write_text('{"timestamp": "not-a-date"}\n', encoding="utf-8")

        with caplog.at_level("WARNING"):
            mod.main()

        assert "audit_retained_malformed=1" in caplog.text

    def test_bootstrap_warns_summary_when_prune_succeeds_with_nonzero_outcomes_malformed(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        mod = _import_bootstrap()
        _patch_bootstrap_run(monkeypatch, mod, tmp_path)
        outcomes_path = tmp_path / "analytics" / "outcomes.jsonl"
        outcomes_path.parent.mkdir(parents=True)
        outcomes_path.write_text('{"timestamp": "not-a-date"}\n', encoding="utf-8")

        with caplog.at_level("WARNING"):
            mod.main()

        assert "outcomes_retained_malformed=1" in caplog.text

    def test_bootstrap_warns_when_prune_raises_oserror(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        mod = _import_bootstrap()
        runs = _patch_bootstrap_run(monkeypatch, mod, tmp_path)

        def fail_prune(self: object) -> object:
            raise OSError("prune failed")

        monkeypatch.setattr(mod.OperationJournal, "prune_audit_logs", fail_prune)

        with caplog.at_level("WARNING"):
            mod.main()

        assert len(runs) == 1
        assert "startup retention cleanup failed or incomplete; continuing" in caplog.text

    def test_bootstrap_warns_summary_when_audit_quarantined(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        mod = _import_bootstrap()
        _patch_bootstrap_run(monkeypatch, mod, tmp_path)
        audit_path = tmp_path / "audit" / "events.jsonl"
        audit_path.parent.mkdir(parents=True)
        audit_path.write_bytes(b"\x80abc\n")

        with caplog.at_level("WARNING"):
            mod.main()

        assert "audit_quarantined_to=" in caplog.text
        assert "events.corrupt-" in caplog.text

    def test_bootstrap_warns_summary_when_outcomes_quarantined(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        mod = _import_bootstrap()
        _patch_bootstrap_run(monkeypatch, mod, tmp_path)
        outcomes_path = tmp_path / "analytics" / "outcomes.jsonl"
        outcomes_path.parent.mkdir(parents=True)
        outcomes_path.write_bytes(b"\x80abc\n")

        with caplog.at_level("WARNING"):
            mod.main()

        assert "outcomes_quarantined_to=" in caplog.text
        assert "outcomes.corrupt-" in caplog.text

    def test_bootstrap_does_not_swallow_unicode_decode_error_directly(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        mod = _import_bootstrap()
        _patch_bootstrap_run(monkeypatch, mod, tmp_path)

        def fail_prune(self: object) -> object:
            raise UnicodeDecodeError("utf-8", b"\x80", 0, 1, "invalid start byte")

        monkeypatch.setattr(mod.OperationJournal, "prune_audit_logs", fail_prune)

        with pytest.raises(UnicodeDecodeError):
            mod.main()

    def test_bootstrap_does_not_swallow_value_error(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        mod = _import_bootstrap()
        _patch_bootstrap_run(monkeypatch, mod, tmp_path)

        def fail_prune(self: object) -> object:
            raise ValueError("bad clock")

        monkeypatch.setattr(mod.OperationJournal, "prune_audit_logs", fail_prune)

        with pytest.raises(ValueError, match="bad clock"):
            mod.main()


class TestPublishSessionIdHook:
    """Tests for the SessionStart hook script."""

    def test_writes_session_id_to_plugin_data(self, tmp_path: Path) -> None:
        payload = json.dumps({"session_id": "sess-hook-test", "cwd": "/tmp"})
        result = subprocess.run(
            [sys.executable, str(_hook_path)],
            input=payload,
            capture_output=True,
            text=True,
            env={**os.environ, "CLAUDE_PLUGIN_DATA": str(tmp_path)},
            timeout=5,
        )
        assert result.returncode == 0
        assert (tmp_path / "session_id").read_text(encoding="utf-8") == "sess-hook-test"

    def test_overwrites_stale_session_id(self, tmp_path: Path) -> None:
        (tmp_path / "session_id").write_text("old-session", encoding="utf-8")
        payload = json.dumps({"session_id": "new-session"})
        subprocess.run(
            [sys.executable, str(_hook_path)],
            input=payload,
            capture_output=True,
            text=True,
            env={**os.environ, "CLAUDE_PLUGIN_DATA": str(tmp_path)},
            timeout=5,
        )
        assert (tmp_path / "session_id").read_text(encoding="utf-8") == "new-session"

    def test_warns_when_recent_different_session_id_exists(
        self, tmp_path: Path
    ) -> None:
        (tmp_path / "session_id").write_text("old-session", encoding="utf-8")
        payload = json.dumps({"session_id": "new-session"})
        result = subprocess.run(
            [sys.executable, str(_hook_path)],
            input=payload,
            capture_output=True,
            text=True,
            env={**os.environ, "CLAUDE_PLUGIN_DATA": str(tmp_path)},
            timeout=5,
        )
        assert result.returncode == 0
        assert "concurrent session warning" in result.stderr
        assert (tmp_path / "session_id").read_text(encoding="utf-8") == "new-session"

    def test_no_warning_when_recent_session_id_is_same(self, tmp_path: Path) -> None:
        (tmp_path / "session_id").write_text("same-session", encoding="utf-8")
        payload = json.dumps({"session_id": "same-session"})
        result = subprocess.run(
            [sys.executable, str(_hook_path)],
            input=payload,
            capture_output=True,
            text=True,
            env={**os.environ, "CLAUDE_PLUGIN_DATA": str(tmp_path)},
            timeout=5,
        )
        assert result.returncode == 0
        assert "concurrent session warning" not in result.stderr

    def test_noop_without_plugin_data_env(self) -> None:
        payload = json.dumps({"session_id": "sess-noop"})
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PLUGIN_DATA"}
        result = subprocess.run(
            [sys.executable, str(_hook_path)],
            input=payload,
            capture_output=True,
            text=True,
            env=env,
            timeout=5,
        )
        assert result.returncode == 0

    def test_noop_on_missing_session_id_in_payload(self, tmp_path: Path) -> None:
        payload = json.dumps({"cwd": "/tmp"})
        subprocess.run(
            [sys.executable, str(_hook_path)],
            input=payload,
            capture_output=True,
            text=True,
            env={**os.environ, "CLAUDE_PLUGIN_DATA": str(tmp_path)},
            timeout=5,
        )
        assert not (tmp_path / "session_id").exists()


class TestHookCommandRuntime:
    """Tests for hook command interpreter wiring."""

    def test_python_hooks_use_project_uv_runtime(self) -> None:
        config = json.loads(_hooks_config_path.read_text(encoding="utf-8"))
        commands: list[str] = []
        for event_entries in config["hooks"].values():
            for entry in event_entries:
                for hook in entry["hooks"]:
                    command = hook.get("command", "")
                    if "/scripts/" in command and command.endswith(".py\""):
                        commands.append(command)

        assert commands
        for command in commands:
            assert not command.startswith("python3 ")
            assert command.startswith('uv run --directory "${CLAUDE_PLUGIN_ROOT}" python ')

    def test_schema_regeneration_uses_project_uv_runtime(self) -> None:
        script = _regenerate_schema_path.read_text(encoding="utf-8")

        assert "PYTHON_CMD=(uv run --directory \"$PLUGIN_DIR\" python)" in script
        assert "python3 -c" not in script

    def test_noop_on_invalid_json_input(self, tmp_path: Path) -> None:
        result = subprocess.run(
            [sys.executable, str(_hook_path)],
            input="not json",
            capture_output=True,
            text=True,
            env={**os.environ, "CLAUDE_PLUGIN_DATA": str(tmp_path)},
            timeout=5,
        )
        assert result.returncode == 0
        assert not (tmp_path / "session_id").exists()


# ---------------------------------------------------------------------------
# Skill metadata boundary
# ---------------------------------------------------------------------------

_skills_root = Path(__file__).resolve().parent.parent / "skills"

# Tools that belong to the consult-only surface (T-20260330-02 scope).
# Dialogue tools are shipped by the MCP server but must NOT appear in
# skill allowed-tools — the skill layer is the user-facing boundary.
_CONSULT_SURFACE_MCP_TOOLS = frozenset(
    {
        "mcp__plugin_codex-collaboration_codex-collaboration__codex.status",
        "mcp__plugin_codex-collaboration_codex-collaboration__codex.consult",
    }
)

_DIALOGUE_MCP_TOOLS = frozenset(
    {
        "mcp__plugin_codex-collaboration_codex-collaboration__codex.dialogue.start",
        "mcp__plugin_codex-collaboration_codex-collaboration__codex.dialogue.reply",
        "mcp__plugin_codex-collaboration_codex-collaboration__codex.dialogue.read",
    }
)


def _parse_allowed_tools(skill_path: Path) -> set[str]:
    """Extract allowed-tools from a SKILL.md YAML frontmatter block."""
    text = skill_path.read_text(encoding="utf-8")
    # Frontmatter is between the first two '---' lines.
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"No YAML frontmatter in {skill_path}")
    import yaml

    meta = yaml.safe_load(parts[1])
    raw = meta.get("allowed-tools", "")
    return {t.strip() for t in raw.split(",") if t.strip()}


class TestSkillMetadataBoundary:
    """Assert that consult-surface skills only reference consult-surface tools.

    The MCP server ships dialogue tools (R2), but the T-20260330-02 skill
    layer must not expose them. These tests pin that boundary so a future
    skill edit that adds dialogue tools to allowed-tools fails explicitly.
    """

    def test_consult_skill_only_references_consult_tools(self) -> None:
        allowed = _parse_allowed_tools(_skills_root / "consult-codex" / "SKILL.md")
        mcp_tools = allowed - {"Bash"}  # Bash is a host tool, not MCP
        assert mcp_tools == _CONSULT_SURFACE_MCP_TOOLS
        assert not mcp_tools & _DIALOGUE_MCP_TOOLS

    def test_status_skill_only_references_status_tool(self) -> None:
        allowed = _parse_allowed_tools(_skills_root / "codex-status" / "SKILL.md")
        mcp_tools = allowed - {"Bash"}
        assert mcp_tools == {
            "mcp__plugin_codex-collaboration_codex-collaboration__codex.status"
        }
        assert not mcp_tools & _DIALOGUE_MCP_TOOLS

    def test_no_user_invocable_dialogue_skill_exists(self) -> None:
        """No user-invocable dialogue skill should exist in the T-20260330-02 surface.

        Agent-internal skills (user-invocable: false or absent) may reference
        dialogue tools — they are subagent behavioral contracts, not user-facing
        commands. Only user-invocable skills define the plugin's user surface.
        """
        for skill_dir in _skills_root.iterdir():
            if not skill_dir.is_dir():
                continue
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                continue
            text = skill_file.read_text(encoding="utf-8")
            parts = text.split("---", 2)
            if len(parts) < 3:
                continue
            import yaml

            meta = yaml.safe_load(parts[1])
            if not meta.get("user-invocable", False):
                continue
            # This is a user-invocable skill — it must not be dialogue-scoped
            allowed = _parse_allowed_tools(skill_file)
            assert not allowed & _DIALOGUE_MCP_TOOLS, (
                f"User-invocable skill {skill_dir.name!r} references dialogue tools: "
                f"{allowed & _DIALOGUE_MCP_TOOLS}"
            )
