package main

import (
    "io"
    "net/url"
    "path/filepath"
)

func processYASL(yaslRootFile string)(map[string]interface{}, map[string]interface{}, error) {

	data, errors := collectAllYASLData(yaslRootFile, make(map[string]struct{}))
	if len(errors) > 0 {
		for _, err := range errors {
			logrus.Error(err)
		}
		return nil, nil, fmt.Errorf("YASL processing errors: %v", errors)
	}

	if len(data) == 0 {
		logrus.Error("YASL file is empty or invalid")
		return nil, nil, fmt.Errorf("YASL file is empty or invalid")
	}

	for _, doc := range data {
		if doc == nil {
			logrus.Error("YASL document is nil")
			return nil, nil, fmt.Errorf("YASL document is nil")
		}
	}

	// Process the YASL data as needed
	// This is a placeholder for actual processing logic
	typeDefs map[string]interface{},
    enums map[string]interface{},
    typeDefSeen map[string]struct{},
    enumSeen map[string]struct{},
    errs *[]error,
	for _, doc := range data {
		if m, ok := doc.(map[string]interface{}); ok {
			for k, v := range m {
				switch keyStr {
				case "type_def":
					addTypeDefs(v, typeDefs, typeDefSeen, errs)
				case "enum":
					addEnums(v, enums, enumSeen, errs)
				case "yasl":
					// a yasl key contains a list of yasl definitions
					if list, ok := v.([]interface{}); ok {
						for _, item := range list {
							// get the item yaml key from the list item
							if itemMap, ok := item.(map[string]interface{}); ok {
								if yamlKey, ok := itemMap["yaml"]; ok {
									// process the yaml key as needed
									// this is a placeholder for actual processing logic
									logrus.Infof("Processing YASL item with yaml key: %v", yamlKey)
								} else {
									logrus.Warnf("YASL item does not contain a yaml key: %v", item)
								}

				}
			}
		}
	}
	return typeDefs, enums, errs
}

// addTypeDefs adds type_def entries to the map, checking for duplicates.
func addTypeDefs(
    v interface{},
    typeDefs map[string]interface{},
    typeDefSeen map[string]struct{},
    errs *[]error,
) {
    defs, ok := v.(map[interface{}]interface{})
    if !ok {
        return
    }
    for name, def := range defs {
        nameStr, ok := name.(string)
        if !ok {
            continue
        }
        if _, exists := typeDefSeen[nameStr]; exists {
            *errs = append(*errs, fmt.Errorf("duplicate type_def name: %s", nameStr))
            continue
        }
        typeDefSeen[nameStr] = struct{}{}
        typeDefs[nameStr] = def
    }
}

// addEnums adds enum entries to the map, checking for duplicates.
func addEnums(
    v interface{},
    enums map[string]interface{},
    enumSeen map[string]struct{},
    errs *[]error,
) {
    enumsMap, ok := v.(map[interface{}]interface{})
    if !ok {
        return
    }
    for name, enumDef := range enumsMap {
        nameStr, ok := name.(string)
        if !ok {
            continue
        }
        if _, exists := enumSeen[nameStr]; exists {
            *errs = append(*errs, fmt.Errorf("duplicate enum name: %s", nameStr))
            continue
        }
        enumSeen[nameStr] = struct{}{}
        enums[nameStr] = enumDef
    }
}

// collectAllYASLData recursively parses the root YASL file and all its imports (local and remote),
// returning a slice of all parsed YASL documents. It avoids infinite loops by tracking processed URIs.
func collectAllYASLData(
    baseURI string,
    processed map[string]struct{},
) ([]interface{}, []error) {
    var allData []interface{}
    var allErrs []error

    // Canonicalize the base URI
    u, err := url.Parse(baseURI)
    if err != nil {
        allErrs = append(allErrs, fmt.Errorf("invalid base URI: %s: %w", baseURI, err))
        return allData, allErrs
    }
    canon := u.String()
    if _, seen := processed[canon]; seen {
        // Already processed, skip to avoid circular import
        return allData, allErrs
    }
    processed[canon] = struct{}{}

    // Load and parse the YASL file (local or remote)
    var reader io.ReadCloser
    switch u.Scheme {
    case "file", "":
        // Local file
        path := u.Path
        if u.Scheme == "" {
            path = baseURI // fallback for plain paths
        }
        f, err := os.Open(path)  // TODO:  Implement safeOpenYASL to check for .yaml/.yasl and trusted root
        if err != nil {
            allErrs = append(allErrs, fmt.Errorf("failed to open YASL file: %s: %w", path, err))
            return allData, allErrs
        }
        reader = f
    default:
        // Remote file
        resp, err := fetchRemoteYASL(u.String())
        if err != nil {
            allErrs = append(allErrs, fmt.Errorf("failed to fetch remote YASL: %s: %w", u.String(), err))
            return allData, allErrs
        }
        reader = resp
    }
    defer reader.Close()

    yaslData, yaslErrs := parseReader(reader)
    if len(yaslErrs) > 0 {
        allErrs = append(allErrs, yaslErrs...)
        return allData, allErrs
    }
    allData = append(allData, yaslData...)

    localImports, remoteImports := findYASLImports(yaslData)

    // Recursively process local imports
    for _, imp := range localImports {
        impURI := resolveImportURI(u, imp)
        subData, subErrs := collectAllYASLData(impURI, processed)
        allData = append(allData, subData...)
        allErrs = append(allErrs, subErrs...)
    }
    // Recursively process remote imports
    for _, imp := range remoteImports {
        impURI := resolveImportURI(u, imp)
        subData, subErrs := collectAllYASLData(impURI, processed)
        allData = append(allData, subData...)
        allErrs = append(allErrs, subErrs...)
    }
    return allData, allErrs
}

// resolveImportURI resolves an import path/URI relative to the parent URI.
func resolveImportURI(parent *url.URL, importPath string) string {
    impURL, err := url.Parse(importPath)
    if err != nil {
        return importPath // fallback: return as-is
    }
    return parent.ResolveReference(impURL).String()
}

// fetchRemoteYASL fetches a remote YASL file and returns an io.ReadCloser.
func fetchRemoteYASL(uri string) (io.ReadCloser, error) {
    // Use http.Get or a custom HTTP client as needed
    resp, err := http.Get(uri)  // TODO: potential security risk, consider using a custom client
    if err != nil {
        return nil, err
    }
    if resp.StatusCode != 200 {
        resp.Body.Close()
        return nil, fmt.Errorf("HTTP error %d for %s", resp.StatusCode, uri)
    }
    return resp.Body, nil
}

// parseReader parses a YASL YAML file from an io.Reader and returns []interface{} and []error.
func parseReader(r io.Reader) ([]interface{}, []error) {
    dec := yaml.NewDecoder(r)
    var docs []interface{}
    var errs []error
    for {
        var doc interface{}
        err := dec.Decode(&doc)
        if err != nil {
            if err == io.EOF {
                break
            }
            errs = append(errs, err)
            break
        }
        docs = append(docs, doc)
    }
    return docs, errs
}


// TODO:  There is a potential path-injection vulnerability when opening YASL files.
// The code below is a basic check to ensure the file is within a trusted directory.
// This has not yet been implemented as it is incomplete in concept and needs refinement.
// The key issue is how do we establish trust for local, networked, or remote files?
// Perhaps we need some sort of YASL package manager that forces the user to explicitly see the dependency tree and approve it.

// isYASLFile checks if the given path has a .yaml or .yasl extension.
func isYASLFile(path string) bool {
    ext := strings.ToLower(filepath.Ext(path))
    return ext == ".yaml" || ext == ".yasl"
}

// isPathSafe checks if the given path is within a trusted root directory.
// It returns true if the path is safe, false otherwise.
// This is a basic check and may need to be extended for symlinks or other cases.
// It assumes trustedRoot is an absolute path to a directory that is considered safe.
func isPathSafe(path string, trustedRoot string) bool {
    absPath, err := filepath.Abs(path)
    if err != nil {
        return false
    }
    root, err := filepath.Abs(trustedRoot)
    if err != nil {
        return false
    }
    rel, err := filepath.Rel(root, absPath)
    if err != nil {
        return false
    }
    // rel will not start with ".." if absPath is within root
    return !strings.HasPrefix(rel, "..")
}

// safeOpenYASL opens a YASL file safely, ensuring it has a .yaml or .yasl extension
// and is within a trusted root directory.
// It returns an os.File pointer or an error if the checks fail.
func safeOpenYASL(path, trustedRoot string) (*os.File, error) {
    if !isYASLFile(path) {
        return nil, fmt.Errorf("imported file does not have a .yaml or .yasl extension: %s", path)
    }
    if !isPathSafe(path, trustedRoot) {
        return nil, fmt.Errorf("imported file is outside the trusted root: %s", path)
    }
    // Optionally, check for symlinks here
    return os.Open(path)
}