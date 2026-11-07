@domain:carbon-estimation @area:operational-emissions @from:carbon-budget-action/carbon-budget
Feature: Estimating operational emissions
  Gives teams an explainable figure for the energy-use footprint of one deploy cycle so a budget can be set against it.

  Background:
    Given no live intensity source and no embodied carbon are configured

  @id:carbon-estimation.operational-emissions.001 @rule:carbon.operational.power-model-estimate @verified @source:carbon_budget.py#estimate_gco2e @test:tests/test_carbon_budget.py#test_estimate_scales_linearly_with_replicas
  Scenario Outline: The estimate is power drawn by the replicas over the run, scaled by PUE and grid intensity
    Given the deployment runs <replicas> replica(s) of 1 CPU and 1G memory
    And it runs for <hours> hours on a grid of <intensity> gCO2e/kWh
    When the pipeline runs the carbon budget check
    Then the estimated-gco2e output is <estimate>
    And the summary's assumptions end with "grid <intensity>.0 gCO2e/kWh, PUE 1.2."

    Examples:
      | replicas | hours | intensity | estimate |
      | 1        | 720   | 480       | 1825     |
      | 3        | 720   | 480       | 5474     |
      | 1        | 360   | 480       | 912      |
      | 1        | 720   | 100       | 380      |

  @id:carbon-estimation.operational-emissions.002 @rule:carbon.operational.default-workload @inferred @source:carbon_budget.py#main
  Scenario: With only a budget configured, the estimate prices one small replica for a month at the world-average grid
    Given only the budget is configured
    When the pipeline runs the carbon budget check
    Then the summary's assumptions read "1 replica(s) × (500m CPU, 512Mi) × 720.0h, grid 480.0 gCO2e/kWh, PUE 1.2."
    And the estimated-gco2e output is 919
