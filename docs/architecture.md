# Architecture

## Overview

`carbon-budget-action` is a composite GitHub Action. `action.yml` maps the
declared inputs to environment variables and runs a single script,
`carbon_budget.py`, on the runner's built-in Python. There is no build step and
no runtime dependency.

## Components

- **`action.yml`** — input/output contract and the composite `run` step.
- **`carbon_budget.py`** — the estimator and the gate. Reads inputs from env,
  writes `estimated-gco2e` / `within-budget` (plus `burned-gco2e` /
  `window-start` when `track-budget: true`) to `$GITHUB_OUTPUT` and a summary
  to `$GITHUB_STEP_SUMMARY`, and exits non-zero when over budget (unless
  `mode: report`).

## The carbon model

Cloud Carbon Footprint methodology, kept explainable. Per replica:

```
energy_kWh  = (cpu_cores * W_PER_CORE + memory_gb * W_PER_GB)
              * PUE * hours / 1000
gco2e       = energy_kWh * grid_intensity * replicas
              + embodied_gco2e * (hours / (lifetime_years * 365 * 24)) * replicas
```

All constants (`W_PER_CORE`, `W_PER_GB`, `PUE`) live at the top of
`carbon_budget.py` so the estimate stays auditable and tunable. The embodied
term is opt-in (`embodied-gco2e` defaults to `0`) and amortizes one replica's
underlying server's manufacturing footprint over its expected lifetime.

## Data flow

```
inputs (action.yml) → env vars → carbon_budget.py → gCO2e estimate
    → compare to budget → job summary + outputs → pass/fail exit code
```

### Error-budget mode (`track-budget`)

The action holds no state across runs — `budget-gco2e` is checked against a
single run's estimate unless the caller opts into `track-budget: true` and
feeds back its own `burned-gco2e` / `window-start` outputs from the previous
run (the same caller-supplied-state pattern `base-gco2e` already uses).
`rollover_burn()` carries the burned total forward while the window (started
at `window-start`, `hours` long) is still open, or resets it to `0` once
`hours` has elapsed. `within-budget` then reflects the window's running
total, not just this run — meant for gating a *deploy* step (skip this
rollout once the window's budget is spent) rather than a PR check, since
blocking a PR doesn't affect what's already running. See
[Getting Started](getting-started.md#error-budget-mode-track-budget) for a
worked example of persisting that state via the Actions cache.

## Decisions

- Composite (not Docker) action: zero image to build or pull, runs on the
  runner's Python.
- No runtime dependencies: the action must run on a clean Python install.
