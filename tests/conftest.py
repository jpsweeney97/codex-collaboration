"""Shared fixtures for codex-collaboration tests."""

import os
from collections.abc import Iterator
from pathlib import Path

import pytest

from server.codex_compat import TESTED_CODEX_VERSION

FIXTURES_DIR = (
    Path(__file__).parent / "fixtures" / "codex-app-server" / TESTED_CODEX_VERSION
)


@pytest.fixture(scope="session", autouse=True)
def _git_identity_for_subprocess_commits() -> Iterator[None]:
    """Ensure subprocess git commits have an author identity.

    Tests that create temporary git repos and clone them rely on ``git commit``
    succeeding in the clone. The clone inherits no per-path identity, and
    strict git builds (Linux CI runners) refuse to fall back to
    ``username@hostname``, exiting 128. macOS git auto-derives identity from
    ``getpwuid()``, which masks this divergence during local development.

    Setting GIT_AUTHOR_* and GIT_COMMITTER_* env vars makes the suite
    hermetic across hosts: these are git's highest-priority identity source
    and are inherited by every ``subprocess.run(["git", ...])`` call.
    """
    keys = {
        "GIT_AUTHOR_NAME": "codex-collaboration-tests",
        "GIT_AUTHOR_EMAIL": "tests@codex-collaboration.invalid",
        "GIT_COMMITTER_NAME": "codex-collaboration-tests",
        "GIT_COMMITTER_EMAIL": "tests@codex-collaboration.invalid",
    }
    previous = {k: os.environ.get(k) for k in keys}
    os.environ.update(keys)
    try:
        yield
    finally:
        for k, v in previous.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


@pytest.fixture
def vendored_schema_dir() -> Path:
    """Path to the vendored schema bundle for the tested version."""
    if not FIXTURES_DIR.is_dir():
        pytest.skip(f"Vendored schema not found at {FIXTURES_DIR}")
    return FIXTURES_DIR


@pytest.fixture
def client_request_schema(vendored_schema_dir: Path) -> Path:
    """Path to the vendored ClientRequest.json."""
    path = vendored_schema_dir / "ClientRequest.json"
    if not path.exists():
        pytest.skip("ClientRequest.json not found in vendored schema")
    return path


from server.models import CollaborationHandle  # noqa: E402


def make_test_handle(
    collaboration_id: str = "collab-1",
    runtime_id: str = "rt-1",
    thread_id: str = "thr-1",
    session_id: str = "sess-1",
    repo_root: str = "/repo",
    status: str = "active",
) -> CollaborationHandle:
    """Factory for test CollaborationHandle instances."""
    return CollaborationHandle(
        collaboration_id=collaboration_id,
        capability_class="advisory",
        runtime_id=runtime_id,
        codex_thread_id=thread_id,
        claude_session_id=session_id,
        repo_root=repo_root,
        created_at="2026-03-28T00:00:00Z",
        status=status,
    )
