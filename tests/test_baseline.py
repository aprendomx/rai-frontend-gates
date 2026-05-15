"""S30.2 T4 — Baseline cache lifecycle + delta computation."""

from pathlib import Path

from rai_frontend_gates.baseline import (
    SCHEMA_VERSION,
    compute_delta,
    is_baseline_stale,
    load_baseline,
    reset_gate,
    save_baseline,
    snapshot_gate,
)
from rai_frontend_gates.models import EslintError


def _err(file: str, line: int, rule: str) -> EslintError:
    return EslintError(file=file, line=line, column=0, rule=rule, message="x")


def test_load_baseline_empty(tmp_path: Path) -> None:
    data = load_baseline(tmp_path)
    assert data["schema_version"] == SCHEMA_VERSION
    assert data["gates"] == {}


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    payload = {"schema_version": SCHEMA_VERSION, "gates": {"gate-lint": {"error_count": 5}}}
    save_baseline(tmp_path, payload)
    assert load_baseline(tmp_path) == payload


def test_snapshot_gate_then_reset(tmp_path: Path) -> None:
    errs = [_err("a.vue", 1, "no-x"), _err("b.vue", 2, "no-y")]
    snapshot_gate(tmp_path, "gate-lint", exit_code=1, errors=errs, package_version="0.1.0")
    data = load_baseline(tmp_path)
    assert "gate-lint" in data["gates"]
    assert data["gates"]["gate-lint"]["error_count"] == 2
    assert data["gates"]["gate-lint"]["package_json_version"] == "0.1.0"

    assert reset_gate(tmp_path, "gate-lint") is True
    data = load_baseline(tmp_path)
    assert "gate-lint" not in data["gates"]

    # Reset on missing gate returns False
    assert reset_gate(tmp_path, "gate-lint") is False


def test_is_baseline_stale_on_version_mismatch(tmp_path: Path) -> None:
    snapshot_gate(tmp_path, "gate-lint", exit_code=0, errors=[], package_version="0.1.0")
    assert is_baseline_stale(tmp_path, "gate-lint", "0.2.0") is True
    assert is_baseline_stale(tmp_path, "gate-lint", "0.1.0") is False
    # No baseline → not stale (no baseline to be stale)
    assert is_baseline_stale(tmp_path, "gate-other", "0.1.0") is False


def test_compute_delta_new_fixed_kept() -> None:
    baseline = [_err("a.vue", 1, "no-x"), _err("b.vue", 2, "no-y")]
    current = [_err("a.vue", 1, "no-x"), _err("c.vue", 3, "no-z")]
    delta = compute_delta(baseline, current)
    # a.vue:1:no-x is kept (in both)
    # b.vue:2:no-y is fixed (in baseline, not in current)
    # c.vue:3:no-z is new (in current, not in baseline)
    assert delta["kept"] == 1
    assert len(delta["new"]) == 1
    assert delta["new"][0].file == "c.vue"
    assert len(delta["fixed"]) == 1
    assert delta["fixed"][0].file == "b.vue"


def test_compute_delta_empty_cases() -> None:
    assert compute_delta([], []) == {"new": [], "fixed": [], "kept": 0}
    only_new = compute_delta([], [_err("a.vue", 1, "r")])
    assert len(only_new["new"]) == 1 and only_new["fixed"] == [] and only_new["kept"] == 0
    only_fixed = compute_delta([_err("a.vue", 1, "r")], [])
    assert only_fixed["new"] == [] and len(only_fixed["fixed"]) == 1 and only_fixed["kept"] == 0
