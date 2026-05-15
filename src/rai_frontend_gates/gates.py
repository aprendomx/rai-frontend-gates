"""GateRunner — orchestrates npm subprocess + parsing + baseline delta."""

from pathlib import Path

from rai_frontend_gates import baseline as bl
from rai_frontend_gates import npm
from rai_frontend_gates.eslint_parser import parse_eslint_output
from rai_frontend_gates.models import EslintError, GateContext, GateResult

# Map gate_id → npm script name
GATE_TO_SCRIPT: dict[str, str] = {
    "gate-tests": "test",
    "gate-lint": "lint",
    "gate-build": "build",
}


def list_gates(cwd: Path) -> list[str]:
    """Detect available gates from package.json scripts."""
    scripts = npm.read_package_json_scripts(cwd)
    return [gate_id for gate_id, script in GATE_TO_SCRIPT.items() if script in scripts]


def check_gate(ctx: GateContext) -> GateResult:
    """Run a gate and return structured result.

    For gate-lint with delta_mode, also computes diff vs baseline.
    """
    if ctx.gate_id not in GATE_TO_SCRIPT:
        return GateResult(
            passed=False,
            gate_id=ctx.gate_id,
            message=f"Unknown gate: {ctx.gate_id}",
            exit_code=2,
        )

    script = GATE_TO_SCRIPT[ctx.gate_id]
    cwd = Path(ctx.working_dir)
    proc = npm.run_npm_script(script, cwd, extra_args=ctx.extra_args or None)

    passed = proc.returncode == 0
    details: list[str] = []

    # Delta mode applies only to gate-lint (eslint parseable)
    if ctx.delta_mode and ctx.gate_id == "gate-lint":
        current_errors = parse_eslint_output(proc.stdout + proc.stderr)
        current_version = npm.read_package_version(cwd)
        if bl.is_baseline_stale(cwd, ctx.gate_id, current_version):
            details.append(
                f"baseline stale: package.json version changed → "
                "run: rai-frontend baseline reset --gate gate-lint"
            )
        else:
            baseline_errors = bl.load_baseline_errors(cwd, ctx.gate_id)
            if baseline_errors or _has_baseline(cwd, ctx.gate_id):
                delta = bl.compute_delta(baseline_errors, current_errors)
                details.append(
                    f"baseline: {len(baseline_errors)} errors | "
                    f"current: {len(current_errors)} errors | "
                    f"delta: +{len(delta['new'])} new, -{len(delta['fixed'])} fixed, "
                    f"{delta['kept']} kept"
                )
                for e in delta["new"]:
                    details.append(f"  + {e.file}:{e.line} [{e.rule}] {e.message}")
            else:
                details.append(
                    f"no baseline yet ({len(current_errors)} errors); "
                    f"run: rai-frontend baseline snapshot --gate gate-lint"
                )

    message = "passed" if passed else "failed"
    return GateResult(
        passed=passed,
        gate_id=ctx.gate_id,
        message=f"{ctx.gate_id} {message} (exit {proc.returncode})",
        details=details,
        exit_code=proc.returncode,
        raw_output=proc.stdout + ("\n" + proc.stderr if proc.stderr else ""),
    )


def _has_baseline(cwd: Path, gate_id: str) -> bool:
    """Check if any baseline entry exists for this gate."""
    data = bl.load_baseline(cwd)
    return gate_id in data.get("gates", {})


def snapshot_lint_baseline(cwd: Path) -> int:
    """Capture current eslint output as new baseline for gate-lint.

    Returns the error count captured.
    """
    proc = npm.run_npm_script(GATE_TO_SCRIPT["gate-lint"], cwd)
    errors: list[EslintError] = parse_eslint_output(proc.stdout + proc.stderr)
    version = npm.read_package_version(cwd)
    bl.snapshot_gate(
        cwd,
        gate_id="gate-lint",
        exit_code=proc.returncode,
        errors=errors,
        package_version=version,
    )
    return len(errors)
