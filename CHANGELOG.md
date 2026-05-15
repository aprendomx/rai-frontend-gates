# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-05-15

### Added

- `rai-frontend` CLI with 6 commands:
  - `gate check gate-{tests,lint,build} [--scope PATH] [--delta]`
  - `gate list` (auto-detects from `package.json` scripts)
  - `baseline snapshot --gate gate-lint`
  - `baseline reset --gate gate-lint`
- Pydantic models (`GateResult`, `GateContext`, `EslintError`) compatible with rai-cli shapes (bridge pattern, no upstream coupling)
- Eslint v9 stylish output parser (handles file headers, error/warning levels, summary lines)
- Baseline JSON cache at `.rai-frontend/baseline.json` (gitignored, per-developer)
- **Delta-vs-baseline display** for `gate-lint` (key tuple: `(file, line, rule)`; column excluded as drift-prone)
- **Auto-invalidation** on `package.json` version bump (warns user, suggests `baseline reset`)
- npm subprocess wrappers with explicit `text=True, encoding="utf-8"`
- 36 unit tests across 6 test modules
- 96% test coverage (`pytest --cov=rai_frontend_gates`)
- 10-step real-world smoke validation on `aprendomx/sinpapel-designer` + `creditos/frontend`

### Architecture

- **Path B chosen** over Path C (upstream raise-cli contribution) for ship speed and controllability. See [ADR-019](https://github.com/aprendomx/rai-frontend-gates/blob/main/ADR-019-NOTE.md) in `creditos/dev/decisions/adr-019-rai-frontend-gates-wrapper.md`.
- **Standalone Python package** fitting aprendomx repo pattern (sibling to `sinpapel`, `sinpapel-drf`, `sinpapel-webhooks`, `sinpapel-designer`).
- **Bridge pattern**: mirrors rai-cli Typer + Pydantic shapes without importing raise-cli (loose coupling).
- **Pinned dependencies**: `typer>=0.12`, `pydantic>=2.0,<3.0`, `rich>=13.0`.

### Known limitations (v0.1.0 → v0.2 roadmap)

- `gate check` doesn't auto-print raw errors on failure (only `--delta` flag does). **`--verbose` flag is v0.1.1/v0.2 candidate** (discovered via S30.3 real-world smoke, parked HIGH priority).
- Type-check gate (`gate-types` analog) deferred to v0.2.
- Coverage gate deferred to v0.2.
- Format gate (prettier wrap) deferred to v0.2.
- Auto-fix integration (`npm run lint -- --fix`) deferred to v0.2 if needed.
- Eslint v8 legacy config parsing deferred to v0.2 (v9 flat-config only).
- Vitest JSON output richer reporting deferred to v0.2 (exit-code-only for tests is intentional — test pass/fail is binary).

### Status

**Production-ready** for `aprendomx/sinpapel-designer` and `creditos/frontend`. Both consumer repos integrated via README + `.gitignore` updates in E30 S30.3. SSH pip install URL: `git+ssh://git@github.com/aprendomx/rai-frontend-gates.git@v0.1.0`.

### Origin

E30 epic in `creditos/work/epics/e30-rai-frontend-gates/` (governance + retrospectives). Recurring framework gap from 5 retros (S27.6, S27.7, S27.9, S29.1, S29.2). 4 stories (S30.1-S30.4); ~30 min total effective implementation across 2 days wall clock.
