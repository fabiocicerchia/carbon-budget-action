@domain:reporting @area:action-outputs @from:carbon-budget-action/carbon-budget
Feature: Publishing the result as step outputs
  Lets later workflow steps act on the estimate and verdict, and persist the burn for the next run.

  Background:
    Given the estimate is 918.5 gCO2e and the budget is 1000 gCO2e

  @id:reporting.action-outputs.001 @rule:reporting.outputs.estimate-and-verdict @inferred @source:carbon_budget.py#emit_results
  Scenario Outline: Every run publishes the rounded estimate and the verdict; burn outputs only when tracking
    Given track-budget is <tracking>
    When the pipeline runs the carbon budget check
    Then the estimated-gco2e output is 919
    And the within-budget output is true
    And burned-gco2e and window-start outputs are <burn_outputs>

    Examples:
      | tracking | burn_outputs |
      | false    | not set      |
      | true     | set          |
