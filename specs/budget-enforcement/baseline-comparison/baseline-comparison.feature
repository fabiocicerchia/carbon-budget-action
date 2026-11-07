@domain:budget-enforcement @area:baseline-comparison @from:carbon-budget-action/carbon-budget
Feature: Comparing against the base branch
  Shows reviewers how a change moves the footprint relative to the base branch, like a bundle-size diff.

  Background:
    Given the budget is 2000 gCO2e

  @id:budget-enforcement.baseline-comparison.001 @rule:budget.baseline.delta-shown @verified @source:carbon_budget.py#render @test:tests/test_carbon_budget.py#test_render_shows_delta_against_base
  Scenario Outline: The summary shows the change in footprint against the base branch's estimate
    Given base-gco2e is <base>
    And this run estimates <estimate> gCO2e
    When the pipeline runs the carbon budget check
    Then the summary shows "Δ vs base: <delta>"

    Examples:
      | base | estimate | delta                |
      | 1000 | 1200     | ▲ +200 gCO2e (+20%)  |
      | 1500 | 1200     | ▼ -300 gCO2e (-20%)  |
      | 1200 | 1200     | ▬ +0 gCO2e (+0%)     |
      | 0    | 1200     | ▲ +1,200 gCO2e (+0%) |
