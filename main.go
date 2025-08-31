package main

import (
	"archive/zip"
	"flag"
	"fmt"
	"github.com/sirupsen/logrus"
	"gopkg.in/yaml.v3"
	"io"
	"net/http"
	"os"
	"path/filepath"
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

// processYASL parses the YAML input file and returns its AST and a list of error messages.
// The AST is a JSON-serializable structure mirroring yaml.Node, including Kind, Tag, Value, Content, Anchor, Alias, Style, Line, Column, HeadComment, FootComment, LineComment.
// Limitations: Anchors and aliases are included as-is, but cross-references are not resolved. Custom Go types in yaml.Node are mapped to JSON-friendly types.
//
// Parameters:
//
//	yamlRootFile: path to the YAML file (required)
//	yaslRootFile: path to the YASL file (required)
//	quiet: suppress non-error output (optional)
//	verbose: enable verbose logging (optional)
//	output: log output type: "text", "json", or "yaml" (optional)
//	sslVerify: enable/disable SSL verification (optional)
//	httpProxy: HTTP proxy URL (optional)
//	httpsProxy: HTTPS proxy URL (optional)
//  treatWarningsAsErrors: if true, warnings are treated as errors and will cause a nonzero exit code
//
// Returns:
//
//	hasError: true if there were errors during processing
//	hasWarning: true if there were warnings (only if treatWarningsAsErrors is false)
//
// Example usage:
//
//	hasError, hasWarning := processYASL("input.yaml", "schema.yasl", false, false, "text", true, "", "", false)

func processYASL(
	yamlRootFile string,
	yaslRootFile string,
	quiet bool,
	verbose bool,
	output string,
	sslVerify bool,
	httpProxy string,
	httpsProxy string,
	treatWarningsAsErrors bool,
) (bool, bool) {
	hasError := false
	hasWarning := false

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

	// Log and check for missing YAML file
	if yamlRootFile == "" {
		logrus.Error("YAML input cannot be empty")
		hasError = true
	}
	// Log and check for missing YASL file
	if yaslRootFile == "" {
		logrus.Error("YASL input cannot be empty")
		hasError = true
	}
	if hasError {
		return hasError, hasWarning
	}

	var yaslData []interface{}
	var yaslError []error

	// Use file:// URI for local files
    baseURI := yaslRootFile
    if !strings.HasPrefix(yaslRootFile, "http://") && !strings.HasPrefix(yaslRootFile, "https://") && !strings.HasPrefix(yaslRootFile, "file://") {
        abs, _ := filepath.Abs(yaslRootFile)
        baseURI = "file://" + abs
    }
    yaslData, yaslError := collectAllYASLData(baseURI, make(map[string]struct{}))

	// log errors and exit if any
	if len(yaslError) > 0 {
		for _, err := range yaslError {
			logrus.Error(err)
		}
		hasError = true
		return hasError, hasWarning
	}
	





	
	

	if len(yamlData) == 0 {
		logrus.Error("YAML file is empty or invalid")
		hasError = true
		return hasError, hasWarning
	}

	return hasError, hasWarning
}

func main() {
	projFlag := flag.String("proj", "", "Path to the project file (default: proj.yasl)")
	versionFlag := flag.Bool("V", false, "Print version and exit")
	versionFlagLong := flag.Bool("version", false, "Print version and exit")
	helpFlag := flag.Bool("h", false, "Show help and exit")
	helpFlagLong := flag.Bool("help", false, "Show help and exit")
	quietFlag := flag.Bool("q", false, "Run in quiet mode (errors only)")
	quietFlagLong := flag.Bool("quiet", false, "Run in quiet mode (errors only)")
	verboseFlag := flag.Bool("v", false, "Run in verbose mode (debug/trace)")
	verboseFlagLong := flag.Bool("verbose", false, "Run in verbose mode (debug/trace)")
	outputFlag := flag.String("output", "", "Log output type: text, json, yaml (overrides project)")
	werrorFlag := flag.Bool("werror", false, "Treat warnings as errors (nonzero exit code on warnings)")

	flag.Parse()

	if *helpFlag || *helpFlagLong {
		fmt.Println("YASL - YAML Advanced Schema Language CLI")
		fmt.Println("Usage:")
		fmt.Println("  yasl [options] <command> [args...]")
		fmt.Println("Commands:")
		fmt.Println("  init         Initialize a new proj.yasl in the current directory")
		fmt.Println("  import       Add an external dependency by URI (downloads to yasl_modules)")
		fmt.Println("  check        Validate one or more YAML files using the project schema")
		fmt.Println("  package      Assemble project and schema into a zip for release/publication")
		fmt.Println("Options:")
		fmt.Println("  -proj <proj.yasl>     Path to the project file (default: proj.yasl)")
		fmt.Println("  -V, --version         Print version and exit")
		fmt.Println("  -h, --help            Show help and exit")
		fmt.Println("  -q, --quiet           Run in quiet mode (errors only)")
		fmt.Println("  -v, --verbose         Run in verbose mode (debug/trace)")
		fmt.Println("  --output              Log output type: text, json, yaml (overrides project)")
		fmt.Println("  --werror              Treat warnings as errors (nonzero exit code on warnings)")
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

	args := flag.Args()
	if len(args) < 1 {
		logrus.Error("Usage: yasl [options] <command> [args...]")
		os.Exit(1)
	}
	command := args[0]

	switch command {
	case "init":
		projPath := "proj.yasl"
		if _, err := os.Stat(projPath); err == nil {
			logrus.Errorf("Project file already exists: %s", projPath)
			os.Exit(1)
		}
		var projName string
		if len(args) > 1 {
			projName = args[1]
		} else {
			cwd, err := os.Getwd()
			if err != nil {
				logrus.Fatalf("Failed to get current directory: %v", err)
			}
			projName = filepath.Base(cwd)
		}

		projContent = `yasl:
name: ` + projName + `

`
				
	

	case "import":
		if len(args) < 2 {
			logrus.Error("Usage: yasl import <dependency-uri>")
			os.Exit(1)
		}
		depURI := args[1]
		modDir := "yasl_modules"
		if err := os.MkdirAll(modDir, 0755); err != nil {
			logrus.Fatalf("Failed to create module directory: %v", err)
		}
		resp, err := http.Get(depURI)
		if err != nil {
			logrus.Fatalf("Failed to download dependency: %v", err)
		}
		defer resp.Body.Close()
		base := filepath.Base(depURI)
		outPath := filepath.Join(modDir, base)
		out, err := os.Create(outPath)
		if err != nil {
			logrus.Fatalf("Failed to create dependency file: %v", err)
		}
		defer out.Close()
		if _, err := io.Copy(out, resp.Body); err != nil {
			logrus.Fatalf("Failed to save dependency: %v", err)
		}
		logrus.Infof("Imported dependency to %s", outPath)
		return

	case "check":
		if len(args) < 2 {
			logrus.Error("Usage: yasl check <file.yaml>")
			os.Exit(1)
		}
		yamlPath := args[1]
		yamlPath, err := SanitizePath(yamlPath)
		if err != nil {
			logrus.Errorf("YAML path error: %v", err)
			os.Exit(1)
		}
		if _, err := os.Stat(yamlPath); os.IsNotExist(err) {
			logrus.Errorf("YAML file not found: %s", yamlPath)
			os.Exit(1)
		}
		projPath := *projFlag
		if projPath == "" {
			projPath = "proj.yasl"
			if _, err := os.Stat(projPath); os.IsNotExist(err) {
				yamlDir := filepath.Dir(yamlPath)
				altProj := filepath.Join(yamlDir, "proj.yasl")
				if _, err := os.Stat(altProj); err == nil {
					projPath = altProj
				}
			}
		}
		if _, err := os.Stat(projPath); os.IsNotExist(err) {
			logrus.Errorf("Project file not found: %s", projPath)
			os.Exit(1)
		}
		type ProjectConfig struct {
			YAML string `yaml:"yaml"`
			Output string `yaml:"output"`
			SSLVerify *bool `yaml:"ssl_verify"`
			HTTPProxy string `yaml:"http_proxy"`
			HTTPSProxy string `yaml:"https_proxy"`
		}
		var projConfig ProjectConfig
		{
			f, err := os.Open(projPath)
			if err != nil {
				logrus.Fatalf("Failed to open project file: %v", err)
			}
			defer f.Close()
			dec := yaml.NewDecoder(f)
			if err := dec.Decode(&projConfig); err != nil && err != io.EOF {
				logrus.Fatalf("Failed to parse project file: %v", err)
			}
		}
		yaslPath := projConfig.YAML
		if yaslPath == "" {
			logrus.Error("YASL file must be specified in the project file under 'yaml'")
			os.Exit(1)
		}
		if _, err := os.Stat(yaslPath); os.IsNotExist(err) {
			logrus.Errorf("YASL file not found: %s", yaslPath)
			os.Exit(1)
		}
		output := projConfig.Output
		if *outputFlag != "" {
			output = *outputFlag
		}
		sslVerify := true
		if projConfig.SSLVerify != nil {
			sslVerify = *projConfig.SSLVerify
		}
		if val, exists := os.LookupEnv("SSL_VERIFY"); exists && val == "false" {
			sslVerify = false
		}
		httpProxy := projConfig.HTTPProxy
		httpsProxy := projConfig.HTTPSProxy
		if v := os.Getenv("HTTP_PROXY"); v != "" {
			httpProxy = v
		}
		if v := os.Getenv("HTTPS_PROXY"); v != "" {
			httpsProxy = v
		}
		quiet := *quietFlag || *quietFlagLong
		verbose := *verboseFlag || *verboseFlagLong
		warnOnError := *werrorFlag
		hasError, hasWarning := processYASL(
			yamlPath,
			yaslPath,
			quiet,
			verbose,
			output,
			sslVerify,
			httpProxy,
			httpsProxy,
			warnOnError,
		)
		if hasError {
			os.Exit(1)
		}
		if warnOnError && hasWarning {
			os.Exit(1)
		}
		logrus.Infof("✅ YASL check complete.")
		return

	case "package":
		projPath := *projFlag
		if projPath == "" {
			projPath = "proj.yasl"
		}
		if _, err := os.Stat(projPath); os.IsNotExist(err) {
			logrus.Errorf("Project file not found: %s", projPath)
			os.Exit(1)
		}
		zipName := "yasl_package.zip"
		zipFile, err := os.Create(zipName)
		if err != nil {
			logrus.Fatalf("Failed to create zip file: %v", err)
		}
		defer zipFile.Close()
		zipWriter := zip.NewWriter(zipFile)
		defer zipWriter.Close()
		if err := addFileToZip(zipWriter, projPath); err != nil {
			logrus.Fatalf("Failed to add project file to zip: %v", err)
		}
		logrus.Infof("Packaged project as %s", zipName)
		return

	default:
		logrus.Errorf("Unknown command: %s", command)
		os.Exit(1)
	}
	return err
}
