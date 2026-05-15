# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-05-15 (walking skeleton)

### Added

- Initial scaffolding (S30.1 bootstrap).
- `rai-frontend` CLI entry point (Typer-based).
- 4 stub subcommands: `gate check`, `gate list`, `baseline snapshot`, `baseline reset`.
- Pyproject.toml with deps pinned: Typer >=0.12, Pydantic >=2.0,<3.0, Rich >=13.0.
- Pytest harness with 3 smoke tests (version, help, gate-check stub).

### Notes

- Walking skeleton release; no gate logic yet (deferred to S30.2).
- See E30 design doc for full v0.1.0 scope.
