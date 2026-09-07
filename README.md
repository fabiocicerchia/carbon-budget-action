# carbon-budget-action

[![CI](https://github.com/fabiocicerchia/carbon-budget-action/actions/workflows/ci.yml/badge.svg)](https://github.com/fabiocicerchia/carbon-budget-action/actions/workflows/ci.yml)
[![Security](https://github.com/fabiocicerchia/carbon-budget-action/actions/workflows/security.yml/badge.svg)](https://github.com/fabiocicerchia/carbon-budget-action/actions/workflows/security.yml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/fabiocicerchia/carbon-budget-action/badge)](https://securityscorecards.dev/viewer/?uri=github.com/fabiocicerchia/carbon-budget-action)
[![CI carbon](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/fabiocicerchia/carbon-budget-action/gh-pages/badge.json)](.github/workflows/carbon-badge.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/fabiocicerchia/carbon-budget-action)](https://github.com/fabiocicerchia/carbon-budget-action/releases)

A **CI gate that fails when a deployment's estimated carbon footprint exceeds
a budget** — bundle-size checks, but for carbon. Give each service a gCO2e
budget; scaling up replicas or requests past it needs a conscious, reviewed
decision instead of a silent drift.

```yaml
- uses: fabiocicerchia/carbon-budget-action@v1
  with:
    budget-gco2e: 5000        # per month of runtime
    hours: 720                # 30d — window the budget above applies to
    replicas: 4
    cpu-request: 500m
    memory-request: 1Gi
    grid-intensity: 56        # eu-north-1; default 480 (world avg)
```

```markdown
## 🌍 Carbon budget check
Estimated: **3,110 gCO2e** / budget 5,000 gCO2e (62%) ✅ within budget
`████████████`
```

## Model

Cloud Carbon Footprint methodology, kept explainable: ~4 W per CPU core,
0.4 W per GB RAM, PUE 1.2, × runtime hours × grid intensity. All constants
live at the top of `carbon_budget.py`. `mode: report` posts the estimate
without ever failing the build — the adoption on-ramp.

## Install

Nothing to install — reference it from a workflow with `uses:`. See **Usage** below.

## Usage

```yaml
# .github/workflows/carbon.yml
name: carbon budget
on: [pull_request]

jobs:
  carbon:
    runs-on: ubuntu-latest
    steps:
      - uses: fabiocicerchia/carbon-budget-action@v1
        with:
```

More in [`docs/getting-started.md`](docs/getting-started.md).

## Documentation

Full docs live in [`docs/`](docs/); runnable examples in [`examples/`](examples/).

## Development

`make setup` installs the dev dependencies and the pre-commit hook; `make
help` lists every target. Every repository in this estate exposes the same
eight verbs, so you do not have to read a Makefile to find out how to test it
(FC-GEN-057).

| Verb      | What it does here                                        |
| --------- | -------------------------------------------------------- |
| `setup`   | `requirements-dev.txt` + the pre-commit hook             |
| `run`     | The estimator locally: `BUDGET_GCO2E=5000 make run`      |
| `test`    | `pytest -q`                                              |
| `lint`    | `pre-commit run --all-files` — the whole gate            |
| `format`  | `ruff format .`                                          |
| `analyze` | `trivy fs` — vulnerabilities, misconfig, secrets         |

### Not applicable

Two verbs have no meaning for a composite action. They exit 0 and say why
rather than pretending to work (FC-GEN-058):

- `install` — consumers name this action in a workflow step.
- `build` — `action.yml` runs `carbon_budget.py` straight from the checkout.

See [CONTRIBUTING.md](CONTRIBUTING.md) and the
[Code of Conduct](CODE_OF_CONDUCT.md).

## Security

Found a vulnerability? See [SECURITY.md](SECURITY.md) — please don't open a
public issue.

## Support

Need help implementing this? [Get in touch](https://fabiocicerchia.it/contact).

## License

Apache 2.0 — see [LICENSE](LICENSE).
