# Changelog

All notable changes to this project are documented here. The format is based
on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0](https://github.com/fabiocicerchia/carbon-budget-action/compare/v0.1.0...v0.2.0) (2026-07-29)


### Features

* embodied-carbon amortization option ([a276c95](https://github.com/fabiocicerchia/carbon-budget-action/commit/a276c95da14761750b3bbde207d697394c3915ee))
* error-budget mode via track-budget for cumulative window burn ([d8857a5](https://github.com/fabiocicerchia/carbon-budget-action/commit/d8857a57e6c44b2781dd10e954668a69e5fe798a))
* live grid intensity via Electricity Maps API ([bedbeca](https://github.com/fabiocicerchia/carbon-budget-action/commit/bedbeca757ed6335af0aefefd4534b61e41cf1c2))
* PR comment with delta vs base branch ([c021cae](https://github.com/fabiocicerchia/carbon-budget-action/commit/c021cae4b09249611a30a3bbd210db89363288de))
* read replicas/cpu/memory requests from a k8s manifest ([97e6e1b](https://github.com/fabiocicerchia/carbon-budget-action/commit/97e6e1b64a45c7df18c85a354b301f338b93d975))


### Bug Fixes

* align codeql-action versions, add missing release-please manifest, satisfy newer ruff rules ([#11](https://github.com/fabiocicerchia/carbon-budget-action/issues/11)) ([512b8a2](https://github.com/fabiocicerchia/carbon-budget-action/commit/512b8a2e5df83b08ef3bfd6e67439e8523f8fdf5))
* wire up the composite action's outputs (they never actually worked) ([188ffd6](https://github.com/fabiocicerchia/carbon-budget-action/commit/188ffd6252024b7f00e38eae39086300751408f8))

## [Unreleased]

## [0.1.0] - 2026-07-14

### Added

- Composite action: carbon-footprint estimate, budget gate, job summary, and
  `estimated-gco2e` / `within-budget` outputs.
- `mode: report` to post the estimate without failing the build.
