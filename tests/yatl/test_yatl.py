import subprocess


def run_cli(args):
    filtered_args = [item for item in args if item is not None]
    result = subprocess.run(["yatl"] + filtered_args, capture_output=True, text=True)
    return result


def test_version_command():
    result = run_cli(["--version"])
    assert result.returncode == 0
    assert "YATL version" in result.stdout
