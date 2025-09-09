import subprocess
import sys
import pytest

def run_cli(args):
    result = subprocess.run(
        [sys.executable, "./src/yasl/main.py"] + args,
        capture_output=True,
        text=True
    )
    return result

def test_init_command():
    result = run_cli(["init", "proj_name"])
    assert result.returncode == 0
    assert "Initializing YASL project" in result.stderr

def test_check_command_missing_param():
    result = run_cli(["check"])
    assert result.returncode != 0
    assert "requires a YAML file" in result.stderr

def test_package_command_missing_param():
    result = run_cli(["package"])
    assert result.returncode != 0
    assert "requires a YAML file" in result.stderr

def test_import_command_missing_param():
    result = run_cli(["import"])
    assert result.returncode != 0
    assert "requires a URI" in result.stderr

def test_quiet_and_verbose():
    result = run_cli(["init", "--quiet", "--verbose"])
    assert result.returncode != 0
    assert "Cannot use both" in result.stderr

def test_eval_command_missing_params():
    # Missing both params
    result = run_cli(["eval"])
    assert result.returncode != 0
    assert "requires a YAML file, a YASL schema file, and a model name" in result.stderr
    # Missing schema param
    result = run_cli(["eval", "foo.yaml"])
    assert result.returncode != 0
    assert "requires a YAML file, a YASL schema file, and a model name" in result.stderr

def test_eval_command_success():
    # Should print evaluation message (no actual file needed for this test)
    result = run_cli(["eval", "./features/data/customer_basic.yaml", "./features/data/customer_basic.yasl", "customer_list"])
    assert result.returncode == 0
    assert "YAML data validation successful" in result.stderr

def test_version_command():
    result = run_cli(["version"])
    assert result.returncode == 0
    assert "YASL version" in result.stderr
