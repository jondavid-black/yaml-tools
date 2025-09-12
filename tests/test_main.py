import subprocess
import sys
import pytest
import tempfile
import os

CUSTOMER_LIST_YASL = """
enums:
  - name: customer_status
    namespace: acme
    description: The status of the customer.
    values:
      - active
      - inactive
types:
  - name: customer
    namespace: acme
    root: true
    description: Information about a customer.
    properties:
      - name: name
        type: str
        description: The customer's name.
        required: true
      - name: age
        type: int
        description: The customer's age.
        required: false
      - name: email
        type: str
        description:  The customer's email address.
        required: true
      - name: status
        type: customer_status
        namespace: acme
        description: The customer's status.
        required: true
  - name: customer_list
    namespace: acme
    root: true
    description: A list of customers.
    properties:
      - name: customers
        type: customer[]
        description: Information about a customer.
        list_min: 2
        list_max: 3
"""

PERSON_YASL = """
types:
  - name: person
    namespace: acme
    root: true
    description: Information about a person.
    properties:
      - name: name
        type: str
        description: The person's name.
        required: true
        str_min: 5
        str_max: 15
        str_regex: '^[A-Za-z ]+$'
      - name: age
        type: int
        description: The person's age.
        required: true
        ge: 18
        lt: 125
        whole_number: true
        multiple_of: 2
        exclude:
            - 64
      - name: birthday
        type: date
        description: The person's birthday.
        required: false
        after: "1900-01-01"
        before: "2050-12-31"
"""

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

def run_eval_command(yaml_data, yasl_schema, model_name, expect_valid):
    
    with tempfile.TemporaryDirectory() as tmpdir:
        yaml_path = os.path.join(tmpdir, "test.yaml")
        yasl_path = os.path.join(tmpdir, "test.yasl")
        with open(yaml_path, "w") as f:
            f.write(yaml_data)
        with open(yasl_path, "w") as f:
            f.write(yasl_schema)
        result = run_cli(["eval", yaml_path, yasl_path, model_name])
        if not expect_valid:
            assert result.returncode != 0
            assert "Validation failed" in result.stderr
        else:
            assert result.returncode == 0
            assert "YAML data validation successful" in result.stderr

def test_eval_nested_types_and_enum():
    yaml_data = """
customers:
  - name: Bob Smith
    age: 30
    email: bob@example.com
    status: active
  - name: Joe Smith
    age: 40
    email: joe@example.com
    status: inactive
"""
    yasl_schema = CUSTOMER_LIST_YASL
    run_eval_command(yaml_data, yasl_schema, "customer_list", True)

def test_eval_nested_types_with_bad_enum():
    yaml_data = """
customers:
  - name: Bob Smith
    age: 30
    email: bob@example.com
    status: unknown
  - name: Joe Smith
    age: 40
    email: joe@example.com
    status: inactive
"""
    yasl_schema = CUSTOMER_LIST_YASL
    run_eval_command(yaml_data, yasl_schema, "customer_list", False)

def test_eval_min_list():
    yaml_data = """
customers:
  - name: Bob Smith
    age: 30
    email: bob@example.com
    status: active
"""
    yasl_schema = CUSTOMER_LIST_YASL
    run_eval_command(yaml_data, yasl_schema, "customer_list", False)

def test_eval_max_list():
    yaml_data = """
customers:
  - name: Bob Smith
    age: 30
    email: bob@example.com
    status: active
  - name: Joe Smith
    age: 30
    email: joe@example.com
    status: active
  - name: Tom Smith
    age: 30
    email: tom@example.com
    status: active
  - name: Rob Smith
    age: 30
    email: rob@example.com
    status: active
"""
    yasl_schema = CUSTOMER_LIST_YASL
    run_eval_command(yaml_data, yasl_schema, "customer_list", False)

def test_eval_person_good():
    yaml_data = """
name: John Doe
age: 20
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", True)

def test_eval_age_too_small():
    yaml_data = """
name: John Doe
age: 10
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", False)

def test_eval_age_too_big():
    yaml_data = """
name: John Doe
age: 130
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", False)

def test_eval_age_excluded():
    yaml_data = """
name: John Doe
age: 64
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", False)

def test_eval_age_float():
    yaml_data = """
name: John Doe
age: 34.2
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", False)

def test_eval_age_odd():
    yaml_data = """
name: John Doe
age: 35
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", False)

def test_eval_name_short():
    yaml_data = """
name: Joe
age: 25
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", False)

def test_eval_name_long():
    yaml_data = """
name: Joseph Reginold Smithington the Third
age: 25
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", False)

def test_eval_name_invalid():
    yaml_data = """
name: Joe-Smith123
age: 25
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", False)

def test_eval_birthday_good():
    yaml_data = """
name: Joe-Smith123
age: 25
birthday: 1970-01-01
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", False)

def test_eval_birthday_before():
    yaml_data = """
name: Joe-Smith123
age: 25
birthday: 1800-01-01
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", False)

def test_eval_birthday_after():
    yaml_data = """
name: Joe-Smith123
age: 25
birthday: 2800-01-01
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", False)

def test_version_command():
    result = run_cli(["version"])
    assert result.returncode == 0
    assert "YASL version" in result.stderr
