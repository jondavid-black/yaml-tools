# YASL - YAML Schema Language Project Instructions for GitHub Copilot

## Project Overview
This project, YASL (YAML Advanced Schema Language), aims to provide robust YAML schema definition and validation capabilities. The core logic is written in Go, with API wrappers in Python and JavaScript to facilitate broader integration. We emphasize clean code, strong typing, comprehensive testing, and clear documentation.

## Project Structure
The project follows a modular structure:
- `core/`: Contains the core utility logic for YASL.
    - `core.go`: Core functionality for schema validation.
    - `core_test.go`: Unit tests for core functionality.
- `yasl.go`: Main entry point for the YASL CLI.
- `yasl_test.go`: Unit tests for YASL CLI functionality.
- `go.mod` and `go.sum`: Go module files for dependency management.
- `README.md`: Project documentation and usage instructions.
- `docs/`: Contains additional documentation, including design decisions and API usage.
- `api/`: Holds API wrappers for different languages.
    - `api/python/`: Python API wrapper.
    - `api/javascript/`: JavaScript API wrapper.
- `features/`: Contains Behave (BDD) feature files and step definitions for acceptance testing.
- `.github/workflows/`: GitHub Actions CI/CD pipeline definitions.

## Core Technologies
- **Go:** Primary language for core logic.
- **Python:** Used for Behave acceptance tests and a dedicated API wrapper.
- **JavaScript/Node.js:** Used for an API wrapper.
- **GitHub Copilot & Gemini CLI:** AI-powered development tools.
- **Behave:** Python-based BDD framework for acceptance testing.
- **GitHub Actions:** For CI/CD automation.

## Coding Style & Best Practices

### General
- **Readability:** Prioritize clear, concise, and self-documenting code.
- **Modularity:** Break down complex problems into smaller, testable functions/components.
- **Error Handling:** Implement robust error handling. Return errors explicitly in Go, use exceptions in Python/JS.
- **Comments:** Use comments to explain *why* something is done, not *what* is done (unless the "what" is complex).
- **Test-Driven Development (TDD) / Behavior-Driven Development (BDD):** Encourage writing tests *before* or concurrently with writing new features.
- **Naming Conventions:** Follow standard conventions for each language (e.g., `CamelCase` for Go types/functions, `snake_case` for Python functions/variables).

### Go Specific
- **Gofmt & Golint:** Adhere to standard Go formatting and linting rules.
- **Explicit Imports:** Avoid unused imports.
- **Concurrency:** Use Go's concurrency primitives (`goroutines`, `channels`) judiciously and safely.
- **Context:** Use `context.Context` for cancellation and request-scoped values.

### Python Specific
- **PEP 8:** Adhere strictly to PEP 8 style guidelines.
- **Virtual Environments:** Always assume development happens within a virtual environment.
- **Type Hinting:** Use type hints for better code clarity and maintainability.

### JavaScript Specific
- **ES Modules:** Prefer ES module syntax (`import`/`export`).
- **ESLint:** Assume ESLint is configured and follow its rules.
- **Async/Await:** Prefer `async/await` for asynchronous operations.

## GitHub Copilot Usage Guidelines

- **Context Awareness:** When providing suggestions, consider the surrounding code, comments, and the project's overall structure.
- **Language Specificity:** Provide suggestions tailored to the specific language of the file being edited (Go, Python, JavaScript).
- **Adherence to Instructions:** Always prioritize the guidelines in this file. If a suggestion conflicts with these instructions, try to refine it.
- **Boilerplate & Patterns:** Focus on generating boilerplate code, common patterns, and repetitive structures.
- **Testing Focus:** When generating code, consider how it will be tested. Suggesting accompanying test stubs or test cases is highly valued.
- **Error Handling Suggestions:** Include appropriate error handling in generated code.
- **Security:** Be mindful of common security vulnerabilities and suggest secure coding practices.
- **No Hallucinations:** Avoid generating non-existent functions, libraries, or APIs.
- **Conciseness:** Keep suggestions concise and to the point, avoiding excessive verbosity.
- **Suggest full functions/methods:** Where appropriate, suggest complete function or method bodies based on the function signature or preceding comments.

---
**NOTE:** This `copilot-instructions.md` file is intended to guide GitHub Copilot's suggestions and is subject to evolution as the project grows and its conventions solidify.