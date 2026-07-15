# carbon-budget-action

[![CI](https://github.com/fabiocicerchia/carbon-budget-action/actions/workflows/ci.yml/badge.svg)](https://github.com/fabiocicerchia/carbon-budget-action/actions/workflows/ci.yml)
[![Security](https://github.com/fabiocicerchia/carbon-budget-action/actions/workflows/security.yml/badge.svg)](https://github.com/fabiocicerchia/carbon-budget-action/actions/workflows/security.yml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/fabiocicerchia/carbon-budget-action/badge)](https://securityscorecards.dev/viewer/?uri=github.com/fabiocicerchia/carbon-budget-action)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Ffabiocicerchia%2Fcarbon-budget-action.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2Ffabiocicerchia%2Fcarbon-budget-action?ref=badge_shield)
[![Release](https://img.shields.io/github/v/release/fabiocicerchia/carbon-budget-action)](https://github.com/fabiocicerchia/carbon-budget-action/releases)

A **CI gate that fails when a deployment's estimated carbon footprint exceeds
a budget** — bundle-size checks, but for carbon. Give each service a gCO2e
budget; scaling up replicas or requests past it needs a conscious, reviewed
decision instead of a silent drift.

```yaml
- uses: fabiocicerchia/carbon-budget-action@v1
  with:
    budget-gco2e: 5000        # per month of runtime
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

## Status & roadmap

- [x] Composite action, estimate + gate + job summary + outputs
- [x] Read replicas/requests straight from the k8s manifests in the diff
- [x] Live grid intensity (pairs with `carbon-region-picker`)
- [x] PR comment with the delta vs the base branch (true "bundle-size" UX)
- [ ] Embodied-carbon amortization option

## Documentation

Full docs live in [`docs/`](docs/); runnable examples in [`examples/`](examples/).

## Development

`make setup` (hooks) then `make dev`, `make test`, `make lint`.
See [CONTRIBUTING.md](CONTRIBUTING.md) and the
[Code of Conduct](CODE_OF_CONDUCT.md).

## Security

Found a vulnerability? See [SECURITY.md](SECURITY.md) — please don't open a
public issue.

## License

Apache 2.0 — see [LICENSE](LICENSE).
