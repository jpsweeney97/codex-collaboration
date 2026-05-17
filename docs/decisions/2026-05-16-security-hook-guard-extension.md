# Decision Record: Extend Fail-Closed Hook Guard To Delegation Inputs

**Date:** 2026-05-16
**Status:** Decided
**Stakes:** High
**Decision:** The PreToolUse credential guard covers content-bearing delegation inputs in addition to advisory inputs.

## 1. Decision

The credential guard applies to every Codex collaboration tool that accepts user-authored prose capable of carrying secrets:

- `codex.consult`
- `codex.dialogue.start`
- `codex.dialogue.reply`
- `codex.delegate.start`
- `codex.delegate.decide`

The guard remains fail-closed. Malformed hook payloads, malformed plugin tool input, unknown guarded plugin tools, and internal policy errors block execution.

## 2. Context

Delegation introduced execution-domain content fields: `objective` on `codex.delegate.start` and `answers` on `codex.delegate.decide`. These fields cross the same outbound trust boundary as advisory prompts. Treating them as outside the guard would create an inconsistent credential-egress model.

Commit `d4f38f7` extended the guard coverage but did not leave a durable decision record. This ADR records the boundary and the reason so future hook, policy-map, and skill-frontmatter changes can be reviewed against one source of intent.

## 3. Rationale

The plugin has a three-layer safety model: host hook guard, plugin policy traversal, and Codex runtime sandboxing. The hook layer is the earliest fail-closed boundary and should not vary by capability class when the input is user-authored prose.

Non-content-bearing delegation tools may still have scan policies for forward compatibility and fail-closed lookup behavior, but the required hook matcher coverage is the content-bearing set above.

## 4. Consequences

- Any new content-bearing Codex collaboration tool must be added to `server/consultation_safety.py`, `hooks/hooks.json`, and the hook coverage tests in the same change.
- If the MCP tool prefix changes, the shared prefix invariant test must fail until the guard and policy-map move together.
- Future security-boundary changes require an ADR in the same change set.
