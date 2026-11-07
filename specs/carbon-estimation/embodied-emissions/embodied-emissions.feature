@domain:carbon-estimation @area:embodied-emissions @from:carbon-budget-action/carbon-budget
Feature: Including embodied hardware emissions
  Lets teams account for the manufacturing footprint of the servers they occupy, not only the electricity they draw.

  Background:
    Given the deployment runs 2 replicas for 720 hours

  @id:carbon-estimation.embodied-emissions.001 @rule:carbon.embodied.amortized-over-lifetime @verified @source:carbon_budget.py#amortized_embodied_gco2e @test:tests/test_carbon_budget.py#test_amortized_embodied_gco2e_scales_with_hours_and_replicas @test:tests/test_carbon_budget.py#test_render_shows_embodied_line
  Scenario: Embodied carbon is added in proportion to run hours over the hardware lifetime
    Given embodied-gco2e is 40000 per replica's server
    And embodied-lifetime-years is 4
    When the pipeline runs the carbon budget check
    Then 1644 gCO2e of embodied carbon is added to the estimate
    And the summary says "Includes 1,644 gCO2e amortized embodied carbon."

  @id:carbon-estimation.embodied-emissions.002 @rule:carbon.embodied.off-unless-configured @verified @source:carbon_budget.py#amortized_embodied_gco2e @test:tests/test_carbon_budget.py#test_amortized_embodied_gco2e_zero_when_not_configured
  Scenario Outline: No embodied carbon is counted when it or its lifetime is zero
    Given embodied-gco2e is <embodied> and embodied-lifetime-years is <years>
    When the pipeline runs the carbon budget check
    Then the estimate contains operational emissions only
    And the summary has no embodied-carbon line

    Examples:
      | embodied | years |
      | 0        | 4     |
      | 1000     | 0     |
