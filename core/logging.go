package core

import (
	"github.com/sirupsen/logrus"
	"gopkg.in/yaml.v3"
)

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
	return append([]byte(entry.Message), '\n'), nil
}

// YAMLFormatter outputs logs as YAML objects (timestamp, level, message).
type YAMLFormatter struct{}

func (f *YAMLFormatter) Format(entry *logrus.Entry) ([]byte, error) {
	obj := map[string]interface{}{
		"time":  entry.Time.Format("2006-01-02T15:04:05Z07:00"),
		"level": entry.Level.String(),
		"msg":   entry.Message,
	}
	out, err := yaml.Marshal(obj)
	if err != nil {
		return nil, err
	}
	return out, nil
}
