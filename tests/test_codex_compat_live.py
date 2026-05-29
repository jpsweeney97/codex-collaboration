"""Integration tests for Codex compatibility — require a live codex binary.

These tests are skipped in CI environments without codex installed.
They verify the version-floor startup check against the actual installed binary.

Method-surface probing (initialize handshake + capability check) is deferred to
build step 1 when the JSON-RPC client exists. T1 relies on the version floor
plus vendored-schema contract tests to guarantee method presence.
"""

from __future__ import annotations

import shutil

import pytest

from server.codex_compat import (
    MINIMUM_CODEX_VERSION,
    OPTIONAL_METHODS,
    REQUIRED_METHODS,
    TESTED_CODEX_VERSION,
    CompatCheckResult,
    SemVer,
    check_live_runtime_compatibility,
    check_version_floor,
    get_codex_version,
    probe_live_method_surface,
)

pytestmark = [
    pytest.mark.skipif(
        shutil.which("codex") is None,
        reason="codex binary not found on PATH",
    ),
    pytest.mark.slow,
]


class TestGetCodexVersion:
    def test_returns_semver(self):
        version = get_codex_version()
        assert isinstance(version, SemVer)

    def test_version_meets_minimum(self):
        version = get_codex_version()
        minimum = SemVer.parse(MINIMUM_CODEX_VERSION)
        assert version >= minimum, (
            f"Installed codex {version} is below minimum {minimum}"
        )

    def test_installed_matches_tested_baseline(self):
        """Installed binary must equal the tested baseline, or fixtures are stale.

        The module-level ``skipif`` guard skips this when no codex binary is
        present, so repo-only CI is unaffected. When a binary IS present and its
        version differs from ``TESTED_CODEX_VERSION``, the vendored fixtures under
        ``tests/fixtures/codex-app-server/<TESTED_CODEX_VERSION>/`` no longer match
        the installed Codex — yet the wire-contract suite keeps validating runtime
        payloads against that stale schema and passes silently. This guard turns
        that silent drift into a loud, named failure.
        """
        installed = get_codex_version()
        tested = SemVer.parse(TESTED_CODEX_VERSION)
        assert installed == tested, (
            f"Installed codex {installed} != tested baseline {tested}. "
            f"Vendored fixtures are stale relative to the installed binary; the "
            f"wire-contract suite validates against the stale schema and passes "
            f"silently. Rebaseline via 'scripts/regenerate_schema.sh <version>' and "
            f"bump TESTED_CODEX_VERSION, or align the installed binary, before "
            f"trusting the contract gate."
        )


class TestCheckVersionFloor:
    def test_passes_with_current_binary(self):
        result = check_version_floor()
        assert result.passed, f"Version floor check failed: {result.errors}"

    def test_reports_version(self):
        result = check_version_floor()
        assert result.codex_version is not None

    def test_errors_empty_on_pass(self):
        result = check_version_floor()
        if result.passed:
            assert result.errors == ()


class TestFeatureGating:
    def test_has_capability_true_for_required_with_explicit_methods(self):
        result = CompatCheckResult.from_version_check(
            codex_version=SemVer.parse("0.117.0"),
            available_methods=REQUIRED_METHODS | OPTIONAL_METHODS,
        )
        assert result.has_capability("thread/start")

    def test_has_capability_false_for_nonexistent(self):
        result = CompatCheckResult.from_version_check(
            codex_version=SemVer.parse("0.117.0"),
            available_methods=REQUIRED_METHODS | OPTIONAL_METHODS,
        )
        assert not result.has_capability("nonexistent/method")

    def test_has_capability_for_optional_method_when_excluded(self):
        result = CompatCheckResult.from_version_check(
            codex_version=SemVer.parse("0.117.0"),
            available_methods=REQUIRED_METHODS,  # no optional
        )
        assert not result.has_capability("turn/steer")

    def test_has_capability_returns_bool(self):
        result = CompatCheckResult.from_version_check(
            codex_version=SemVer.parse("0.117.0"),
            available_methods=REQUIRED_METHODS | OPTIONAL_METHODS,
        )
        assert isinstance(result.has_capability("turn/steer"), bool)

    def test_exact_baseline_populates_methods(self):
        """Exact tested version gets vendored schema methods without explicit list."""
        result = CompatCheckResult.from_version_check(
            codex_version=SemVer.parse("0.117.0"),
        )
        assert result.has_capability("thread/start")
        assert result.has_capability("turn/steer")

    def test_newer_version_has_empty_methods(self):
        """Newer version gets empty methods — unverified until build step 1."""
        result = CompatCheckResult.from_version_check(
            codex_version=SemVer.parse("0.118.0"),
        )
        assert not result.has_capability("thread/start")
        assert not result.has_capability("turn/steer")
        assert result.passed  # startup still passes, just no capability claims


class TestLiveRuntimeCompatibility:
    def test_live_probe_returns_required_methods(self):
        available = probe_live_method_surface()
        missing = REQUIRED_METHODS - available
        assert missing == frozenset(), (
            f"Live probe missing required methods: {sorted(missing)}"
        )

    def test_live_runtime_compatibility_passes(self):
        result = check_live_runtime_compatibility()
        assert result.passed, f"Live runtime compatibility failed: {result.errors}"

    def test_optional_method_reported(self):
        result = check_live_runtime_compatibility()
        assert isinstance(result.has_capability("turn/steer"), bool)
