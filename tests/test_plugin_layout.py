"""Plugin layout regression test.

Defends the structural invariant that this repo loads as a Claude Code plugin
via `.claude-plugin/`, not via a root-level `.mcp.json`. A regression here
would dedup-collide the project-scope and plugin-scope MCP reads, the plugin
registration would be skipped, and the plugin-prefixed tool surface every
agent, hook, and skill in this repo expects would silently disappear.

See `.claude/CLAUDE.md` §Migration-Era Cautions for the symptoms and rationale.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_root_mcp_json_must_not_exist() -> None:
    p = REPO_ROOT / ".mcp.json"
    assert not p.exists() and not p.is_symlink(), (
        "root .mcp.json must not exist; use .claude-plugin/mcp-config.json. "
        f"Got: exists={p.exists()}, is_symlink={p.is_symlink()}"
    )


def test_plugin_json_points_at_mcp_config() -> None:
    plugin = json.loads(
        (REPO_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    expected = "./.claude-plugin/mcp-config.json"
    actual = plugin.get("mcpServers")
    assert actual == expected, (
        f"plugin.json mcpServers must be {expected!r}. Got: {actual!r}"
    )


def test_mcp_config_defines_codex_collaboration_server() -> None:
    config = json.loads(
        (REPO_ROOT / ".claude-plugin" / "mcp-config.json").read_text(encoding="utf-8")
    )
    servers = config.get("mcpServers")
    assert isinstance(servers, dict), (
        f"mcp-config.json must define mcpServers as object. "
        f"Got: {type(servers).__name__}"
    )
    assert "codex-collaboration" in servers, (
        "mcp-config.json must define mcpServers.codex-collaboration. "
        f"Got keys: {sorted(servers.keys())}"
    )


def test_ci_validation_targets_match_layout() -> None:
    ci_text = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert ".claude-plugin/plugin.json" in ci_text, (
        "CI must validate .claude-plugin/plugin.json"
    )
    assert ".claude-plugin/mcp-config.json" in ci_text, (
        "CI must validate .claude-plugin/mcp-config.json"
    )
    assert ".claude-plugin/marketplace.json" in ci_text, (
        "CI must validate .claude-plugin/marketplace.json"
    )
    assert "hooks/hooks.json" in ci_text, "CI must validate hooks/hooks.json"
    assert "json.tool .mcp.json" not in ci_text, (
        "CI must not validate root .mcp.json as JSON — it should not exist. "
        "If you see this failure, the CI step is referencing the deleted file."
    )


def test_scripts_check_validation_targets_match_layout() -> None:
    check_text = (REPO_ROOT / "scripts" / "check").read_text(encoding="utf-8")
    assert ".claude-plugin/plugin.json" in check_text, (
        "scripts/check must validate .claude-plugin/plugin.json"
    )
    assert ".claude-plugin/mcp-config.json" in check_text, (
        "scripts/check must validate .claude-plugin/mcp-config.json"
    )
    assert ".claude-plugin/marketplace.json" in check_text, (
        "scripts/check must validate .claude-plugin/marketplace.json"
    )
    assert "json.tool .mcp.json" not in check_text, (
        "scripts/check must not validate root .mcp.json as JSON — it should not exist."
    )
