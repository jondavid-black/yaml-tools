# features/example.feature
Feature: Basic YASL Schema Validation
  As a developer
  I want to validate YAML schemas
  So that I can ensure data integrity

  Scenario: Validating a simple YASL schema by specifying model name
    Given a YASL schema "features/data/person.yasl" is provided
    And a YAML document "features/data/person.yaml" is provided
    And the model name "person" is provided
    When I run the YASL CLI with provided arguments
    Then the validation should pass

Scenario: Validating a simple YASL schema without specifying model name
    Given a YASL schema "features/data/person.yasl" is provided
    And a YAML document "features/data/person.yaml" is provided
    When I run the YASL CLI with provided arguments
    Then the validation should pass

  Scenario: Validating a directory of YASL files
    Given a YASL schema "features/data/dir_test" is provided
    And a YAML document "features/data/dir_test" is provided
    When I run the YASL CLI with provided arguments
    Then the validation should pass

  Scenario: Validating a bad directory of YASL files
    Given a YASL schema "features/data/bad_dir_test" is provided
    And a YAML document "features/data/bad_dir_test" is provided
    When I run the YASL CLI with provided arguments
    Then the validation should fail