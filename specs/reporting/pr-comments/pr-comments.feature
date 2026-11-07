@domain:reporting @area:pr-comments @from:carbon-budget-action/carbon-budget
Feature: Commenting the result on the pull request
  Puts the carbon check where reviewers already look, as one comment that stays current across re-runs.

  Background:
    Given pr-comment is true
    And a github-token is provided
    And the run is for pull request #42

  @id:reporting.pr-comments.001 @rule:reporting.pr-comment.single-updated-comment @verified @source:carbon_budget.py#upsert_pr_comment @test:tests/test_carbon_budget.py#test_upsert_pr_comment_patches_existing_marker_comment
  Scenario Outline: Re-runs update the action's existing pull request comment instead of adding another
    Given pull request #42 <existing>
    When the pipeline runs the carbon budget check
    Then <outcome>
    And the comment body is the job summary, preceded by the hidden marker "<!-- carbon-budget-action -->"

    Examples:
      | existing                               | outcome                         |
      | already has a comment from this action | that comment is edited in place |
      | has no comment from this action        | a new comment is posted         |

  @id:reporting.pr-comments.002 @rule:reporting.pr-comment.skipped-without-prerequisites @verified @source:carbon_budget.py#post_pr_comment @test:tests/test_carbon_budget.py#test_find_pr_number_missing_path_returns_none
  Scenario Outline: No comment is attempted unless commenting is on and a token, repository and pull request are known
    Given <missing>
    When the pipeline runs the carbon budget check
    Then no pull request comment is posted
    And the budget verdict and exit status are unaffected

    Examples:
      | missing                           |
      | pr-comment is false               |
      | github-token is empty             |
      | the run is not for a pull request |

  @id:reporting.pr-comments.003 @rule:reporting.pr-comment.failure-only-warns @inferred @source:carbon_budget.py#post_pr_comment
  Scenario: A comment that fails to post raises a warning but never fails the check
    Given the budget is met
    And GitHub rejects the comment request
    When the pipeline runs the carbon budget check
    Then the run shows the warning "carbon-budget-action: failed to post PR comment: …"
    And the step succeeds
