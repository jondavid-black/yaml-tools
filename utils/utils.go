package utils

import (
	"fmt"
	"os"
)

func SanitizePath(path string) string {
	// Example sanitization logic: ensure no special characters or invalid paths
	if len(path) == 0 || path[0] == '-' {
		fmt.Fprintf(os.Stderr, "Invalid file path: %s\n", path)
		os.Exit(1)
	}
	return path
}
