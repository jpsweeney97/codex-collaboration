---
id: T-20260516-02
title: Decide Codex App Server contract-version assertion
status: open
created: 2026-05-16
---

# Decide Codex App Server contract-version assertion

## Current state

The JSON-RPC `"2.0"` field is the JSON-RPC protocol version, not a Codex App Server contract version. Payload-shape tests now cover the vendored schema boundary, but runtime negotiation still has no explicit contract-version assertion.

## Relationship to QW4 (stopgap)

QW4 (the Task 5 startup compatibility preflight) is an explicit **stopgap on this roadmap line, not a substitute for ST3**. QW4 converts a silent mid-session version mismatch into a clean startup failure; it does **not** protect against silent wire-format drift within a "compatible" version. Only HL1 (payload-shape contract tests) plus this ST3 contract-version decision close that gap. Risk the audit calls out explicitly: QW4 feels like "done" and ST3 never gets scheduled — this ticket exists so it does.

## Exit condition

Land a design that either adds a clear contract-version assertion point at startup or records why vendored schema plus live method probing is the v1 compatibility boundary.
