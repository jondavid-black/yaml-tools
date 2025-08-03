package main

import (
	"github.com/jondavid-black/YASL/core"
	"os"
	"os/exec"
	"testing"
)

func TestYASL_CLI_PositionalArgs(t *testing.T) {
	yamlFile, err := os.CreateTemp("", "test-*.yaml")
	if err != nil {
		t.Fatalf("Failed to create temp YAML file: %v", err)
	}
	defer os.Remove(yamlFile.Name())
	yamlFile.Close()
	yaslFile, err := os.CreateTemp("", "test-*.yasl")
	if err != nil {
		t.Fatalf("Failed to create temp YASL file: %v", err)
	}
	defer os.Remove(yaslFile.Name())
	yaslFile.Close()

	yamlPath, err := core.SanitizePath(yamlFile.Name())
	if err != nil {
		t.Fatalf("SanitizePath failed for yaml: %v", err)
	}
	yaslPath, err := core.SanitizePath(yaslFile.Name())
	if err != nil {
		t.Fatalf("SanitizePath failed for yasl: %v", err)
	}
	cmd := exec.Command("./yasl", yamlPath, yaslPath) // #nosec
	cmd.Env = append(os.Environ(), "GO_WANT_HELPER_PROCESS=1")
	output, err := cmd.CombinedOutput()
	if err != nil {
		t.Fatalf("Expected success, got error: %v, output: %s", err, output)
	}
	if !containsOKText(string(output)) {
		t.Errorf("Expected plain text output with '✅ YASL processing complete', got: %s", output)
	}
}

func TestYASL_CLI_Flags(t *testing.T) {
	yamlFile, err := os.CreateTemp("", "test-*.yaml")
	if err != nil {
		t.Fatalf("Failed to create temp YAML file: %v", err)
	}
	defer os.Remove(yamlFile.Name())
	yamlFile.Close()
	yaslFile, err := os.CreateTemp("", "test-*.yasl")
	if err != nil {
		t.Fatalf("Failed to create temp YASL file: %v", err)
	}
	defer os.Remove(yaslFile.Name())
	yaslFile.Close()

	yamlPath, err := core.SanitizePath(yamlFile.Name())
	if err != nil {
		t.Fatalf("SanitizePath failed for yaml: %v", err)
	}
	yaslPath, err := core.SanitizePath(yaslFile.Name())
	if err != nil {
		t.Fatalf("SanitizePath failed for yasl: %v", err)
	}
	cmd := exec.Command("./yasl", "-yaml", yamlPath, "-yasl", yaslPath) // #nosec
	cmd.Env = append(os.Environ(), "GO_WANT_HELPER_PROCESS=1")
	output, err := cmd.CombinedOutput()
	if err != nil {
		t.Fatalf("Expected success, got error: %v, output: %s", err, output)
	}
	if !containsOKText(string(output)) {
		t.Errorf("Expected plain text output with '✅ YASL processing complete', got: %s", output)
	}
}

func TestYASL_CLI_OutputType_Text(t *testing.T) {
	yamlFile, err := os.CreateTemp("", "test-*.yaml")
	if err != nil {
		t.Fatalf("Failed to create temp YAML file: %v", err)
	}
	defer os.Remove(yamlFile.Name())
	yamlFile.Close()
	yaslFile, err := os.CreateTemp("", "test-*.yasl")
	if err != nil {
		t.Fatalf("Failed to create temp YASL file: %v", err)
	}
	defer os.Remove(yaslFile.Name())
	yaslFile.Close()

	yamlPath, err := core.SanitizePath(yamlFile.Name())
	if err != nil {
		t.Fatalf("SanitizePath failed for yaml: %v", err)
	}
	yaslPath, err := core.SanitizePath(yaslFile.Name())
	if err != nil {
		t.Fatalf("SanitizePath failed for yasl: %v", err)
	}
	cmd := exec.Command("./yasl", yamlPath, yaslPath, "--output-type", "text")
	output, err := cmd.CombinedOutput()
	if err != nil {
		t.Fatalf("Expected success, got error: %v, output: %s", err, output)
	}
	if !containsOKText(string(output)) {
		t.Errorf("Expected plain text output with '✅ YASL processing complete', got: %s", output)
	}
}

func TestYASL_CLI_OutputType_JSON(t *testing.T) {
	yamlFile, err := os.CreateTemp("", "test-*.yaml")
	if err != nil {
		t.Fatalf("Failed to create temp YAML file: %v", err)
	}
	defer os.Remove(yamlFile.Name())
	yamlFile.Close()
	yaslFile, err := os.CreateTemp("", "test-*.yasl")
	if err != nil {
		t.Fatalf("Failed to create temp YASL file: %v", err)
	}
	defer os.Remove(yaslFile.Name())
	yaslFile.Close()

	yamlPath, err := core.SanitizePath(yamlFile.Name())
	if err != nil {
		t.Fatalf("SanitizePath failed for yaml: %v", err)
	}
	yaslPath, err := core.SanitizePath(yaslFile.Name())
	if err != nil {
		t.Fatalf("SanitizePath failed for yasl: %v", err)
	}
	cmd := exec.Command("./yasl", "--output-type", "json", yamlPath, yaslPath)
	output, err := cmd.CombinedOutput()
	if err != nil {
		t.Fatalf("Expected success, got error: %v, output: %s", err, output)
	}
	if !containsJSONLog(string(output)) {
		t.Errorf("Expected JSON log output, got: %s", output)
	}
}

func TestYASL_CLI_OutputType_YAML(t *testing.T) {
	yamlFile, err := os.CreateTemp("", "test-*.yaml")
	if err != nil {
		t.Fatalf("Failed to create temp YAML file: %v", err)
	}
	defer os.Remove(yamlFile.Name())
	yamlFile.Close()
	yaslFile, err := os.CreateTemp("", "test-*.yasl")
	if err != nil {
		t.Fatalf("Failed to create temp YASL file: %v", err)
	}
	defer os.Remove(yaslFile.Name())
	yaslFile.Close()

	yamlPath, err := core.SanitizePath(yamlFile.Name())
	if err != nil {
		t.Fatalf("SanitizePath failed for yaml: %v", err)
	}
	yaslPath, err := core.SanitizePath(yaslFile.Name())
	if err != nil {
		t.Fatalf("SanitizePath failed for yasl: %v", err)
	}
	cmd := exec.Command("./yasl", "--output-type", "yaml", yamlPath, yaslPath)
	output, err := cmd.CombinedOutput()
	if err != nil {
		t.Fatalf("Expected success, got error: %v, output: %s", err, output)
	}
	if !containsYAMLLog(string(output)) {
		t.Errorf("Expected YAML log output, got: %s", output)
	}
}

// Helper functions for log output checks
func containsOKText(out string) bool {
	// Should contain '✅ YASL processing complete.' and not look like JSON or YAML
	return len(out) > 0 && contains(out, "✅ YASL processing complete.")
}

func containsJSONLog(out string) bool {
	// Should contain JSON keys: "time", "level", "msg"
	return (len(out) > 0 &&
		(contains(out, "\"time\"") && contains(out, "\"level\"") && contains(out, "\"msg\"")))
}

func containsYAMLLog(out string) bool {
	// Should contain YAML keys: time:, level:, msg:
	return (len(out) > 0 &&
		contains(out, "time:") && contains(out, "level:") && contains(out, "msg:"))
}

func contains(s, substr string) bool {
	return len(s) > 0 && len(substr) > 0 && (stringIndex(s, substr) >= 0)
}

func stringIndex(s, substr string) int {
	for i := 0; i+len(substr) <= len(s); i++ {
		if s[i:i+len(substr)] == substr {
			return i
		}
	}
	return -1
}
