package core

import (
	"fmt"
)

func SanitizePath(path string) (string, error) {
	   // Example sanitization logic: ensure no special characters or invalid paths
	   if len(path) == 0 || path[0] == '-' {
			   return "", fmt.Errorf("invalid file path: %s", path)
	   }
	   return path, nil
}
