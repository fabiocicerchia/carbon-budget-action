@domain:grid-intensity @area:electricity-maps @from:carbon-budget-action/carbon-budget
Feature: Choosing the grid intensity to price with
  Lets teams price a deploy with live grid data when they have it, without ever failing the gate because a data source is down.

  Background:
    Given grid-intensity is set to 300 gCO2e/kWh

  @id:grid-intensity.electricity-maps.001 @rule:grid.source.precedence-and-fallback @verified @source:carbon_budget.py#resolve_grid_intensity @test:tests/test_carbon_budget.py#test_fetch_live_intensity_returns_value_on_success @test:tests/test_carbon_budget.py#test_fetch_live_intensity_falls_back_to_none_on_error @test:tests/test_carbon_budget.py#test_ci_api_failure_falls_back_to_the_static_input
  Scenario Outline: Electricity Maps is preferred, then the carbon intensity API, then the configured grid intensity
    Given Electricity Maps is <em_setup>
    And ci-api-area is <ci_area> and the carbon intensity API <ci_state>
    When the pipeline runs the carbon budget check
    Then the estimate is priced at <priced> gCO2e/kWh

    Examples:
      | em_setup                                            | ci_area | ci_state       | priced |
      | configured with zone FR and a token and reports 42  | IT      | reports 384    | 42     |
      | configured with zone FR and a token but unreachable | IT      | reports 384    | 384    |
      | given a zone but no token                           | IT      | reports 384    | 384    |
      | configured with zone FR and a token but unreachable | empty   | —              | 300    |
      | not configured                                      | IT      | is unreachable | 300    |
      | not configured                                      | empty   | —              | 300    |
