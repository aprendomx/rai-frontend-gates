"""Baseline cache lifecycle: load/save/snapshot/reset/stale-check/delta.

Storage: `.rai-frontend/baseline.json` in consumer repo root.
Schema versioned via SCHEMA_VERSION; auto-invalidation on
`package.json` version mismatch (see is_baseline_stale).
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from rai_frontend_gates.models import EslintError

BASELINE_DIR = ".rai-frontend"
BASELINE_FILE = "baseline.json"
SCHEMA_VERSION = "0.1"


def _baseline_path(cwd: Path) -> Path:
    return cwd / BASELINE_DIR / BASELINE_FILE


def load_baseline(cwd: Path) -> dict:
    """Load baseline.json or return empty schema-versioned default."""
    path = _baseline_path(cwd)
    if not path.exists():
        return {"schema_version": SCHEMA_VERSION, "gates": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def save_baseline(cwd: Path, data: dict) -> None:
    """Persist baseline dict to .rai-frontend/baseline.json (creates dir if needed)."""
    path = _baseline_path(cwd)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def snapshot_gate(
    cwd: Path,
    gate_id: str,
    exit_code: int,
    errors: list[EslintError],
    package_version: str,
) -> None:
    """Capture gate output as new baseline for delta comparison."""
    data = load_baseline(cwd)
    data.setdefault("schema_version", SCHEMA_VERSION)
    data.setdefault("gates", {})
    data["gates"][gate_id] = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "package_json_version": package_version,
        "exit_code": exit_code,
        "error_count": len(errors),
        "errors": [e.model_dump() for e in errors],
    }
    save_baseline(cwd, data)


def reset_gate(cwd: Path, gate_id: str) -> bool:
    """Remove gate entry from baseline. Returns True if entry existed."""
    data = load_baseline(cwd)
    if gate_id in data.get("gates", {}):
        del data["gates"][gate_id]
        save_baseline(cwd, data)
        return True
    return False


def is_baseline_stale(cwd: Path, gate_id: str, current_package_version: str) -> bool:
    """Return True if cached baseline's package version differs from current."""
    data = load_baseline(cwd)
    cached = data.get("gates", {}).get(gate_id, {})
    cached_version = cached.get("package_json_version", "")
    return bool(cached_version) and cached_version != current_package_version


def compute_delta(
    baseline_errors: list[EslintError],
    current_errors: list[EslintError],
) -> dict:
    """Compare two error lists by (file, line, rule) key tuple.

    Returns: {new: [EslintError], fixed: [EslintError], kept: int}.
    """
    def key(e: EslintError) -> tuple[str, int, str]:
        return (e.file, e.line, e.rule)

    baseline_by_key = {key(e): e for e in baseline_errors}
    current_by_key = {key(e): e for e in current_errors}

    baseline_keys = set(baseline_by_key)
    current_keys = set(current_by_key)

    return {
        "new": [current_by_key[k] for k in current_keys - baseline_keys],
        "fixed": [baseline_by_key[k] for k in baseline_keys - current_keys],
        "kept": len(current_keys & baseline_keys),
    }


def load_baseline_errors(cwd: Path, gate_id: str) -> list[EslintError]:
    """Convenience: load baseline errors for a gate as EslintError list."""
    data = load_baseline(cwd)
    raw = data.get("gates", {}).get(gate_id, {}).get("errors", [])
    return [EslintError(**e) for e in raw]
