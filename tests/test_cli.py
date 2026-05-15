"""S30.1 smoke tests — CLI entry point + version + help + stub responses."""

from typer.testing import CliRunner

from rai_frontend_gates.cli import app

runner = CliRunner()


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


def test_gate_check_stub() -> None:
    """gate check stub responds with stub message and exit 0."""
    result = runner.invoke(app, ["gate", "check", "gate-tests"])
    assert result.exit_code == 0
    assert "stub" in result.stdout
    assert "gate-tests" in result.stdout
