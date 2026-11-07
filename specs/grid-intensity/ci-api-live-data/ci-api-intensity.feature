@domain:grid-intensity @area:ci-api-live-data @from:carbon-budget-action/carbon-budget
Feature: Pricing with the public carbon intensity API
  Gives teams credential-free live grid intensity per country or bidding zone, while refusing data too old to trust.

  Background:
    Given grid-intensity is set to 300 gCO2e/kWh
    And Electricity Maps is not configured

  @id:grid-intensity.ci-api-live-data.001 @rule:grid.ci-api.most-complete-figure @verified @source:carbon_budget.py#fetch_ci_api_intensity @test:tests/test_carbon_budget.py#test_ci_api_reports_consumption_lifecycle @test:tests/test_carbon_budget.py#test_ci_api_zone_falls_back_to_lifecycle
  Scenario Outline: A country is priced at its consumption lifecycle intensity and a zone at its lifecycle intensity
    Given the carbon intensity API publishes a fresh measured reading for <area>
    When the pipeline runs the carbon budget check with ci-api-area <area>
    Then the estimate is priced at <priced> gCO2e/kWh
    And the log says "carbon-budget: <area> at <priced> gCO2e/kWh (measured) from ci-api.fabiocicerchia.it"

    Examples:
      | area    | priced |
      | IT      | 384    |
      | IT/SICI | 456    |

  @id:grid-intensity.ci-api-live-data.002 @rule:grid.ci-api.zone-falls-back-to-country @verified @source:carbon_budget.py#_ci_api_payload @test:tests/test_carbon_budget.py#test_ci_api_zone_404_asks_the_country_after_waiting_out_the_rate_limit
  Scenario: A zone without a reading for the hour is priced at its country's intensity
    Given the carbon intensity API has no reading for zone IT/SICI this hour
    And it publishes a fresh reading of 384 gCO2e/kWh for IT
    When the pipeline runs the carbon budget check with ci-api-area IT/SICI
    Then the check waits 10 seconds before asking for the country
    And the estimate is priced at 384 gCO2e/kWh

  @id:grid-intensity.ci-api-live-data.003 @rule:grid.ci-api.stale-measurement-refused @verified @source:carbon_budget.py#_reading_is_fresh @test:tests/test_carbon_budget.py#test_ci_api_refuses_a_stale_measurement @test:tests/test_carbon_budget.py#test_ci_api_reports_consumption_lifecycle
  Scenario Outline: A measured reading older than 65 minutes is not used
    Given the carbon intensity API's latest measured reading for IT was generated <age> ago
    When the pipeline runs the carbon budget check with ci-api-area IT
    Then the estimate is priced at <priced> gCO2e/kWh

    Examples:
      | age        | priced |
      | 10 minutes | 384    |
      | 75 minutes | 300    |

  @id:grid-intensity.ci-api-live-data.004 @rule:grid.ci-api.annual-average-accepted @verified @source:carbon_budget.py#fetch_ci_api_intensity @test:tests/test_carbon_budget.py#test_ci_api_accepts_an_annual_average_and_names_it
  Scenario: An annual-average reading is used regardless of age and named as such
    Given the carbon intensity API publishes only a six-day-old annual average of 510 gCO2e/kWh for MX
    When the pipeline runs the carbon budget check with ci-api-area MX
    Then the estimate is priced at 510 gCO2e/kWh
    And the log says "carbon-budget: MX at 510 gCO2e/kWh (annual-average) from ci-api.fabiocicerchia.it"
