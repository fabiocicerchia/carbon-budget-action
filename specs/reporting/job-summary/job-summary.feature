@domain:reporting @area:job-summary @from:carbon-budget-action/carbon-budget
Feature: Reporting the check in the job summary
  Gives anyone looking at the CI run a readable verdict, usage bar and assumptions without digging into logs.

  @id:reporting.job-summary.001 @rule:reporting.summary.verdict-and-usage-bar @verified @source:carbon_budget.py#render @test:tests/test_carbon_budget.py#test_render_over_budget_flags
  Scenario Outline: The summary shows the estimate against the budget with a capped usage bar
    Given the budget is <budget> gCO2e
    And the estimate is <estimate> gCO2e
    When the pipeline runs the carbon budget check
    Then the job summary is headed "## 🌍 Carbon budget check"
    And it shows "Estimated: **<estimate_fmt> gCO2e** / budget <budget_fmt> gCO2e (<pct>) <status>"
    And the usage bar has <blocks> blocks

    Examples:
      | budget | estimate | estimate_fmt | budget_fmt | pct  | status          | blocks |
      | 2000   | 1000     | 1,000        | 2,000      | 50%  | ✅ within budget | 10     |
      | 1000   | 1200     | 1,200        | 1,000      | 120% | ❌ OVER BUDGET   | 20     |
      | 1000   | 9000     | 9,000        | 1,000      | 900% | ❌ OVER BUDGET   | 20     |
