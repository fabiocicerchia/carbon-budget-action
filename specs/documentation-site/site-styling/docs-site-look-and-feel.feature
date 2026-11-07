@domain:documentation-site @area:site-styling @from:docs/stylesheets
Feature: Documentation site look and feel
  Gives readers of the carbon-budget-action docs and splash page one consistent GreenOps-branded look that loads nothing from third parties.

  Background:
    Given the documentation site and the splash page are published

  @id:documentation-site.site-styling.001 @rule:docs.styling.shared-greenops-accent @inferred @source:docs/stylesheets/extra.css#:root
  Scenario: The docs and the splash page share the green GreenOps accent
    Given the project belongs to the GreenOps family
    When a reader opens the rendered docs and the splash page
    Then the links, primary buttons and home hero of the docs use the green accent pair #34d399 / #059669
    And the splash page uses the same accent pair
    And the light and dark colour schemes use the same accent pair

  @id:documentation-site.site-styling.002 @rule:docs.styling.no-third-party-requests @inferred @source:docs/stylesheets/extra.css#:root
  Scenario: Reading the docs fetches no web fonts or other third-party assets
    Given the reader's browser has its usual system fonts
    When a reader opens any documentation page
    Then the text is shown in the operating system's sans-serif font
    And code is shown in the operating system's monospace font
    And no font or stylesheet is downloaded from a third-party host

  @id:documentation-site.site-styling.003 @rule:docs.styling.no-stand-in-logo @inferred @source:docs/stylesheets/extra.css#.md-header__button.md-logo
  Scenario: The docs header shows no borrowed logo while the project has none
    Given the documentation has no project logo configured
    When a reader opens any documentation page
    Then the header shows the site title without a logo icon
    And the navigation title shows no logo icon

  @id:documentation-site.site-styling.004 @rule:docs.styling.wide-tables-readable-on-narrow-screens @inferred @source:docs/stylesheets/extra.css#.md-typeset table:not([class]) @questionable
  Scenario: Wide tables stay readable on narrow screens
    Given a documentation page contains a table wider than the screen
    When a reader opens that page on a narrow screen
    Then the table is shown as a rounded card with uppercase column headings
    And the reader can scroll the table sideways to see every column
