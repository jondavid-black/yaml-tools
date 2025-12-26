from io import StringIO

from yasl import yasl_eval


def test_presence_optional_missing():
    schema_path = "tests/yasl/data/presence_optional.yasl"
    data_path = "tests/yasl/data/presence_optional_missing.yaml"

    stream = StringIO()
    # Should pass without warnings
    result = yasl_eval(schema_path, data_path, "person_optional", log_stream=stream)

    assert result is not None
    log_output = stream.getvalue()

    # Verify no warnings about missing optional fields
    assert "Preferred property 'nickname' is missing" not in log_output
    assert "Preferred property 'bio' is missing" not in log_output
    assert "Warning" not in log_output

    # Verify validation success
    assert "validation successful" in log_output


def test_presence_default_is_optional():
    # 'bio' has no presence attribute, so it should be optional by default
    schema_path = "tests/yasl/data/presence_optional.yasl"
    data_path = "tests/yasl/data/presence_optional_missing.yaml"

    stream = StringIO()
    result = yasl_eval(schema_path, data_path, "person_optional", log_stream=stream)

    assert result is not None
    # If bio was required, validation would fail.
    # If bio was preferred, we would see a warning (checked above).
