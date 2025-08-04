package main

import "C"
import (
	"encoding/json"
	"flag"
	"fmt"
	"github.com/sirupsen/logrus"
	"gopkg.in/yaml.v3"
	"os"
	"strings"
)

// Version is the semantic version for the YASL CLI.
const Version = "v0.0.6"

func SanitizePath(path string) (string, error) {
	// Example sanitization logic: ensure no special characters or invalid paths
	if len(path) == 0 || path[0] == '-' {
		return "", fmt.Errorf("invalid file path: %s", path)
	}
	return path, nil
}

// OutputType represents the supported log output formats.
type OutputType string

const (
	OutputText OutputType = "text"
	OutputJSON OutputType = "json"
	OutputYAML OutputType = "yaml"
)

// SetLoggerFormat configures logrus output format based on the outputType.
func SetLoggerFormat(outputType OutputType) {
	switch outputType {
	case OutputText:
		logrus.SetFormatter(&PlainFormatter{})
	case OutputJSON:
		logrus.SetFormatter(&logrus.JSONFormatter{})
	case OutputYAML:
		logrus.SetFormatter(&YAMLFormatter{})
	}
}

// PlainFormatter outputs only the log message, no timestamp or level.
type PlainFormatter struct{}

func (f *PlainFormatter) Format(entry *logrus.Entry) ([]byte, error) {
	msg := entry.Message
	if len(entry.Data) > 0 {
		fields := make([]string, 0, len(entry.Data))
		for k, v := range entry.Data {
			fields = append(fields, fmt.Sprintf("%s=%v", k, v))
		}
		msg = fmt.Sprintf("%s | %s", msg, strings.Join(fields, ", "))
	}
	return append([]byte(msg), '\n'), nil
}

// YAMLFormatter outputs logs as YAML objects (timestamp, level, message).
type YAMLFormatter struct{}

func (f *YAMLFormatter) Format(entry *logrus.Entry) ([]byte, error) {
	obj := map[string]interface{}{
		"time":  entry.Time.Format("2006-01-02T15:04:05Z07:00"),
		"level": entry.Level.String(),
		"msg":   entry.Message,
	}
	for k, v := range entry.Data {
		obj[k] = v
	}
	out, err := yaml.Marshal(obj)
	if err != nil {
		return nil, err
	}
	return out, nil
}

// processContext extracts context variables and returns them for process control.
func processContext(context map[string]string) (quiet, verbose, sslVerify bool, output, httpProxy, httpsProxy string) {
	quiet = false
	verbose = false
	sslVerify = true
	output = "text" // Default output type
	httpProxy = ""
	httpsProxy = ""
	for key, value := range context {
		switch key {
		case "quiet":
			quiet = value == "true"
		case "verbose":
			verbose = value == "true"
		case "ssl_verify":
			sslVerify = value != "false"
			if !sslVerify {
				logrus.Warn("SSL verification is disabled.")
			}
		case "output":
			output = value
			if output != "text" && output != "json" && output != "yaml" {
				logrus.Warnf("Unknown output type: %s, defaulting to text", value)
				output = "text"
			}
		case "http_proxy":
			httpProxy = value
		case "https_proxy":
			httpsProxy = value
		default:
			logrus.Warnf("Unknown context variable: %s", key)
		}
	}

	return
}

// process_yasl contains the original Go logic.
func processYASL(yamlRootFile string, yaslRootFile string, context map[string]string, yamlData map[string]string, yaslData map[string]string) error {
	logrus.Infof("YASL version: %s", Version)
	logrus.Debug("▶️  Starting YASL processing.")

	if yamlRootFile == "" {
		logrus.Error("YAML input cannot be empty")
		return fmt.Errorf("YAML input cannot be empty")
	}
	if yaslRootFile == "" {
		logrus.Error("YASL input cannot be empty")
		return fmt.Errorf("YASL input cannot be empty")
	}

	quiet, verbose, sslVerify, output, httpProxy, httpsProxy := processContext(context)

	// Set log level based on flags
	switch {
	case quiet:
		logrus.SetLevel(logrus.ErrorLevel)
	case verbose:
		logrus.SetLevel(logrus.TraceLevel)
	default:
		logrus.SetLevel(logrus.InfoLevel)
	}

	// Set log output format
	switch strings.ToLower(output) {
	case "json":
		SetLoggerFormat(OutputJSON)
	case "yaml":
		SetLoggerFormat(OutputYAML)
	}

	logrus.Debugf("YASL context variables: \n  - quiet: %t\n  - verbose: %t\n  - output: %s\n  - ssl_verify: %t\n  - http_proxy: %s\n  - https_proxy: %s\n", quiet, verbose, output, sslVerify, httpProxy, httpsProxy)

	// TODO: add processing logic, including yamlData and yaslData usage for imports
	// For now, just log if maps are provided
	if yamlData != nil {
		logrus.Debug("yamlData map provided for imports.")
	}
	if yaslData != nil {
		logrus.Debug("yaslData map provided for imports.")
	}

	logrus.Debug("✅ YASL processing complete.")
	return nil
}

// ProcessYASL is the C-compatible exported function.
// It takes C strings as input and returns a single C string containing JSON.
//
//export ProcessYASL
func ProcessYASL(yaml *C.char, yasl *C.char, contextJSON *C.char, yamlDataJSON *C.char, yaslDataJSON *C.char) *C.char {
	// Convert C inputs to Go strings
	yamlStr := C.GoString(yaml)
	yaslStr := C.GoString(yasl)
	contextJSONStr := C.GoString(contextJSON)
	yamlDataJSONStr := C.GoString(yamlDataJSON)
	yaslDataJSONStr := C.GoString(yaslDataJSON)

	// Unmarshal the context map from JSON
	var context map[string]string
	if err := json.Unmarshal([]byte(contextJSONStr), &context); err != nil {
		return C.CString(`{"error": "failed to parse context JSON"}`)
	}

	// Unmarshal yamlData and yaslData maps from JSON
	var yamlData map[string]string
	var yaslData map[string]string
	if yamlDataJSONStr != "" {
		if err := json.Unmarshal([]byte(yamlDataJSONStr), &yamlData); err != nil {
			return C.CString(`{"error": "failed to parse yamlData JSON"}`)
		}
	}
	if yaslDataJSONStr != "" {
		if err := json.Unmarshal([]byte(yaslDataJSONStr), &yaslData); err != nil {
			return C.CString(`{"error": "failed to parse yaslData JSON"}`)
		}
	}

	// Call the main Go logic
	err := processYASL(yamlStr, yaslStr, context, yamlData, yaslData)
	if err != nil {
		return C.CString(fmt.Sprintf(`{"error": "%s"}`, err.Error()))
	}
	return C.CString(`{"error": null}`)
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
	outputFlag := flag.String("output", "text", "Log output type: text, json, yaml")

	flag.Parse()

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
		fmt.Println("  --output         Log output type: text, json, yaml")
		fmt.Println("Environment Variables:")
		fmt.Println("  SSL_VERIFY            Set to 'false' to disable SSL verification")
		fmt.Println("  HTTP_PROXY            Set HTTP proxy URL")
		fmt.Println("  HTTPS_PROXY           Set HTTPS proxy URL")
		os.Exit(0)
	}

	if *versionFlag || *versionFlagLong {
		fmt.Println(Version)
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

	yamlPath, err = SanitizePath(yamlPath)
	if err != nil {
		logrus.Errorf("YAML path error: %v", err)
		os.Exit(1)
	}
	yaslPath, err = SanitizePath(yaslPath)
	if err != nil {
		logrus.Errorf("YASL path error: %v", err)
		os.Exit(1)
	}

	if _, err := os.Stat(yamlPath); os.IsNotExist(err) {
		logrus.Errorf("YAML file not found: %s", yamlPath)
		os.Exit(1)
	}
	if _, err := os.Stat(yaslPath); os.IsNotExist(err) {
		logrus.Errorf("YASL file not found: %s", yaslPath)
		os.Exit(1)
	}

	// Collect context inputs from environment variables or CLI flags
	context := make(map[string]string)

	// add any CLI flags
	context["quiet"] = fmt.Sprintf("%t", *quietFlag || *quietFlagLong)
	context["verbose"] = fmt.Sprintf("%t", *verboseFlag || *verboseFlagLong)
	context["output"] = fmt.Sprintf("%s", *outputFlag)

	// add any environment variables
	envVars := []string{"SSL_VERIFY", "HTTP_PROXY", "HTTPS_PROXY"}
	for _, envVar := range envVars {
		if val, exists := os.LookupEnv(envVar); exists {
			context[strings.TrimPrefix(envVar, envVar)] = val
		}
	}

	err = processYASL(yamlPath, yaslPath, context, nil, nil)
	if err != nil {
		logrus.Errorf("YASL processing error: %s", err)
		os.Exit(1)
	}
	logrus.Infof("OK - %s, %s", yamlPath, yaslPath)
}
