# Basic Example

What it shows: gate a pull request on a per-deploy carbon budget.

## Run

Drop this into `.github/workflows/carbon.yml`:

```yaml
name: carbon budget
on: [pull_request]

jobs:
  carbon:
    runs-on: ubuntu-latest
    steps:
      - uses: fabiocicerchia/carbon-budget-action@v1
        with:
          budget-gco2e: 5000
          replicas: 4
          cpu-request: 500m
          memory-request: 1Gi
          grid-intensity: 56   # eu-north-1; default 480 (world avg)
```

Switch to `mode: report` to see the estimate on every PR without failing the
build.
