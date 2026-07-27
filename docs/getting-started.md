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

Pass `base-gco2e` (e.g. the `estimated-gco2e` output from a run on the base
branch) to render a Δ, and `pr-comment: true` + `github-token: ${{ github.token }}`
to post/update a PR comment with the summary instead of only the job summary.

Pass `embodied-gco2e` (one replica's server's total manufacturing footprint)
+ `embodied-lifetime-years` (default 4) to amortize embodied carbon into the
estimate, proportional to the run's `hours` over the hardware's lifetime.

### Error-budget mode (`track-budget`)

By default `budget-gco2e` is checked against *this run's* estimate alone —
fine for a PR check on the diff, but blocking a PR doesn't stop whatever's
already running in production from emitting. `track-budget: true` makes
`budget-gco2e` apply to a running total for the window instead — an SRE
error budget for carbon. Put it in the *deploy* job, not the PR check: once
the window's budget is burned, this step fails and the deploy step (gated on
it, e.g. `if: steps.budget.outcome == 'success'`) gets skipped until the
window resets — it doesn't touch what's already deployed.

This action keeps no state of its own (same as `base-gco2e`): pass its own
`burned-gco2e` and `window-start` outputs from the previous deploy back in
as inputs next time. Leave them unset on the first run; the window starts
then, and resets automatically once `hours` has elapsed since.

The `outcome == 'success'` check on the deploy step only works with the
default `mode: gate` (this step needs to actually fail when the budget's
burned). Under `mode: report` this step never fails, so check
`steps.budget.outputs.within-budget == 'true'` instead.

The example below persists state in the Actions cache instead of committing
to the repo: `actions/cache` has no key-overwrite, so each run deletes the
previous entry (via the `gh-actions-cache` CLI extension, which works under
the default `GITHUB_TOKEN`'s `actions: write` permission — no extra token
needed) and re-saves it. Two caveats: caches unused for 7 days are
auto-evicted, silently resetting the window early if deploys are sparser
than that; and without `concurrency`, two runs racing the same
restore/delete/save can lose one's write, so the job pins itself to a single
lane.

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    concurrency:
      group: carbon-budget-state
      cancel-in-progress: false
    steps:
      - uses: actions/cache/restore@v4
        id: cache
        with:
          path: carbon-state.json
          key: carbon-budget-state

      - id: state
        run: |
          if [ -f carbon-state.json ]; then
            echo "burned=$(jq -r .burned carbon-state.json)" >> "$GITHUB_OUTPUT"
            echo "window-start=$(jq -r .window_start carbon-state.json)" >> "$GITHUB_OUTPUT"
          else
            echo "burned=0" >> "$GITHUB_OUTPUT"
            echo "window-start=" >> "$GITHUB_OUTPUT"
          fi

      - id: budget
        continue-on-error: true
        uses: fabiocicerchia/carbon-budget-action@v1
        with:
          budget-gco2e: 5000
          hours: 720                      # 30d window
          track-budget: true
          burned-gco2e: ${{ steps.state.outputs.burned }}
          window-start: ${{ steps.state.outputs.window-start }}
          replicas: 4
          cpu-request: 500m
          memory-request: 1Gi

      - if: steps.budget.outcome == 'success'
        run: ./deploy.sh

      - if: always() && steps.budget.outputs.burned-gco2e != ''
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          echo '{"burned":"${{ steps.budget.outputs.burned-gco2e }}","window_start":"${{ steps.budget.outputs.window-start }}"}' > carbon-state.json
          gh extension install actions/gh-actions-cache 2>/dev/null || true
          gh actions-cache delete carbon-budget-state --confirm || true

      - if: always() && steps.budget.outputs.burned-gco2e != ''
        uses: actions/cache/save@v4
        with:
          path: carbon-state.json
          key: carbon-budget-state
```

## Outputs

| Output             | Description                                          |
| ------------------ | ----------------------------------------------------- |
| `estimated-gco2e`  | Estimated footprint in gCO2e                           |
| `within-budget`    | `true` / `false`                                       |
| `burned-gco2e`     | New window running total (`track-budget: true` only)   |
| `window-start`     | Window start to persist (`track-budget: true` only)    |

## Run locally

```sh
BUDGET_GCO2E=5000 REPLICAS=4 CPU_REQUEST=500m python carbon_budget.py
```
