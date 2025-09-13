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
      - name: office
        type: any
        description: The person's office number, or true / false to indicate need.
        required: false
        any_of:
          - int
          - bool
      - name: bio
        type: path
        description: Path to a bio file.
        required: false
        is_file: true
        path_exists: false
        file_ext:
          - txt
          - md
      - name: home_directory
        type: path
        description: Path to the person's home directory.
        required: false
        is_dir: true
        path_exists: true
      - name: website
        type: url
        description: The person's website.
        required: false
        url_base: www.example.com
        url_protocols:
          - http
          - https
"""

def run_cli(args):
    result = subprocess.run(
        [sys.executable, "./src/yasl/cli.py"] + args,
        capture_output=True,
        text=True
    )
    print(f"DEBUG: stdout: {result.stdout}")
    print(f"DEBUG: stderr: {result.stderr}")
    return result

def test_quiet_and_verbose():
    result = run_cli(["file.yasl", "file.yaml", "--quiet", "--verbose"])
    assert result.returncode != 0
    assert "Cannot use both" in result.stdout

def run_eval_command(yaml_data, yasl_schema, model_name, expect_valid):
    
    with tempfile.TemporaryDirectory() as tmpdir:
        yaml_path = os.path.join(tmpdir, "test.yaml")
        yasl_path = os.path.join(tmpdir, "test.yasl")
        with open(yaml_path, "w") as f:
            f.write(yaml_data)
        with open(yasl_path, "w") as f:
            f.write(yasl_schema)
        result = run_cli([yasl_path, yaml_path, model_name])
        if not expect_valid:
            assert result.returncode != 0
            assert "Validation failed" in result.stdout
        else:
            assert result.returncode == 0
            assert "YAML data validation successful" in result.stdout

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
age: 24
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", False)

def test_eval_name_long():
    yaml_data = """
name: Joseph Reginold Smithington the Third
age: 24
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", False)

def test_eval_name_invalid():
    yaml_data = """
name: Joe-Smith123
age: 24
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", False)

def test_eval_birthday_good():
    yaml_data = """
name: Joe Smith
age: 24
birthday: 1970-01-01
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", True)

def test_eval_birthday_before():
    yaml_data = """
name: Joe Smith
age: 24
birthday: 1800-01-01
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", False)

def test_eval_birthday_after():
    yaml_data = """
name: Joe Smith
age: 24
birthday: 2800-01-01
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", False)

def test_eval_office_int_good():
    yaml_data = """
name: Joe Smith
age: 24
office: 42
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", True)

def test_eval_office_bool_good():
    yaml_data = """
name: Joe Smith
age: 24
office: true
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", True)

def test_eval_office_str():
    yaml_data = """
name: Joe Smith
age: 24
office: please
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", False)

def test_eval_office_float():
    yaml_data = """
name: Joe Smith
age: 24
office: 33.3
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", False)

def test_eval_bio_good():
    yaml_data = """
name: Joe Smith
age: 24
bio: ./myfile.txt
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", True)

def test_eval_bio_bad_ext():
    yaml_data = """
name: Joe Smith
age: 24
bio: ./myfile.docx
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", False)

def test_eval_home_dir_good():
    yaml_data = f"""
name: Joe Smith
age: 24
home_directory: {os.getcwd()}
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", True)

def test_eval_home_dir_not_exist():
    yaml_data = """
name: Joe Smith
age: 24
home_directory: /not/a/real/dir
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", False)

def test_eval_website_good():
    yaml_data = """
name: Joe Smith
age: 24
website: https://www.example.com/joe_smith
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", True)

def test_eval_website_bad_protocol():
    yaml_data = """
name: Joe Smith
age: 24
website: ftp://www.example.com/joe_smith
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", False)

def test_eval_website_reachable():
    yasl_schema = """
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
      - name: website
        type: url
        description: The person's website.
        required: false
        url_reachable: true
"""
    yaml_data = """
name: Joe Smith
website: https://www.google.com
"""
    run_eval_command(yaml_data, yasl_schema, "person", True)

def test_eval_website_bad_base():
    yaml_data = """
name: Joe Smith
age: 24
website: ftp://www.notexample.com/joe_smith
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", False)

def test_version_command():
    result = run_cli(["--version"])
    print(f"DEBUG: stdout: {result.stdout}")
    assert result.returncode == 0
    assert "YASL version" in result.stdout
