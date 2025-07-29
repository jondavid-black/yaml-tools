package main

import "C"
import (
	"encoding/json"
	"flag"
	"fmt"
	"github.com/jondavid-black/YASL/core"
	"github.com/sirupsen/logrus"
	"os"
	"strings"
)

// LogEntry defines a single structured log message.
type LogEntry struct {
	Level   string `json:"level"` // e.g., "info", "warn", "error"
	Message string `json:"message"`
}

// ProcessingResult is the single, unified return object.
// It will be serialized to JSON.
type ProcessingResult struct {
	Logs  []LogEntry `json:"logs"`
	Error string     `json:"error,omitempty"`
}

// process_yasl contains the original Go logic.
func processYASL(yamlStr string, yaslStr string, context map[string]string) ProcessingResult {

	var result ProcessingResult
	result.Logs = make([]LogEntry, 0) // Initialize the logs slice
	result.Logs = append(result.Logs, LogEntry{Level: "debug", Message: "▶️  Starting YASL processing."})

	if yamlStr == "" {
		result.Logs = append(result.Logs, LogEntry{Level: "error", Message: "YAML input cannot be empty"})
		result.Error = "YAML input cannot be empty"
		return result
	}
	if yaslStr == "" {
		result.Logs = append(result.Logs, LogEntry{Level: "error", Message: "YASL input cannot be empty"})
		result.Error = "YASL input cannot be empty"
		return result
	}

	// Extract context variables by looping through the map and creating primitive types
	var quiet bool = false    // default value
	var verbose bool = false  // default value
	var sslVerify bool = true // default value
	var httpProxy string      // default empty
	var httpsProxy string     // default empty
	for key, value := range context {
		switch key {
		case "quiet":
			quiet = value == "true"
		case "verbose":
			verbose = value == "true"
		case "ssl_verify":
			sslVerify = value != "false" // true unless explicitly set to "false"
			if !sslVerify {
				result.Logs = append(result.Logs, LogEntry{Level: "warn", Message: "SSL verification is disabled."})
			}
		case "http_proxy":
			httpProxy = value
		case "https_proxy":
			httpsProxy = value
		default:
			result.Logs = append(result.Logs, LogEntry{Level: "warn", Message: fmt.Sprintf("Unknown context variable: %s", key)})
		}
	}

	// debug logging for context variables
	var contextInputs string = "YASL context variables: /n"
	contextInputs += fmt.Sprintf("  - quiet: %s", quiet)
	contextInputs += fmt.Sprintf("  - verbose: %s", verbose)
	contextInputs += fmt.Sprintf("  - ssl_verify: %t", sslVerify)
	contextInputs += fmt.Sprintf("  - http_proxy: %s", httpProxy)
	contextInputs += fmt.Sprintf("  - https_proxy: %s", httpsProxy)

	result.Logs = append(result.Logs, LogEntry{Level: "debug", Message: contextInputs})

	// TODO: add processing logic

	fmt.Println("✅ Go logic complete.")
	result.Logs = append(result.Logs, LogEntry{Level: "debug", Message: "✅ YASL processing complete."})
	return result
}

// ProcessYASL is the C-compatible exported function.
// It takes C strings as input and returns a single C string containing JSON.
//
//export ProcessYASL
func ProcessYASL(yaml *C.char, yasl *C.char, contextJSON *C.char) *C.char {
	// Convert C inputs to Go strings
	yamlStr := C.GoString(yaml)
	yaslStr := C.GoString(yasl)
	contextJSONStr := C.GoString(contextJSON)

	// Unmarshal the context map from JSON
	var context map[string]string
	if err := json.Unmarshal([]byte(contextJSONStr), &context); err != nil {
		errJSON, _ := json.Marshal(ProcessingResult{Error: "failed to parse context JSON"})
		return C.CString(string(errJSON))
	}

	// Call the main Go logic
	result := processYASL(yamlStr, yaslStr, context)

	// Marshal the entire result object to a single JSON string
	jsonBytes, _ := json.Marshal(result)
	return C.CString(string(jsonBytes))
}

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

	// Collect context inputs from environment variables or CLI flags
	context := make(map[string]string)

	// add any CLI flags
	context["quiet"] = fmt.Sprintf("%t", *quietFlag || *quietFlagLong)
	context["verbose"] = fmt.Sprintf("%t", *verboseFlag || *verboseFlagLong)

	// add any environment variables
	envVars := []string{"SSL_VERIFY", "HTTP_PROXY", "HTTPS_PROXY"}
	for _, envVar := range envVars {
		if val, exists := os.LookupEnv(envVar); exists {
			context[strings.TrimPrefix(envVar, envVar)] = val
		}
	}

	result := processYASL(yamlPath, yaslPath, context)

	if result.Error != "" {
		logrus.Errorf("YASL rocessing error: %s", result.Error)
		os.Exit(1)
	} else {
		logrus.Infof("YASL processing completed successfully.")
	}

	// Print the result logs
	for _, logEntry := range result.Logs {
		var level logrus.Level
		switch strings.ToLower(logEntry.Level) {
		case "trace":
			level = logrus.TraceLevel
		case "debug":
			level = logrus.DebugLevel
		case "info":
			level = logrus.InfoLevel
		case "warn", "warning":
			level = logrus.WarnLevel
		case "error":
			level = logrus.ErrorLevel
		case "fatal":
			level = logrus.FatalLevel
		case "panic":
			level = logrus.PanicLevel
		default:
			level = logrus.InfoLevel
		}
		logrus.WithFields(logrus.Fields{
			"level":   logEntry.Level,
			"message": logEntry.Message,
		}).Log(level)
	}

	logrus.Infof("OK - %s, %s", yamlPath, yaslPath)
}
