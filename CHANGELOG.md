# Changelog

All notable changes to this project are documented here. The format is based
on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0](https://github.com/fabiocicerchia/carbon-budget-action/compare/v0.2.0...v0.3.0) (2026-08-25)


### Features

* **docs:** build the docs site in Actions and drop Read the Docs ([#37](https://github.com/fabiocicerchia/carbon-budget-action/issues/37)) ([9a4416b](https://github.com/fabiocicerchia/carbon-budget-action/commit/9a4416b4a5f9657157b03292b36665453f86bbee))

## [0.2.0](https://github.com/fabiocicerchia/carbon-budget-action/compare/v0.1.2...v0.2.0) (2026-08-15)


### Features

* add ci-api-area, a keyless live grid-intensity source ([#31](https://github.com/fabiocicerchia/carbon-budget-action/issues/31)) ([6d77163](https://github.com/fabiocicerchia/carbon-budget-action/commit/6d77163c09879297ecd56f93affb821c93e64d39))

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
