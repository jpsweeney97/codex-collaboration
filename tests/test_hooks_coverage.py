"""Architectural coverage: hooks/hooks.json must dispatch every content-bearing
MCP tool to codex_guard.py.

Drift class this test prevents: a new MCP tool is added with a policy entry in
``consultation_safety._TOOL_POLICY_MAP`` (so the guard script handles it
correctly when invoked), but the PreToolUse matcher in ``hooks/hooks.json`` is
not extended, leaving the credential-scan chain unreachable at the outer
boundary for that tool.

"Content-bearing" here means the policy has a non-empty ``content_fields``
set — i.e., the tool accepts user-authored prose (objective, answers, profile)
that could carry a credential.

Non-content-bearing tools (delegate.poll/promote/discard, codex.status) are
NOT required to be in the matcher by this test. The guard script handles
unknown-field-with-secret cases for those tools (see
test_codex_guard.TestDelegatePromoteDiscardGuard), but invoking the guard for
every plugin tool is a broader policy decision out of scope for this test.
"""

from __future__ import annotations

import json
from pathlib import Path

from server.consultation_safety import _TOOL_POLICY_MAP

_HOOKS_JSON_PATH = (
    Path(__file__).resolve().parent.parent / "hooks" / "hooks.json"
)
_GUARD_SCRIPT_NAME = "codex_guard.py"


def _guard_matcher_source() -> str:
    """Return the PreToolUse matcher string that dispatches to codex_guard.py."""
    payload = json.loads(_HOOKS_JSON_PATH.read_text(encoding="utf-8"))
    pretooluse = payload["hooks"]["PreToolUse"]
    for entry in pretooluse:
        commands = (hook.get("command", "") for hook in entry.get("hooks", []))
        if any(_GUARD_SCRIPT_NAME in command for command in commands):
            return entry["matcher"]
    raise AssertionError(
        f"hooks.json has no PreToolUse entry invoking {_GUARD_SCRIPT_NAME!r}"
    )


def _matcher_tool_names() -> set[str]:
    """Decode the alternation matcher into a set of plain tool names.

    The matcher is a regex with `\\.` escapes around dots and `|` between
    alternatives. The current format does not use grouping, character classes,
    or quantifiers, so a simple split + unescape is sufficient.
    """
    return {branch.replace("\\.", ".") for branch in _guard_matcher_source().split("|")}


def _content_bearing_tools() -> set[str]:
    return {
        tool_name
        for tool_name, policy in _TOOL_POLICY_MAP.items()
        if policy.content_fields
    }


def test_policy_map_keys_share_one_mcp_prefix() -> None:
    from server.tool_prefix import TOOL_PREFIX

    unexpected = sorted(
        tool_name
        for tool_name in _TOOL_POLICY_MAP
        if not tool_name.startswith(TOOL_PREFIX)
    )
    assert unexpected == []


def test_hooks_matcher_covers_every_content_bearing_mcp_tool() -> None:
    """Every tool with non-empty content_fields must invoke codex_guard.

    Source of truth: ``consultation_safety._TOOL_POLICY_MAP``. If a future
    tool adds ``content_fields`` to its policy, it must also be added to the
    hook matcher — otherwise the outer credential boundary is materially
    advisory-only for that tool.
    """
    matched = _matcher_tool_names()
    missing = sorted(_content_bearing_tools() - matched)
    assert not missing, (
        "hooks/hooks.json matcher omits content-bearing tools: "
        f"{missing}. Update the PreToolUse matcher to include every tool "
        "whose policy has non-empty content_fields."
    )


def test_hooks_matcher_references_only_known_mcp_tools() -> None:
    """Drift in the other direction: matcher must not name unknown tools.

    An unknown tool name in the matcher would invoke the guard, which then
    fails closed via ``policy_for_tool`` raising ``KeyError`` — safe at
    runtime but a sign the matcher and policy map are out of sync.
    """
    matched = _matcher_tool_names()
    unknown = sorted(matched - set(_TOOL_POLICY_MAP.keys()))
    assert not unknown, (
        "hooks/hooks.json matcher references tool names with no policy: "
        f"{unknown}. Either add policies to _TOOL_POLICY_MAP or remove "
        "from the matcher."
    )
