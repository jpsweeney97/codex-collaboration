"""Targeted regression checks for operator-facing repo docs.

These assertions are intentionally narrow: they cover the specific README and
check-script drift that previously overstated the live tool surface, blurred
containment boundaries, and misrepresented the full verification gate.
"""

from __future__ import annotations

from pathlib import Path


_REPO_ROOT = Path(__file__).resolve().parent.parent
_README_PATH = _REPO_ROOT / "README.md"
_CHECK_SCRIPT_PATH = _REPO_ROOT / "scripts" / "check"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_readme_reports_current_mcp_tool_count() -> None:
    readme = _read_text(_README_PATH)

    assert "exposes 10 tools" in readme
    assert "exposes 11 tools" not in readme


def test_readme_distinguishes_contained_dialogue_agents_from_gatherers() -> None:
    readme = _read_text(_README_PATH)

    assert "`dialogue-orchestrator`" in readme
    assert "`shakedown-dialogue`" in readme
    assert "outside containment" in readme


def test_check_script_runs_marker_inclusive_suite() -> None:
    lines = [line.strip() for line in _read_text(_CHECK_SCRIPT_PATH).splitlines()]

    assert 'uv run pytest tests -q -m ""' in lines
