@domain:carbon-estimation @area:workload-sizing @from:carbon-budget-action/carbon-budget
Feature: Sizing the workload to estimate
  Lets a team describe the deployment once — as inputs or as the Kubernetes manifest they already ship — so the estimate prices what will actually run.

  Background:
    Given the budget is 100000 gCO2e
    And the grid intensity is 480 gCO2e/kWh and no live intensity source is configured

  @id:carbon-estimation.workload-sizing.001 @rule:carbon.workload.manifest-overrides-inputs @verified @source:carbon_budget.py#parse_manifest @test:tests/test_carbon_budget.py#test_parse_manifest_reads_replicas_and_first_container_requests @test:tests/test_carbon_budget.py#test_parse_manifest_missing_fields_return_empty_dict
  Scenario Outline: A manifest's replicas and resource requests replace the sizing inputs
    Given the replicas input is 1, cpu-request is 500m and memory-request is 512Mi
    And manifest-path points at a Deployment with <manifest_content>
    When the pipeline runs the carbon budget check
    Then the summary's assumptions read "<assumptions>"

    Examples:
      | manifest_content                                                    | assumptions                               |
      | replicas 4 and a first container requesting cpu 250m and memory 1Gi | 4 replica(s) × (250m CPU, 1Gi) × 720.0h   |
      | replicas 3 and no resource requests                                 | 3 replica(s) × (500m CPU, 512Mi) × 720.0h |
      | no replicas and no resource requests (e.g. a ConfigMap)             | 1 replica(s) × (500m CPU, 512Mi) × 720.0h |

  @id:carbon-estimation.workload-sizing.002 @rule:carbon.workload.kubernetes-quantity-units @verified @source:carbon_budget.py#parse_cpu @test:tests/test_carbon_budget.py#test_parsers
  Scenario Outline: CPU and memory requests are read in Kubernetes quantity units
    Given the workload runs 1 replica for 720 hours
    And cpu-request is <cpu> and memory-request is <memory>
    When the pipeline runs the carbon budget check
    Then the estimated-gco2e output is <estimate>

    Examples:
      | cpu  | memory | estimate |
      | 500m | 512Mi  | 919      |
      | 1    | 1G     | 1825     |
      | 0.5  | 512Mi  | 919      |
