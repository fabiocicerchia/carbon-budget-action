@domain:ci-integrations @area:devtron @from:examples/ci-platforms
Feature: Gating a Devtron deployment on its carbon budget
  Lets a platform operator stop a Devtron CD stage before a deployment that would go over its carbon budget, using a pasted shell task with no extra setup.

  Background:
    Given the operator has added the carbon budget shell task to the Pre-Deployment stage of a Devtron CD pipeline

  @id:ci-integrations.devtron.001 @rule:ci.devtron.rendered-chart-sizes-workload @inferred @source:carbon_budget.py#main
  Scenario: A rendered Helm chart sizes the workload instead of the task figures
    Given the operator points MANIFEST_PATH at a rendered Deployment with 3 replicas requesting 250m CPU and 768Mi memory
    And the task's replica, CPU and memory figures are left at 4, 500m and 1Gi
    When the pre-deployment task runs
    Then the report shows 3 replicas at 250m CPU and 768Mi memory
    And the verdict is judged on that rendered workload
