"""S30.2 T5 — GateRunner orchestration tests (mocked subprocess)."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from rai_frontend_gates import baseline as bl
from rai_frontend_gates.gates import (
    GATE_TO_SCRIPT,
    check_gate,
    list_gates,
    snapshot_lint_baseline,
)
from rai_frontend_gates.models import GateContext


def _write_pkg(tmp_path: Path, scripts: dict[str, str], version: str = "0.1.0") -> None:
    pj = {"name": "x", "version": version, "scripts": scripts}
    (tmp_path / "package.json").write_text(json.dumps(pj), encoding="utf-8")


@patch("rai_frontend_gates.gates.npm.run_npm_script")
def test_gate_tests_success(mock_run: MagicMock, tmp_path: Path) -> None:
    _write_pkg(tmp_path, {"test": "vitest run"})
    mock_run.return_value = MagicMock(returncode=0, stdout="1 passed", stderr="")
    result = check_gate(GateContext(gate_id="gate-tests", working_dir=str(tmp_path)))
    assert result.passed is True
    assert result.exit_code == 0
    assert "passed" in result.message
    # Verify npm called with "test" script
    assert mock_run.call_args[0][0] == "test"


@patch("rai_frontend_gates.gates.npm.run_npm_script")
def test_gate_tests_failure_propagates_exit_code(mock_run: MagicMock, tmp_path: Path) -> None:
    _write_pkg(tmp_path, {"test": "vitest run"})
    mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="0 passed, 1 failed")
    result = check_gate(GateContext(gate_id="gate-tests", working_dir=str(tmp_path)))
    assert result.passed is False
    assert result.exit_code == 1


def test_unknown_gate_returns_error_result(tmp_path: Path) -> None:
    result = check_gate(GateContext(gate_id="gate-bogus", working_dir=str(tmp_path)))
    assert result.passed is False
    assert "Unknown gate" in result.message
    assert result.exit_code == 2


@patch("rai_frontend_gates.gates.npm.run_npm_script")
def test_gate_lint_delta_no_baseline_yet(mock_run: MagicMock, tmp_path: Path) -> None:
    _write_pkg(tmp_path, {"lint": "eslint ."})
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    ctx = GateContext(gate_id="gate-lint", working_dir=str(tmp_path), delta_mode=True)
    result = check_gate(ctx)
    assert result.passed is True
    # Details include the "no baseline yet" hint
    assert any("no baseline yet" in d for d in result.details)


@patch("rai_frontend_gates.gates.npm.run_npm_script")
def test_gate_lint_delta_stale_baseline(mock_run: MagicMock, tmp_path: Path) -> None:
    _write_pkg(tmp_path, {"lint": "eslint ."}, version="0.2.0")
    # Pre-snapshot baseline with old version
    bl.snapshot_gate(tmp_path, "gate-lint", exit_code=0, errors=[], package_version="0.1.0")
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    ctx = GateContext(gate_id="gate-lint", working_dir=str(tmp_path), delta_mode=True)
    result = check_gate(ctx)
    assert any("baseline stale" in d for d in result.details)


def test_list_gates_detects_from_package_json(tmp_path: Path) -> None:
    _write_pkg(tmp_path, {"test": "vitest", "lint": "eslint", "dev": "vite", "format": "prettier"})
    gates = list_gates(tmp_path)
    assert "gate-tests" in gates
    assert "gate-lint" in gates
    assert "gate-build" not in gates  # no build script
    # dev/format excluded (not in GATE_TO_SCRIPT map)


def test_list_gates_all_three(tmp_path: Path) -> None:
    _write_pkg(tmp_path, {"test": "vitest", "lint": "eslint", "build": "vite build"})
    gates = list_gates(tmp_path)
    assert set(gates) == {"gate-tests", "gate-lint", "gate-build"}


@patch("rai_frontend_gates.gates.npm.run_npm_script")
def test_snapshot_lint_baseline_persists(mock_run: MagicMock, tmp_path: Path) -> None:
    _write_pkg(tmp_path, {"lint": "eslint ."})
    mock_run.return_value = MagicMock(
        returncode=1,
        stdout="\n/foo.vue\n  1:1  error  bad  no-x\n\n✖ 1 problem\n",
        stderr="",
    )
    count = snapshot_lint_baseline(tmp_path)
    assert count == 1
    # Verify baseline.json was created
    assert (tmp_path / ".rai-frontend" / "baseline.json").exists()
    data = bl.load_baseline(tmp_path)
    assert "gate-lint" in data["gates"]
    assert data["gates"]["gate-lint"]["error_count"] == 1


def test_gate_to_script_map_contract() -> None:
    """Sanity: the 3 gates we promise are all present."""
    assert set(GATE_TO_SCRIPT) == {"gate-tests", "gate-lint", "gate-build"}
    assert GATE_TO_SCRIPT["gate-tests"] == "test"
    assert GATE_TO_SCRIPT["gate-lint"] == "lint"
    assert GATE_TO_SCRIPT["gate-build"] == "build"
