# Getting Started

## Prerequisites

- A GitHub repository with Actions enabled. Nothing to install — the action
  runs on the runner's built-in Python.

## Add the action

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
          budget-gco2e: 5000     # per deploy cycle
          replicas: 4
          cpu-request: 500m
          memory-request: 1Gi
          grid-intensity: 56     # gCO2e/kWh; default 480 (world avg)
```

The job fails when the estimate exceeds `budget-gco2e`. Use `mode: report` to
post the estimate to the job summary without ever failing the build — the
adoption on-ramp.

Pass `manifest-path` instead of `replicas`/`cpu-request`/`memory-request` to
read them straight from a k8s Deployment/StatefulSet manifest (first
container's `requests:` block).

Pass `em-zone` + `em-token` to fetch live grid intensity from
[Electricity Maps](https://www.electricitymaps.com/) instead of the static
`grid-intensity` input (falls back to it on any API error).

## Outputs

| Output            | Description                       |
| ----------------- | --------------------------------- |
| `estimated-gco2e` | Estimated footprint in gCO2e      |
| `within-budget`   | `true` / `false`                  |

## Run locally

```sh
BUDGET_GCO2E=5000 REPLICAS=4 CPU_REQUEST=500m python carbon_budget.py
```
