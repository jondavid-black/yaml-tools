#!/usr/bin/env bash

set -euo pipefail

# Print usage and exit
usage() {
    echo "Usage: $0 {test|lint|lint-fix|bdd|build|all}"
    exit 1
}

# Run unit tests
run_test() {
    echo "Running unit tests..."
    uv run pytest --cov=src/yasl --cov-report=xml --cov-fail-under=75 tests/yasl
}

# Run linter
run_lint() {
    echo "Running linter..."
    uv run ruff check src/yasl tests/yasl
}

# Run linter and fix
run_lint_fix() {
    echo "Running linter..."
    uv run ruff check src/yasl tests/yasl --fix
}

# Run BDD tests
run_bdd() {
    echo "Running BDD tests..."
    uv run behave ./features
}

# Build project (placeholder)
run_build() {
    echo "Building project..."
    uv run python -m build
}

# Run all CI steps
run_all() {
    run_test
    run_lint
    run_bdd
    run_build
}

# Main
if [[ $# -ne 1 ]]; then
    usage
fi

case "$1" in
    test)  run_test ;;
    lint)  run_lint ;;
    lint-fix)  run_lint_fix ;;
    bdd)   run_bdd ;;
    build) run_build ;;
    all) run_all ;;
    *)     usage ;;
esac