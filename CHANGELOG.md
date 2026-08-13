# Changelog

All notable changes to this project are documented here. The format is based
on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2](https://github.com/fabiocicerchia/carbon-budget-action/compare/v0.1.1...v0.1.2) (2026-08-13)


### Bug Fixes

* security and code-quality findings ([#29](https://github.com/fabiocicerchia/carbon-budget-action/issues/29)) ([c018bf6](https://github.com/fabiocicerchia/carbon-budget-action/commit/c018bf62fe4c6c34903b56f45d19b09d783dad93))

## [0.1.1](https://github.com/fabiocicerchia/carbon-budget-action/compare/v0.1.0...v0.1.1) (2026-08-06)


### Bug Fixes

* **pre-commit:** stop check-yaml failing on Helm templates and multi-doc manifests ([12247a3](https://github.com/fabiocicerchia/carbon-budget-action/commit/12247a398d80afde1c0ba00d00a242983fb84777))
* **security:** skip the SARIF upload on private repos ([9d3a8b2](https://github.com/fabiocicerchia/carbon-budget-action/commit/9d3a8b22916fdfacc4c1bbf8ecaaf76f1ec6372f))

## [Unreleased]

## [0.1.0] - 2026-07-14

### Added

- Composite action: carbon-footprint estimate, budget gate, job summary, and
  `estimated-gco2e` / `within-budget` outputs.
- `mode: report` to post the estimate without failing the build.
