# Error-Budget Example

What it shows: gate a *deploy* step (not a PR check) on a running carbon
total for a 30-day window, SRE-error-budget style — once the window's
`budget-gco2e` is burned, the deploy step is skipped until the window
resets. Blocking a PR doesn't stop what's already running, so this targets
the pipeline that would add more footprint, not the running workload.

The action keeps no state of its own: `burned-gco2e` / `window-start` are
this action's own outputs from the previous run, fed back in as inputs.
This example persists them in the Actions cache (no repo commits, no extra
token) using the restore+delete+save workaround for `actions/cache` having
no key-overwrite. See
[docs/getting-started.md](../../docs/getting-started.md#error-budget-mode-track-budget)
for the caveats (7-day cache eviction, run concurrency).

## Run

Drop this into `.github/workflows/deploy.yml`:

```yaml
name: deploy

on:
  push:
    branches: [main]

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

Under `mode: report` (never fails), the `outcome == 'success'` check on the
deploy step always passes — check
`steps.budget.outputs.within-budget == 'true'` instead.
