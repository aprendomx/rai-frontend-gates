"""S30.2 T3 — npm subprocess wrappers + package.json readers."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from rai_frontend_gates.npm import (
    read_package_json_scripts,
    read_package_version,
    run_npm_script,
)


def test_run_npm_script_invokes_correct_command(tmp_path: Path) -> None:
    with patch("rai_frontend_gates.npm.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="ok", stderr="")
        run_npm_script("test", tmp_path)
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert cmd == ["npm", "run", "test"]
        kwargs = mock_run.call_args[1]
        assert kwargs["cwd"] == tmp_path
        assert kwargs["text"] is True
        assert kwargs["encoding"] == "utf-8"


def test_run_npm_script_with_extra_args(tmp_path: Path) -> None:
    with patch("rai_frontend_gates.npm.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        run_npm_script("test", tmp_path, extra_args=["tests/foo/"])
        cmd = mock_run.call_args[0][0]
        assert cmd == ["npm", "run", "test", "--", "tests/foo/"]


def test_read_package_json_scripts(tmp_path: Path) -> None:
    pj = {"name": "x", "version": "1.0.0", "scripts": {"test": "vitest run", "lint": "eslint ."}}
    (tmp_path / "package.json").write_text(json.dumps(pj), encoding="utf-8")
    scripts = read_package_json_scripts(tmp_path)
    assert scripts == {"test": "vitest run", "lint": "eslint ."}


def test_read_package_version(tmp_path: Path) -> None:
    pj = {"name": "x", "version": "0.2.3", "scripts": {}}
    (tmp_path / "package.json").write_text(json.dumps(pj), encoding="utf-8")
    assert read_package_version(tmp_path) == "0.2.3"


def test_read_missing_package_json_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        read_package_json_scripts(tmp_path)
