# features/example.feature
Feature: Basic YASL Schema Validation
  As a developer
  I want to validate YAML schemas
  So that I can ensure data integrity

  Scenario: Validating a simple YASL schema
    Given a YASL schema "data/person.yasl" is defined
    And a YAML document "data/person.yaml" is given
    And the model name "person" is specified
    When I validate the document against the schema
    Then the validation should pass