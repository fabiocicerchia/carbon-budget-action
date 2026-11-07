# Specifications of carbon-budget-action

What this code does, one atomic Gherkin scenario per behaviour, read from the code by code-atlas.
Tags: `@verified` a test asserts it · `@inferred` read from the code only · `@gap` an entry point no test covers · `@human` written or amended by a person, never rewritten.

## Budget enforcement
Deciding whether a deployment fits its carbon budget and failing CI when it does not.

- **Baseline comparison**: [Comparing against the base branch](budget-enforcement/baseline-comparison/baseline-comparison.feature) (1)
- **Budget gate**: [Gating a deploy on its carbon budget](budget-enforcement/budget-gate/budget-gate.feature) (2)
- **Rolling budget tracking**: [Tracking a rolling carbon budget](budget-enforcement/rolling-budget/rolling-budget.feature) (2)

## Carbon estimation
Turning a deployment's size and runtime into an explainable grams-of-CO2e figure.

- **Embodied emissions**: [Including embodied hardware emissions](carbon-estimation/embodied-emissions/embodied-emissions.feature) (2)
- **Operational emissions**: [Estimating operational emissions](carbon-estimation/operational-emissions/operational-emissions.feature) (2)
- **Workload sizing**: [Sizing the workload to estimate](carbon-estimation/workload-sizing/workload-sizing.feature) (2)

## CI platform integrations
Running the carbon gate outside GitHub Actions on other delivery platforms.

- **Devtron pre-deployment task**: [Gating a Devtron deployment on its carbon budget](ci-integrations/devtron/devtron-pre-deployment-gate.feature) (1)

## Documentation site
The published user documentation for the action.

- **Site styling**: [Documentation site look and feel](documentation-site/site-styling/docs-site-look-and-feel.feature) (4)

## Grid intensity
Choosing the carbon intensity of the electricity the workload runs on.

- **Carbon intensity API**: [Pricing with the public carbon intensity API](grid-intensity/ci-api-live-data/ci-api-intensity.feature) (4)
- **Electricity Maps live data**: [Choosing the grid intensity to price with](grid-intensity/electricity-maps/live-grid-intensity.feature) (1)

## Reporting
Communicating results to people and downstream workflow steps.

- **Action outputs**: [Publishing the result as step outputs](reporting/action-outputs/action-outputs.feature) (1)
- **Job summary**: [Reporting the check in the job summary](reporting/job-summary/job-summary.feature) (1)
- **Pull request comments**: [Commenting the result on the pull request](reporting/pr-comments/pr-comments.feature) (3)
