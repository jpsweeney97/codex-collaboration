#!/usr/bin/env python3
"""SessionStart hook: publish the host session identity for MCP server use.

Reads the Claude Code session_id from the hook's stdin JSON payload and
writes it to ${CLAUDE_PLUGIN_DATA}/session_id. The codex-collaboration MCP
server reads this file on first dialogue tool call to initialize
session-scoped stores (LineageStore, TurnStore, OperationJournal).

Contract:
- Called once per Claude Code session via the SessionStart hook.
- Overwrites any stale session_id from a previous session.
- The MCP server treats the published identity as pinned: it reads the file
  once, caches the value, and refuses mid-process identity changes.
"""

from __future__ import annotations

import json
import os
import sys
import time

_RECENT_SESSION_WINDOW_SECONDS = 60.0


def main() -> None:
    plugin_data = os.environ.get("CLAUDE_PLUGIN_DATA")
    if not plugin_data:
        return

    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return

    session_id = payload.get("session_id")
    if not isinstance(session_id, str) or not session_id:
        return

    target = os.path.join(plugin_data, "session_id")
    tmp = target + ".tmp"
    if os.path.exists(target):
        try:
            existing_session_id = open(target, encoding="utf-8").read().strip()
            age_seconds = time.time() - os.path.getmtime(target)
        except OSError:
            existing_session_id = ""
            age_seconds = _RECENT_SESSION_WINDOW_SECONDS + 1.0
        if (
            existing_session_id
            and existing_session_id != session_id
            and age_seconds <= _RECENT_SESSION_WINDOW_SECONDS
        ):
            print(
                "codex-collaboration: concurrent session warning: "
                "recent different session_id exists; single-session use only",
                file=sys.stderr,
            )
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(session_id)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, target)


if __name__ == "__main__":
    main()
