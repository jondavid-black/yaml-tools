import os
import sys

# Add src to path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src/"))
)

from io import StringIO

from yasl import yasl_eval


def test_presence_required_valid():
    schema_path = "tests/yasl/data/presence_required.yasl"
    data_path = "tests/yasl/data/presence_required_valid.yaml"

    # Should pass
    result = yasl_eval(schema_path, data_path, "person", quiet_log=True)
    assert result is not None


def test_presence_required_warn():
    schema_path = "tests/yasl/data/presence_required.yasl"
    data_path = "tests/yasl/data/presence_required_warn.yaml"

    stream = StringIO()
    # Should pass but warn
    result = yasl_eval(schema_path, data_path, "person", log_stream=stream)

    assert result is not None
    log_output = stream.getvalue()
    assert "Preferred property 'email' is missing at line 1" in log_output


def test_presence_required_invalid():
    schema_path = "tests/yasl/data/presence_required.yasl"
    data_path = "tests/yasl/data/presence_required_invalid.yaml"

    # Should fail
    result = yasl_eval(schema_path, data_path, "person", quiet_log=True)
    assert result is None
