@domain:budget-enforcement @area:budget-gate @from:carbon-budget-action/carbon-budget
Feature: Gating a deploy on its carbon budget
  Stops a CI job whose deployment would exceed its carbon budget, or only reports when the team chooses not to block.

  Background:
    Given the estimate for the deployment is 919 gCO2e
    And budget tracking is off

  @id:budget-enforcement.budget-gate.001 @rule:budget.gate.fail-over-budget @inferred @source:carbon_budget.py#main
  Scenario Outline: In gate mode a deploy over budget fails the job; at or under budget it passes
    Given the budget is <budget> gCO2e
    And the mode is gate
    When the pipeline runs the carbon budget check
    Then the step <result>
    And the within-budget output is <within>

    Examples:
      | budget | result                 | within |
      | 1000   | succeeds               | true   |
      | 919    | succeeds               | true   |
      | 900    | fails with exit code 1 | false  |

  @id:budget-enforcement.budget-gate.002 @rule:budget.gate.report-mode-never-fails @inferred @source:carbon_budget.py#main
  Scenario: In report mode a deploy over budget is reported but does not fail the job
    Given the budget is 900 gCO2e
    And the mode is report
    When the pipeline runs the carbon budget check
    Then the step succeeds
    And the within-budget output is false
    And the summary shows "❌ OVER BUDGET"
