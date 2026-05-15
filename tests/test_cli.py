"""CLI integration tests — version, help, gate commands, baseline commands.

S30.1 smoke tests preserved; S30.2 adds integration tests with mocked GateRunner.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from rai_frontend_gates.cli import app

runner = CliRunner()


# ── S30.1 smoke tests (preserved) ─────────────────────────────────────


def test_version() -> None:
    """--version flag returns 0.1.0 and exits 0."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout


def test_help() -> None:
    """--help lists gate + baseline subcommands."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "gate" in result.stdout
    assert "baseline" in result.stdout


# ── S30.2 integration tests ────────────────────────────────────────────


def _make_pkg(tmp_path: Path, scripts: dict[str, str], version: str = "0.1.0") -> None:
    pj = {"name": "x", "version": version, "scripts": scripts}
    (tmp_path / "package.json").write_text(json.dumps(pj), encoding="utf-8")


@patch("rai_frontend_gates.gates.npm.run_npm_script")
def test_cli_gate_check_tests_passes(mock_run: MagicMock, tmp_path: Path) -> None:
    _make_pkg(tmp_path, {"test": "vitest run"})
    mock_run.return_value = MagicMock(returncode=0, stdout="ok", stderr="")
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Re-write package.json inside isolated cwd
        Path("package.json").write_text(
            json.dumps({"name": "x", "version": "0.1.0", "scripts": {"test": "vitest"}}),
            encoding="utf-8",
        )
        result = runner.invoke(app, ["gate", "check", "gate-tests"])
    assert result.exit_code == 0
    assert "gate-tests passed" in result.stdout


@patch("rai_frontend_gates.gates.npm.run_npm_script")
def test_cli_gate_check_failure_exits_nonzero(mock_run: MagicMock, tmp_path: Path) -> None:
    mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="boom")
    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path("package.json").write_text(
            json.dumps({"name": "x", "version": "0.1.0", "scripts": {"lint": "eslint"}}),
            encoding="utf-8",
        )
        result = runner.invoke(app, ["gate", "check", "gate-lint"])
    assert result.exit_code == 1
    assert "failed" in result.stdout


def test_cli_gate_list_shows_detected_scripts(tmp_path: Path) -> None:
    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path("package.json").write_text(
            json.dumps({
                "name": "x", "version": "0.1.0",
                "scripts": {"test": "vitest", "lint": "eslint", "dev": "vite"},
            }),
            encoding="utf-8",
        )
        result = runner.invoke(app, ["gate", "list"])
    assert result.exit_code == 0
    assert "gate-tests" in result.stdout
    assert "gate-lint" in result.stdout
    # dev script is not a gate
    assert "gate-dev" not in result.stdout


def test_cli_gate_list_no_package_json(tmp_path: Path) -> None:
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(app, ["gate", "list"])
    assert result.exit_code == 2


@patch("rai_frontend_gates.gates.npm.run_npm_script")
def test_cli_baseline_snapshot_and_reset_roundtrip(mock_run: MagicMock, tmp_path: Path) -> None:
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path("package.json").write_text(
            json.dumps({"name": "x", "version": "0.1.0", "scripts": {"lint": "eslint"}}),
            encoding="utf-8",
        )
        result_snap = runner.invoke(app, ["baseline", "snapshot", "--gate", "gate-lint"])
        assert result_snap.exit_code == 0
        assert "baseline captured" in result_snap.stdout

        result_reset = runner.invoke(app, ["baseline", "reset", "--gate", "gate-lint"])
        assert result_reset.exit_code == 0
        assert "cleared" in result_reset.stdout


def test_cli_baseline_snapshot_unsupported_gate(tmp_path: Path) -> None:
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(app, ["baseline", "snapshot", "--gate", "gate-tests"])
    assert result.exit_code == 2


def test_cli_baseline_reset_no_baseline(tmp_path: Path) -> None:
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(app, ["baseline", "reset", "--gate", "gate-lint"])
    assert result.exit_code == 0
    assert "no baseline found" in result.stdout
