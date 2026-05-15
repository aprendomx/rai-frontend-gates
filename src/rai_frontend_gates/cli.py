"""rai-frontend CLI — frontend stack gate wrapper for rai-cli.

v0.1.0 walking skeleton — stubs only. Real gate logic lands in S30.2.
"""

import typer

from rai_frontend_gates import __version__

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
    version: bool = typer.Option(
        None,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    """rai-frontend CLI entry point."""


# ── Stub subcommands (S30.2 fills logic) ─────────────────────────────


@gate_app.command("check")
def gate_check(
    gate_id: str = typer.Argument(..., help="Gate identifier (e.g. gate-tests)"),
    scope: str | None = typer.Option(None, "--scope", help="Path scope"),
    delta: bool = typer.Option(False, "--delta", help="Show delta vs baseline"),
) -> None:
    """Run a frontend gate (stub — S30.2 implements logic)."""
    parts = [f"gate-check stub: {gate_id}"]
    if scope:
        parts.append(f"scope={scope}")
    if delta:
        parts.append("delta=enabled")
    typer.echo(" | ".join(parts))
    raise typer.Exit(code=0)


@gate_app.command("list")
def gate_list() -> None:
    """List available gates (stub — S30.2 reads package.json scripts)."""
    typer.echo("gate-list stub: gate-tests, gate-lint, gate-build (S30.2 will detect from package.json)")


@baseline_app.command("snapshot")
def baseline_snapshot(
    gate: str = typer.Option(..., "--gate", help="Gate identifier to snapshot"),
) -> None:
    """Capture current gate output as baseline (stub — S30.2 implements)."""
    typer.echo(f"baseline-snapshot stub: gate={gate}")


@baseline_app.command("reset")
def baseline_reset(
    gate: str = typer.Option(..., "--gate", help="Gate identifier to reset"),
) -> None:
    """Clear cached baseline for a gate (stub — S30.2 implements)."""
    typer.echo(f"baseline-reset stub: gate={gate}")


if __name__ == "__main__":
    app()
