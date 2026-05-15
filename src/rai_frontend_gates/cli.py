"""rai-frontend CLI — frontend stack gate wrapper for rai-cli.

v0.1.0 functional release (S30.2): 3 gates + baseline cache + delta display.
"""

from pathlib import Path

import typer

from rai_frontend_gates import __version__
from rai_frontend_gates import baseline as bl
from rai_frontend_gates import gates as gates_mod
from rai_frontend_gates.models import GateContext

app = typer.Typer(
    no_args_is_help=True,
    help="Frontend gate wrapper for rai-cli (npm/vitest/eslint/build)",
)
gate_app = typer.Typer(no_args_is_help=True, help="Run frontend gates")
baseline_app = typer.Typer(no_args_is_help=True, help="Manage gate baselines")
app.add_typer(gate_app, name="gate")
app.add_typer(baseline_app, name="baseline")


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"rai-frontend {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(  # noqa: ARG001 (consumed by callback)
        None,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    """rai-frontend CLI entry point."""


# ── Gate subcommands ─────────────────────────────────────────────────


@gate_app.command("check")
def gate_check(
    gate_id: str = typer.Argument(..., help="Gate identifier (gate-tests, gate-lint, gate-build)"),
    scope: str | None = typer.Option(None, "--scope", help="Path scope passed as extra arg to npm script"),
    delta: bool = typer.Option(False, "--delta", help="Show delta vs cached baseline (gate-lint only)"),
) -> None:
    """Run a frontend gate via npm and report results."""
    cwd = Path.cwd()
    ctx = GateContext(
        gate_id=gate_id,
        working_dir=str(cwd),
        extra_args=[scope] if scope else [],
        delta_mode=delta,
    )
    result = gates_mod.check_gate(ctx)
    typer.echo(result.message)
    for detail in result.details:
        typer.echo(detail)
    raise typer.Exit(code=result.exit_code)


@gate_app.command("list")
def gate_list() -> None:
    """List available gates detected from package.json scripts."""
    cwd = Path.cwd()
    try:
        available = gates_mod.list_gates(cwd)
    except FileNotFoundError:
        typer.echo("No package.json found in current directory", err=True)
        raise typer.Exit(code=2)

    if not available:
        typer.echo("No gates detected (package.json has no test/lint/build scripts)")
        return

    typer.echo("Available gates:")
    for gate_id in available:
        npm_script = gates_mod.GATE_TO_SCRIPT[gate_id]
        typer.echo(f"  {gate_id}  → npm run {npm_script}")


# ── Baseline subcommands ─────────────────────────────────────────────


@baseline_app.command("snapshot")
def baseline_snapshot(
    gate: str = typer.Option(..., "--gate", help="Gate identifier (currently only gate-lint supported)"),
) -> None:
    """Capture current gate output as baseline for delta comparison."""
    if gate != "gate-lint":
        typer.echo(f"Baseline currently supports gate-lint only (got: {gate})", err=True)
        raise typer.Exit(code=2)

    cwd = Path.cwd()
    count = gates_mod.snapshot_lint_baseline(cwd)
    typer.echo(f"baseline captured: {count} errors → .rai-frontend/baseline.json")


@baseline_app.command("reset")
def baseline_reset(
    gate: str = typer.Option(..., "--gate", help="Gate identifier to reset"),
) -> None:
    """Clear cached baseline for a gate."""
    cwd = Path.cwd()
    removed = bl.reset_gate(cwd, gate)
    if removed:
        typer.echo(f"baseline cleared for {gate}")
    else:
        typer.echo(f"no baseline found for {gate}")


if __name__ == "__main__":
    app()
