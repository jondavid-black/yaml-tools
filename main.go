package main

import (
	"flag"
	"fmt"
	"github.com/jondavid-black/YASL/core"
	"os"
)

func main() {
	yamlFlag := flag.String("yaml", "", "Path to the YAML file")
	yaslFlag := flag.String("yasl", "", "Path to the YASL file")
	versionFlag := flag.Bool("V", false, "Print version and exit")
	versionFlagLong := flag.Bool("version", false, "Print version and exit")

	flag.Parse()

	if *versionFlag || *versionFlagLong {
		fmt.Println(core.Version)
		os.Exit(0)
	}

	var yamlPath, yaslPath string
	var err error

	if *yamlFlag != "" && *yaslFlag != "" {
		yamlPath = *yamlFlag
		yaslPath = *yaslFlag
	} else {
		args := flag.Args()
		if len(args) < 2 {
			fmt.Fprintln(os.Stderr, "Usage: ./yasl <file.yaml> <file.yasl> OR ./yasl -yaml <file.yaml> -yasl <file.yasl>")
			os.Exit(1)
		}
		yamlPath = args[0]
		yaslPath = args[1]
	}

	if _, err := os.Stat(yamlPath); os.IsNotExist(err) {
		fmt.Fprintf(os.Stderr, "YAML file not found: %s\n", yamlPath)
		os.Exit(1)
	}
	if _, err := os.Stat(yaslPath); os.IsNotExist(err) {
		fmt.Fprintf(os.Stderr, "YASL file not found: %s\n", yaslPath)
		os.Exit(1)
	}

	yamlPath, err = core.SanitizePath(yamlPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "YAML path error: %v\n", err)
		os.Exit(1)
	}
	yaslPath, err = core.SanitizePath(yaslPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "YASL path error: %v\n", err)
		os.Exit(1)
	}

	fmt.Println("OK - ", yamlPath, ", ", yaslPath)
}
