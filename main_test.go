package main

import (
	"os"
	"os/exec"
	"testing"

	"github.com/jondavid-black/YASL/utils"
)

func TestMain_CLI_PositionalArgs(t *testing.T) {
	// Create temp files to simulate YAML and YASL files
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

	// Sanitize inputs to prevent potential security issues
	cmd := exec.Command("./yasl", utils.SanitizePath(yamlFile.Name()), utils.SanitizePath(yaslFile.Name())) // #nosec
	cmd.Env = append(os.Environ(), "GO_WANT_HELPER_PROCESS=1")
	output, err := cmd.CombinedOutput()
	if err != nil {
		t.Fatalf("Expected success, got error: %v, output: %s", err, output)
	}
	if len(output) < 2 || string(output[:2]) != "OK" {
		t.Errorf("Expected output to start with 'OK', got: %s", output)
	}
}

func TestMain_CLI_Flags(t *testing.T) {
	// Create temp files to simulate YAML and YASL files
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

	// Sanitize inputs to prevent potential security issues
	cmd := exec.Command("./yasl", "-yaml", utils.SanitizePath(yamlFile.Name()), "-yasl", utils.SanitizePath(yaslFile.Name())) // #nosec
	cmd.Env = append(os.Environ(), "GO_WANT_HELPER_PROCESS=1")
	output, err := cmd.CombinedOutput()
	if err != nil {
		t.Fatalf("Expected success, got error: %v, output: %s", err, output)
	}
	if len(output) < 2 || string(output[:2]) != "OK" {
		t.Errorf("Expected output to start with 'OK', got: %s", output)
	}
}

func TestMain_CLI_MissingFiles(t *testing.T) {
	cmd := exec.Command("./yasl", "missing.yaml", "missing.yasl")
	cmd.Env = append(os.Environ(), "GO_WANT_HELPER_PROCESS=1")
	output, err := cmd.CombinedOutput()
	if err == nil {
		t.Fatalf("Expected error for missing files, got none. Output: %s", output)
	}
}
