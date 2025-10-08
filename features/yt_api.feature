Feature: YAML-TOOLS API Version Endpoint

  Scenario: Get the YAML-TOOLS version from the API
    Given the YAML-TOOLS API server is running using the "yt-serve" command
    When I run "curl http://localhost:5000/api/version"
    Then the response should contain a "version" field matching the pattern "\d+\.\d+\.\d+"