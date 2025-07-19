package main

import (
	"flag"
	"fmt"
	"github.com/jondavid-black/YASL/core"
	"os"
	"github.com/sirupsen/logrus"
	"strings"
)

func main() {
	yamlFlag := flag.String("yaml", "", "Path to the YAML file")
	yaslFlag := flag.String("yasl", "", "Path to the YASL file")
	versionFlag := flag.Bool("V", false, "Print version and exit")
	versionFlagLong := flag.Bool("version", false, "Print version and exit")
	helpFlag := flag.Bool("h", false, "Show help and exit")
	helpFlagLong := flag.Bool("help", false, "Show help and exit")
	quietFlag := flag.Bool("q", false, "Run in quiet mode (errors only)")
	quietFlagLong := flag.Bool("quiet", false, "Run in quiet mode (errors only)")
	verboseFlag := flag.Bool("v", false, "Run in verbose mode (debug/trace)")
	verboseFlagLong := flag.Bool("verbose", false, "Run in verbose mode (debug/trace)")
	outputTypeFlag := flag.String("output-type", "text", "Log output type: text, json, yaml")

	flag.Parse()

	// Set log level based on flags
	switch {
	case *quietFlag || *quietFlagLong:
		logrus.SetLevel(logrus.ErrorLevel)
	case *verboseFlag || *verboseFlagLong:
		logrus.SetLevel(logrus.TraceLevel)
	default:
		logrus.SetLevel(logrus.InfoLevel)
	}

	// Set log output format
	outputType := core.OutputText
	switch strings.ToLower(*outputTypeFlag) {
	case "json":
		outputType = core.OutputJSON
	case "yaml":
		outputType = core.OutputYAML
	}
	core.SetLoggerFormat(outputType)

	if *helpFlag || *helpFlagLong {
		fmt.Println("YASL - YAML Advanced Schema Language CLI")
		fmt.Println("Usage:")
		fmt.Println("  yasl <file.yaml> <file.yasl>")
		fmt.Println("  yasl -yaml <file.yaml> -yasl <file.yasl>")
		fmt.Println("Options:")
		fmt.Println("  -yaml <file.yaml>     Path to the YAML file")
		fmt.Println("  -yasl <file.yasl>     Path to the YASL file")
		fmt.Println("  -V, --version         Print version and exit")
		fmt.Println("  -h, --help            Show help and exit")
		fmt.Println("  -q, --quiet           Run in quiet mode (errors only)")
		fmt.Println("  -v, --verbose         Run in verbose mode (debug/trace)")
		fmt.Println("  --output-type         Log output type: text, json, yaml")
		os.Exit(0)
	}

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
			logrus.Error("Usage: ./yasl <file.yaml> <file.yasl> OR ./yasl -yaml <file.yaml> -yasl <file.yasl>")
			os.Exit(1)
		}
		yamlPath = args[0]
		yaslPath = args[1]
	}

	if _, err := os.Stat(yamlPath); os.IsNotExist(err) {
		logrus.Errorf("YAML file not found: %s", yamlPath)
		os.Exit(1)
	}
	if _, err := os.Stat(yaslPath); os.IsNotExist(err) {
		logrus.Errorf("YASL file not found: %s", yaslPath)
		os.Exit(1)
	}

	yamlPath, err = core.SanitizePath(yamlPath)
	if err != nil {
		logrus.Errorf("YAML path error: %v", err)
		os.Exit(1)
	}
	yaslPath, err = core.SanitizePath(yaslPath)
	if err != nil {
		logrus.Errorf("YASL path error: %v", err)
		os.Exit(1)
	}

	logrus.Infof("OK - %s, %s", yamlPath, yaslPath)
}
