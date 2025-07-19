package core

import (
	"testing"
)

func TestSanitizePath_Valid(t *testing.T) {
	valid := "file.yaml"
	result, err := SanitizePath(valid)
	if err != nil {
		t.Fatalf("Expected no error, got %v", err)
	}
	if result != valid {
		t.Errorf("Expected %s, got %s", valid, result)
	}
}

func TestSanitizePath_Invalid(t *testing.T) {
	_, err := SanitizePath("")
	if err == nil {
		t.Errorf("Expected error for empty path, got nil")
	}
}

func TestSanitizePath_DashPrefix(t *testing.T) {
	_, err := SanitizePath("-badfile.yaml")
	if err == nil {
		t.Errorf("Expected error for dash-prefixed path, got nil")
	}
}
