# Architecture

## Overview

`carbon-budget-action` is a composite GitHub Action. `action.yml` maps the
declared inputs to environment variables and runs a single script,
`carbon_budget.py`, on the runner's built-in Python. There is no build step and
no runtime dependency.

## Components

- **`action.yml`** — input/output contract and the composite `run` step.
- **`carbon_budget.py`** — the estimator and the gate. Reads inputs from env,
  writes `estimated-gco2e` / `within-budget` to `$GITHUB_OUTPUT` and a summary
  to `$GITHUB_STEP_SUMMARY`, and exits non-zero when over budget (unless
  `mode: report`).

## The carbon model

Cloud Carbon Footprint methodology, kept explainable. Per replica:

```
energy_kWh  = (cpu_cores * WATTS_PER_CORE + memory_gb * WATTS_PER_GB)
              * PUE * hours / 1000
gco2e       = energy_kWh * grid_intensity * replicas
```

All constants (`WATTS_PER_CORE`, `WATTS_PER_GB`, `PUE`) live at the top of
`carbon_budget.py` so the estimate stays auditable and tunable.

## Data flow

```
inputs (action.yml) → env vars → carbon_budget.py → gCO2e estimate
    → compare to budget → job summary + outputs → pass/fail exit code
```

## Decisions

- Composite (not Docker) action: zero image to build or pull, runs on the
  runner's Python.
- No runtime dependencies: the action must run on a clean Python install.
