# YASL Developer Contribution Guide

At this time YASL is a experimental project.
While it is intented to provide a valuable technical capibility, it is also a workspace to explore and refine developer workflows using GenAI coding assistants.
This project primarily uses GitHub Copilot with [instructions](./.github/copilot-instructions.md) intended to drive quality above quantity with GenAI contribution.
Additional Gemini 2.5 Pro is used for supporting research and concept exploration.

Designed for high performance in Go, YASL also provides convenient wrappers for Python and JavaScript, making it easy to integrate adavnced YAML definition and validation into a variety of environments.

## Developer Setup

The following core dependencies are required:

- Git (obviously)
- Go 1.22.2 or higher
- Python 3.12.3 or higher w/ pip 24.0 or higher
- NodeJS 20.29.4 or higher

The following developer tools are recommended:

- VScode - Code editor.
- GitHub Copilot - GenAI coding assistant.
- Act - Local GitHub Actions runner.