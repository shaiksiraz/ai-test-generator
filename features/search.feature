
Feature: Playwright Documentation Search
  As a developer
  I want to use the search modal
  So that I can quickly find information about locators
  @stable
  Scenario: User searches for locators successfully
    Given I navigate to "https://playwright.dev"
    When I click the Search button to open the modal
    And I fill the search input with 'locators'
    And I press Enter
    Then I verify the url contains 'locators'
