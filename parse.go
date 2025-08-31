package main

import (
    "bytes"
    "fmt"
    "os"
    "gopkg.in/yaml.v3"
)

type FileResult struct {
    FileName   string
    Documents  []*yaml.Node
    Errors     []error
}

// parse reads and parses one or more YAML documents from the given file path.
// It returns a slice of parsed documents and a slice of errors encountered.
func parse(filePath string) ([]FileResult) {
    var results []FileResult
    uq := core.NewUniqueQueue()
    uq.Enqueue(filePath)
    for !uq.IsEmpty() {
        file := uq.Dequeue()
        // Process file...
        nodes, errs := processFile(file)
        results = append(results, FileResult{
            FileName:  file,
            Documents: nodes,
            Errors:    errs,
        })
        // If you discover "other.yaml":
        for node := range nodes {
            
        }
    }
}

// ImportValueNode searches for "import" keys in a YAML node, handling cases where:
// - "import" is the root key in the document
// - "import" is a key in a list of entries (e.g., in a sequence of maps)
// - "import" is a subkey of a "yasl" key
// Returns a slice of import URIs and a slice of errors encountered.
// This implementation uses UniqueQueue[*yaml.Node] for traversal.
func ImportValueNode(fileName string, root *yaml.Node) ([]string, []error) {
    var uris []string
    var errors []error
    if root == nil {
        return uris, errors
    }

    queue := NewUniqueQueue[*yaml.Node]()
    queue.Enqueue(root)

    for !queue.IsEmpty() {
        node, ok := queue.Dequeue()
        if !ok || node == nil {
            continue
        }

        switch node.Kind {
        case yaml.MappingNode:
            for i := 0; i < len(node.Content)-1; i += 2 {
                keyNode := node.Content[i]
                valueNode := node.Content[i+1]
                if keyNode.Value == "import" {
                    // Handle sequence or scalar
                    if valueNode.Kind == yaml.SequenceNode {
                        for _, item := range valueNode.Content {
                            if item.Kind == yaml.ScalarNode {
                                uris = append(uris, item.Value)
                            } else {
                                errors = append(errors, fmt.Errorf("expected scalar node in import sequence, got %v", item.Kind))
                            }
                        }
                    } else {
                        errors = append(errors, fmt.Errorf("expected sequence node for import value, got %v", valueNode.Kind))
                    }
                }
                // Always enqueue mapping and sequence values for further search
                if valueNode.Kind == yaml.MappingNode || valueNode.Kind == yaml.SequenceNode {
                    queue.Enqueue(valueNode)
                }
            }
        case yaml.SequenceNode:
            for _, item := range node.Content {
                if item.Kind == yaml.MappingNode || item.Kind == yaml.SequenceNode {
                    queue.Enqueue(item)
                }
            }
        }
    }
    return uris, errors
}

// processFile reads and parses a YAML file at the given path.
// It returns the parsed documents and any errors encountered.
func processFile(filePath string) ([]*yaml.Node, []error) {
    data, err := os.ReadFile(filePath)
    if err != nil {
        return nil, []error{fmt.Errorf("error reading file: %w", err)}
    }

    dec := yaml.NewDecoder(bytes.NewReader(data))
    var retVal []*yaml.Node
    var errs []error
    docNum := 1
    for {
        var node yaml.Node
        err := dec.Decode(&node)
        if err != nil {
            if err.Error() == "EOF" {
                break
            }
            errs = append(errs, fmt.Errorf("YAML parse error in document %s: %w", filePath, err))
            docNum++
            break
        }

        // Handle case where node.Kind == 0 (malformed or empty YAML)
        if node.Kind == 0 {
            errs = append(errs, fmt.Errorf("YAML document in file %s at doc %d is invalid or empty (node.Kind == 0)", filePath, docNum))
            docNum++
            break
        }

        // Strict check: treat empty docs as errors
        isEmpty := false
        if node.Kind == yaml.MappingNode || node.Kind == yaml.SequenceNode {
            isEmpty = len(node.Content) == 0
        }
        if isEmpty {
            startLine := node.Line
            endLine := node.Line
            if len(node.Content) > 0 {
                endLine = node.Content[len(node.Content)-1].Line
            }
            errs = append(errs, fmt.Errorf("YAML document in file %s at line %d-%d is empty", filePath, startLine, endLine))
        } else {
            retVal = append(retVal, &node)
        }
        docNum++
    }
    return retVal, errs
}

// getRootKeys returns the root key(s) of a YAML document, or a description if not a map.
func getRootKeys(doc interface{}) []string {
    switch v := doc.(type) {
    case map[string]interface{}:
        keys := make([]string, 0, len(v))
        for k := range v {
            keys = append(keys, k)
        }
        return keys
    case map[interface{}]interface{}:
        keys := make([]string, 0, len(v))
        for k := range v {
            keys = append(keys, fmt.Sprintf("%v", k))
        }
        return keys
    case []interface{}:
        return []string{"<root is a list>"}
    default:
        return []string{fmt.Sprintf("<root is %T>", doc)}
    }
}