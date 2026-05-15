"""npm subprocess wrappers + package.json readers."""

import json
import subprocess
from pathlib import Path


def run_npm_script(
    script: str,
    cwd: Path,
    extra_args: list[str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run `npm run <script>` in cwd, capturing stdout/stderr as UTF-8 text."""
    cmd = ["npm", "run", script]
    if extra_args:
        cmd.extend(["--", *extra_args])
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def read_package_json_scripts(cwd: Path) -> dict[str, str]:
    """Read `scripts` section from package.json in cwd.

    Raises FileNotFoundError if package.json is absent.
    """
    pj = json.loads((cwd / "package.json").read_text(encoding="utf-8"))
    return pj.get("scripts", {})


def read_package_version(cwd: Path) -> str:
    """Read `version` field from package.json in cwd."""
    pj = json.loads((cwd / "package.json").read_text(encoding="utf-8"))
    return pj.get("version", "")
