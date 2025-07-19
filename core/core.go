package core

import (
	"fmt"
)

// Version is the semantic version for the YASL CLI.
const Version = "v0.0.2"

func SanitizePath(path string) (string, error) {
	// Example sanitization logic: ensure no special characters or invalid paths
	if len(path) == 0 || path[0] == '-' {
		return "", fmt.Errorf("invalid file path: %s", path)
	}
	return path, nil
}
