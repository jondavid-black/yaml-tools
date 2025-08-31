package main

import (
    "os"
    "path/filepath"
    "testing"
)

// helper to create a temp YAML file for testing
func writeTempYAML(t *testing.T, content string) string {
    t.Helper()
    tmpDir := t.TempDir()
    tmpFile := filepath.Join(tmpDir, "test.yaml")
    if err := os.WriteFile(tmpFile, []byte(content), 0644); err != nil {
        t.Fatalf("failed to write temp yaml: %v", err)
    }
    return tmpFile
}

func TestParse_SingleDocument(t *testing.T) {
    yaml := `
foo: bar
baz: 42
`
    file := writeTempYAML(t, yaml)
    docs, errs := parse(file)
    if len(errs) != 0 {
        t.Fatalf("unexpected errors: %v", errs)
    }
    if len(docs) != 1 {
        t.Fatalf("expected 1 document, got %d", len(docs))
    }
    keys := getRootKeys(docs[0])
    if len(keys) != 2 || keys[0] != "foo" && keys[1] != "baz" && keys[0] != "baz" && keys[1] != "foo" {
        t.Errorf("unexpected root keys: %v", keys)
    }
}

func TestParse_MultipleDocuments(t *testing.T) {
    yaml := `
foo: bar
---
- a
- b
- c
---
number: 123
`
    file := writeTempYAML(t, yaml)
    docs, errs := parse(file)
    if len(errs) != 0 {
        t.Fatalf("unexpected errors: %v", errs)
    }
    if len(docs) != 3 {
        t.Fatalf("expected 3 documents, got %d", len(docs))
    }
    if keys := getRootKeys(docs[1]); len(keys) != 1 || keys[0] != "<root is a list>" {
        t.Errorf("expected root to be a list, got: %v", keys)
    }
}

func TestParse_StrictInvalidYAML(t *testing.T) {
    yaml := `
foo: bar
But this is not valid YAML
So we should see an error
baz: 42
`
    file := writeTempYAML(t, yaml)
    docs, errs := parse(file)
    if len(errs) == 0 {
        t.Fatal("expected error for invalid YAML, got none")
    }
    if len(docs) != 0 {
        t.Errorf("expected no documents, got %d", len(docs))
    }
}

func TestParse_InvalidYAML(t *testing.T) {
    yaml := `
foo: bar
baz: [unclosed
`
    file := writeTempYAML(t, yaml)
    docs, errs := parse(file)
    if len(errs) == 0 {
        t.Fatal("expected error for invalid YAML, got none")
    }
    if len(docs) != 0 {
        t.Errorf("expected no documents, got %d", len(docs))
    }
}

func TestParse_CommentedYAML(t *testing.T) {
    yaml := `
# This is a comment
foo: bar
# Another comment
baz: 42
`
    file := writeTempYAML(t, yaml)
    docs, errs := parse(file)
    if len(errs) != 0 {
        t.Fatalf("unexpected errors: %v", errs)
    }
    if len(docs) != 1 {
        t.Fatalf("expected 1 document, got %d", len(docs))
    }
}

func TestParse_EmptyFile(t *testing.T) {
    file := writeTempYAML(t, "")
    docs, errs := parse(file)
    if len(errs) != 0 {
        t.Fatalf("unexpected errors: %v", errs)
    }
    if len(docs) != 0 {
        t.Errorf("expected 0 documents, got %d", len(docs))
    }
}

func TestParse_FileNotFound(t *testing.T) {
    docs, errs := parse("/nonexistent/file.yaml")
    if len(errs) == 0 {
        t.Fatal("expected error for missing file, got none")
    }
    if docs != nil {
        t.Errorf("expected nil docs, got %v", docs)
    }
}