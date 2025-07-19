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
	if len(output) < 2 || string(output[:2]) != "OK" {
		t.Errorf("Expected output to start with 'OK', got: %s", output)
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
	if len(output) < 2 || string(output[:2]) != "OK" {
		t.Errorf("Expected output to start with 'OK', got: %s", output)
	}
}

func TestYASL_CLI_MissingFiles(t *testing.T) {
	cmd := exec.Command("./yasl", "missing.yaml", "missing.yasl")
	cmd.Env = append(os.Environ(), "GO_WANT_HELPER_PROCESS=1")
	output, err := cmd.CombinedOutput()
	if err == nil {
		t.Fatalf("Expected error for missing files, got none. Output: %s", output)
	}
}
