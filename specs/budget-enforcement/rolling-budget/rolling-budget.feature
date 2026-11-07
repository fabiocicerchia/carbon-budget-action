@domain:budget-enforcement @area:rolling-budget @from:carbon-budget-action/carbon-budget
Feature: Tracking a rolling carbon budget
  Lets operators apply one budget to all deploys in a window, error-budget style, carrying the burn between runs without the action storing state.

  Background:
    Given track-budget is true
    And the budget is 5000 gCO2e
    And hours is 720
    And this deploy's estimate is 919 gCO2e

  @id:budget-enforcement.rolling-budget.001 @rule:budget.rolling.running-total-gated @verified @source:carbon_budget.py#emit_results @test:tests/test_carbon_budget.py#test_rollover_burn_carries_forward_within_window @test:tests/test_carbon_budget.py#test_render_shows_window_burn_status @questionable
  Scenario Outline: Within an open window the budget applies to the burned total plus this deploy
    Given burned-gco2e is <burned>
    And window-start is 100 hours ago
    When the pipeline runs the carbon budget check
    Then the within-budget output is <within>
    And the burned-gco2e output is <burned_out>
    And the window-start output is unchanged
    And the summary shows "Window burn: **<total> gCO2e** / budget 5,000 gCO2e" and "<status>"

    Examples:
      | burned | within | burned_out | total | status             |
      | 3000   | true   | 3919       | 3,919 | ✅ within budget    |
      | 4500   | false  | 4500       | 5,419 | ❌ BUDGET EXHAUSTED |

  @id:budget-enforcement.rolling-budget.002 @rule:budget.rolling.window-rollover @verified @source:carbon_budget.py#rollover_burn @test:tests/test_carbon_budget.py#test_rollover_burn_resets_once_window_elapsed @test:tests/test_carbon_budget.py#test_rollover_burn_no_window_start_starts_fresh
  Scenario Outline: Once the window has elapsed, or none was given, the burn starts over at zero
    Given burned-gco2e is 4500
    And window-start is <window_start>
    When the pipeline runs the carbon budget check
    Then the within-budget output is true
    And the burned-gco2e output is 919
    And the window-start output is the current time

    Examples:
      | window_start  |
      | 800 hours ago |
      | empty         |
