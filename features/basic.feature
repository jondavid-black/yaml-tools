# features/example.feature
Feature: Basic YASL Schema Validation
  As a developer
  I want to validate YAML schemas
  So that I can ensure data integrity

  Scenario: Validating a simple YASL schema
    Given a YASL schema "data/basic.yasl" is defined
    And a YAML document "data/basic.yaml" is given
    When I validate the document against the schema
    Then the validation should pass