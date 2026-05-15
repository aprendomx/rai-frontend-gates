# rai-frontend-gates

Frontend stack gate wrapper for [rai-cli](https://github.com/humansys/raise) — extends `rai gate check` UX to npm/vitest/eslint/build stacks.

## Status

**v0.1.0** — Walking skeleton release. CLI surface scaffolded; gate logic in progress (S30.2).

See [CHANGELOG.md](./CHANGELOG.md).

## Install

```bash
pip install "rai-frontend-gates @ git+ssh://git@github.com/aprendomx/rai-frontend-gates.git@v0.1.0"
```

Requires Python 3.10+.

## Usage (v0.1.0 — stubs)

```bash
rai-frontend --version
# rai-frontend 0.1.0

rai-frontend --help
# Lists: gate, baseline subcommands

rai-frontend gate check gate-tests
# gate-check stub: gate-tests
```

## Planned commands (S30.2)

```bash
rai-frontend gate check gate-tests [--scope PATH]
rai-frontend gate check gate-lint [--scope PATH] [--delta]
rai-frontend gate check gate-build
rai-frontend gate list
rai-frontend baseline snapshot --gate gate-lint
rai-frontend baseline reset --gate gate-lint
```

## Architecture

See E30 design in the governance repo (`creditos/work/epics/e30-rai-frontend-gates/design.md`) and ADR-019 (lands S30.4).

## License

MIT
