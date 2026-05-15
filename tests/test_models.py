"""S30.2 T1 — Pydantic model contracts."""

from rai_frontend_gates.models import EslintError, GateContext, GateResult


def test_eslint_error_required_fields() -> None:
    err = EslintError(file="src/a.vue", line=10, column=5, rule="no-unused-vars", message="x")
    assert err.file == "src/a.vue"
    assert err.line == 10
    assert err.column == 5
    assert err.rule == "no-unused-vars"
    assert err.message == "x"


def test_gate_result_defaults() -> None:
    r = GateResult(passed=True, gate_id="gate-tests", message="OK", exit_code=0)
    assert r.details == []
    assert r.raw_output == ""
    # Round-trip
    assert GateResult(**r.model_dump()).passed is True


def test_gate_context_defaults() -> None:
    ctx = GateContext(gate_id="gate-lint", working_dir="/tmp")
    assert ctx.extra_args == []
    assert ctx.delta_mode is False
