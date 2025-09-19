# YAML-TOOLS Project Instructions for GitHub Copilot

## Project Overview
This project, YAML-TOOLS, aims to provide robust collection of YAML validation, procssing, and manipulation capabilities. YAML-TOOLS is written in Python. 
We emphasize clean code, strong typing, comprehensive testing, and clear documentation.

## Project Structure
The project follows a modular structure:
- `src/`: Contains the python source code for YAML-TOOLS.
- `src/yasl/`: Contains the core YASL (YAML Advanced Scripting Language) implementation.
- `src/yaql/`: Contains the core YAQL (YAML Advanced Query Language) implementation.
- 'src/yarl/': Contains the core YARL (YAML Advanced Reporting Language) implementation.
- `README.md`: Project documentation and usage instructions.
- `docs/`: Contains YAML-TOOLS documentation in Markdown for publication in GitHub Pages.
- `tests/`: Contains the python unit test code for YAML-TOOLS.
- `tests/yasl/`: Contains unit tests for the YASL implementation.
- `tests/yaql/`: Contains unit tests for the YAQL implementation.
- `tests/yarl/`: Contains unit tests for the YARL implementation.
- `features/`: Contains Behave (BDD) feature files and step definitions for acceptance testing.
- `.github/workflows/`: GitHub Actions CI/CD pipeline definitions.

## Core Technologies
- **Python:** Language used to implement YASL.
- **UV:** Python environment for development and testing.
- **Pydantic:** Data validation and settings management using Python type annotations.
- **ruamel.yaml:** YAML 1.2 parser and emitter for Python.
- **Behave:** Python-based BDD framework for acceptance testing.
- **GitHub Copilot & Gemini CLI:** AI-powered development tools.
- **GitHub Actions:** For CI/CD automation.

## Coding Style & Best Practices

### General
- **Readability:** Prioritize clear, concise, and self-documenting code.
- **Modularity:** Break down complex problems into smaller, testable functions/components.
- **Error Handling:** Implement robust error handling.
- **Comments:** Use comments to explain *why* something is done, not *what* is done (unless the "what" is complex).
- **Test-Driven Development (TDD) / Behavior-Driven Development (BDD):** Encourage writing tests *before* or concurrently with writing new features.
- **Naming Conventions:** Follow standard conventions for each language (e.g., `snake_case` for Python functions/variables).

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