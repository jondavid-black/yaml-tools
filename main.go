package main

import (
	"flag"
	"fmt"
	"github.com/jondavid-black/YASL/utils"
	"os"
)

func main() {
	yamlFlag := flag.String("yaml", "", "Path to the YAML file")
	yaslFlag := flag.String("yasl", "", "Path to the YASL file")
	flag.Parse()

	var yamlPath, yaslPath string

	// If flags are provided, use them. Otherwise, use positional arguments.
	if *yamlFlag != "" && *yaslFlag != "" {
		yamlPath = *yamlFlag
		yaslPath = *yaslFlag
	} else {
		args := flag.Args()
		if len(args) < 2 {
			fmt.Fprintln(os.Stderr, "Usage: ./YASL <file.yaml> <file.yasl> OR ./YASL -yaml <file.yaml> -yasl <file.yasl>")
			os.Exit(1)
		}
		yamlPath = args[0]
		yaslPath = args[1]
	}

	// Check if files exist
	if _, err := os.Stat(yamlPath); os.IsNotExist(err) {
		fmt.Fprintf(os.Stderr, "YAML file not found: %s\n", yamlPath)
		os.Exit(1)
	}
	if _, err := os.Stat(yaslPath); os.IsNotExist(err) {
		fmt.Fprintf(os.Stderr, "YASL file not found: %s\n", yaslPath)
		os.Exit(1)
	}

	// Sanitize inputs to prevent potential security issues
	yamlPath = utils.SanitizePath(yamlPath)
	yaslPath = utils.SanitizePath(yaslPath)

	fmt.Println("OK - ", yamlPath, ", ", yaslPath)
}
