"""S30.2 T2 — Eslint v9 stylish output parser."""

from pathlib import Path

from rai_frontend_gates.eslint_parser import parse_eslint_output

FIXTURES = Path(__file__).parent / "fixtures"


def test_empty_output() -> None:
    assert parse_eslint_output("") == []


def test_empty_fixture_file() -> None:
    output = (FIXTURES / "eslint_empty.txt").read_text(encoding="utf-8")
    assert parse_eslint_output(output) == []


def test_stylish_multi_file_errors() -> None:
    output = (FIXTURES / "eslint_stylish.txt").read_text(encoding="utf-8")
    errors = parse_eslint_output(output)
    # Only errors counted (3 errors, 1 warning); parser includes ONLY errors per spec
    assert len(errors) == 3
    files = {e.file for e in errors}
    assert any("CatalogosPage.vue" in f for f in files)
    assert any("CatalogoEditor.vue" in f for f in files)
    # First error: line 42, rule no-unused-vars
    first = next(e for e in errors if "CatalogosPage" in e.file and e.line == 42)
    assert first.rule == "no-unused-vars"
    assert "foo" in first.message


def test_tolerates_summary_line() -> None:
    # Output containing "✖ N problems" summary should not crash or produce phantom errors
    output = """
/foo/bar.js
  1:1  error  bad stuff  some-rule

✖ 1 problem (1 error, 0 warnings)
"""
    errors = parse_eslint_output(output)
    assert len(errors) == 1
    assert errors[0].rule == "some-rule"
