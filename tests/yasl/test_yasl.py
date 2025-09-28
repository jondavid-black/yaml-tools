import subprocess
import sys
import tempfile
import os
from io import StringIO
from pathlib import Path
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src/")))

from yasl import yasl_eval
from yasl.cli import main as yasl_cli_main

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
    description: Information about a customer.
    properties:
      - name: name
        type: str
        description: The customer's name.
        required: true
        unique: true
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
    description: A list of customers.
    properties:
      - name: customers
        type: customer[]
        description: Information about a customer.
        list_min: 2
        list_max: 3
  - name: account
    namespace: acme
    description: Information about an account.
    properties:
      - name: id
        type: str
        description: The unique identifier for the account.
        required: true
      - name: account_rep
        type: str
        description: The name of the account representative.
        required: true
      - name: customer_name
        type: ref(customer.name)
        description: The name of the customer associated with the account.
        required: true
  - name: business
    namespace: acme
    description: A list of accounts.
    properties:
      - name: business_name
        type: str
        description: The name of the business.
        required: true
      - name: customers
        type: customer[]
        description: Information about a list of customers.
        required: true
      - name: accounts
        type: account[]
        description: Information about an account.
        required: true
"""

PERSON_YASL = """
types:
  - name: person
    namespace: acme
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
      - name: favorite_time
        type: time
        description: The person's favorite time of day.
        required: false
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

SHAPE_YASL = """
types:
  - name: shape
    namespace: acme
    description: Information about a shape.
    properties:
      - name: name
        type: str
        description: The name of the shape.
        required: true
      - name: type
        type: ShapeType
        description: The type of shape.
        required: true
      - name: radius
        type: float
        description: The radius of the circle.
        required: false
        gt: 0
      - name: side_length
        type: float
        description: The length of the side of the square or triangle.
        required: false
        gt: 0
      - name: color
        type: str
        description: The color of the shape.
        required: false
      - name: colour
        type: str
        description: The color of the shape (British spelling).
        required: false
      - name: location
        type: str
        description: The location of the shape.
        required: false
      - name: orientation
        type: str
        description: The orientation of the shape.
        required: false
    validators:
      only_one:
        - color
        - colour
      at_least_one:
        - location
        - orientation
      if_then:
        - eval: type
          value: 
           - circle
          present:
            - radius
          absent:
            - side_length
        - eval: type
          value: 
            - square
            - triangle
          present:
            - side_length
          absent:
            - radius
enums:
  - name: ShapeType
    namespace: acme
    description: The type of shape.
    values:
      - circle
      - square
      - triangle
"""

TODO_YASL = """
types:
  - name: task
    description: A thing to do.
    namespace: dynamic
    properties:
      - name: description
        type: str
        description: A description of the task.
        required: true
      - name: owner
        type: str
        description: The person responsible for the task.
        required: false
      - name: complete
        type: bool
        description: Is the task finished? True if yes, false if no.
        required: true
        default: false
  - name: list_of_tasks
    description: A list of tasks to complete.
    namespace: dynamic
    properties:
      - name: task_list
        type: map(str, task)
        description: A list of tasks to do.
        required: true
"""

def run_cli(args):
    filtered_args = [item for item in args if item is not None]
    result = subprocess.run(
        ["yasl"] + filtered_args,
        capture_output=True,
        text=True
    )
    return result

def test_cli_version(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["yasl", "--version"])
    with pytest.raises(SystemExit) as e:
        yasl_cli_main()
    assert e.value.code == 0
    captured = capsys.readouterr()
    assert "YASL version" in captured.out

def test_cli_quiet_and_verbose(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["yasl", "--quiet", "--verbose"])
    with pytest.raises(SystemExit) as e:
        yasl_cli_main()
    assert e.value.code == 1
    captured = capsys.readouterr()
    assert "❌ Cannot use both --quiet and --verbose." in captured.out

def test_cli_missing_args(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["yasl", "./file.yasl"])
    with pytest.raises(SystemExit) as e:
        yasl_cli_main()
    assert e.value.code == 1
    captured = capsys.readouterr()
    assert "❌ requires a YASL file, a YAML schema file, and optionally a model name as parameters." in captured.out

def test_cli_good(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["yasl", "./features/data/todo.yasl", "./features/data/todo.yaml", "list_of_tasks"])
    with pytest.raises(SystemExit) as e:
        yasl_cli_main()
    assert e.value.code == 0

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

        run_eval_command_with_paths(yaml_path, yasl_path, model_name, expect_valid)


def run_eval_command_with_paths(yaml_path, yasl_path, model_name, expect_valid):
    
    # Test via the API
    test_log = StringIO()
    yasl_model = yasl_eval(yasl_path, yaml_path, model_name, verbose_log=True, output="text", log_stream=test_log)
    if not expect_valid:
        assert yasl_model is None
        assert "❌" in test_log.getvalue()
    else:
        assert yasl_model is not None
        assert "data validation successful" in test_log.getvalue()

    # Test via the CLI
    result = run_cli([yasl_path, yaml_path, model_name])
    if not expect_valid:
        assert result.returncode != 0
        assert "❌" in result.stdout
    else:
        assert result.returncode == 0
        assert "data validation successful" in result.stdout

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

def test_eval_non_unique():
    yaml_data = """
customers:
  - name: Bob Smith
    age: 30
    email: bob@example.com
    status: unknown
  - name: Bob Smith
    age: 40
    email: joe@example.com
    status: inactive
"""
    yasl_schema = CUSTOMER_LIST_YASL
    run_eval_command(yaml_data, yasl_schema, "customer_list", False)

def test_eval_business_good():
    yaml_data = """
business_name: Acme Corporation
customers:
  - name: Bob Smith
    age: 30
    email: bob@example.com
    status: inactive
  - name: Alice Johnson
    age: 25
    email: alice@example.com
    status: active
accounts:
  - id: ACC123
    account_rep: John Doe
    customer_name: Bob Smith
  - id: ACC456
    account_rep: Jane Doe
    customer_name: Alice Johnson
"""
    yasl_schema = CUSTOMER_LIST_YASL
    run_eval_command(yaml_data, yasl_schema, "business", True)

def test_eval_business_bad_ref():
    yaml_data = """
business_name: Acme Corporation
customers:
  - name: Bob Smith
    age: 30
    email: bob@example.com
    status: inactive
  - name: Alice Johnson
    age: 25
    email: alice@example.com
    status: active
accounts:
  - id: ACC123
    account_rep: John Doe
    customer_name: Dan Smith
  - id: ACC456
    account_rep: Jane Doe
    customer_name: Alice Johnson
"""
    yasl_schema = CUSTOMER_LIST_YASL
    run_eval_command(yaml_data, yasl_schema, "business", False)

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

def test_eval_favorite_time_good():
    yaml_data = """
name: Joe Smith
age: 24
favorite_time: 12:30:00
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", True)

def test_eval_favorite_time_early():
    yaml_data = """
name: Joe Smith
age: 24
favorite_time: 06:30:00
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", True)

def test_eval_favorite_time_late():
    yaml_data = """
name: Joe Smith
age: 24
favorite_time: 16:30:00
"""
    yasl_schema = PERSON_YASL
    run_eval_command(yaml_data, yasl_schema, "person", True)

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

def test_eval_shape_good():
    yaml_data = """
name: bob
type: square
side_length: 10.0
color: red
location: top-left
"""
    yasl_schema = SHAPE_YASL
    run_eval_command(yaml_data, yasl_schema, "shape", True)

def test_eval_shape_only_one_fail():
    yaml_data = """
name: bob
type: square
side_length: 10.0
color: red
colour: blue
location: top-left
"""
    yasl_schema = SHAPE_YASL
    run_eval_command(yaml_data, yasl_schema, "shape", False)

def test_eval_shape_at_least_one_fail():
    yaml_data = """
name: bob
type: square
side_length: 10.0
color: red
"""
    yasl_schema = SHAPE_YASL
    run_eval_command(yaml_data, yasl_schema, "shape", False)

def test_eval_shape_if_then_1_fail():
    yaml_data = """
name: bob
type: circle
side_length: 10.0
color: red
"""
    yasl_schema = SHAPE_YASL
    run_eval_command(yaml_data, yasl_schema, "shape", False)

def test_eval_shape_if_then_2_fail():
    yaml_data = """
name: bob
type: square
radius: 10.0
color: red
"""
    yasl_schema = SHAPE_YASL
    run_eval_command(yaml_data, yasl_schema, "shape", False)

def test_eval_shape_if_then_3_fail():
    yaml_data = """
name: bob
type: triangle
radius: 10.0
color: red
"""
    yasl_schema = SHAPE_YASL
    run_eval_command(yaml_data, yasl_schema, "shape", False)

def test_version_command():
    result = run_cli(["--version"])
    assert result.returncode == 0
    assert "YASL version" in result.stdout

def test_pydantic_types():
    yasl = """
types:
  - name: thing
    namespace: acme
    description: Information about a thing.
    properties:
      - name: id
        type: str
        description: The unique identifier for the thing.
        required: true
      - name: strict_bool
        type: StrictBool
        description: A strict boolean value.
        required: false
      - name: markdown
        type: markdown
        description: A markdown value
        required: false
      - name: positive_int
        type: PositiveInt
        description: A positive integer value.
        required: false
      - name: negative_int
        type: NegativeInt
        description: A negative integer value.
        required: false
      - name: non_positive_int
        type: NonPositiveInt
        description: A non-positive integer value.
        required: false
      - name: non_negative_int
        type: NonNegativeInt
        description: A non-negative integer value.
        required: false
      - name: strict_int
        type: StrictInt
        description: A strict integer value.
        required: false
      - name: positive_float
        type: PositiveFloat
        description: A positive float value.
        required: false
      - name: negative_float
        type: NegativeFloat
        description: A negative float value.
        required: false
      - name: non_positive_float
        type: NonPositiveFloat
        description: A non-positive float value.
        required: false
      - name: non_negative_float
        type: NonNegativeFloat
        description: A non-negative float value.
        required: false
      - name: strict_float
        type: StrictFloat
        description: A strict float value.
        required: false
      - name: finite_float
        type: FiniteFloat
        description: A finite float value (not NaN or infinite).
        required: false
      - name: strict_str
        type: StrictStr
        description: A strict string value.
        required: false
      - name: uuid1
        type: UUID1
        description: A UUID version 1.
        required: false
      - name: uuid3
        type: UUID3
        description: A UUID version 3.
        required: false
      - name: uuid4
        type: UUID4
        description: A UUID version 4.
        required: false
      - name: uuid5
        type: UUID5
        description: A UUID version 5.
        required: false
      - name: uuid6
        type: UUID6
        description: A UUID version 6.
        required: false
      - name: uuid7   
        type: UUID7
        description: A UUID version 7.
        required: false
      - name: uuid8
        type: UUID8
        description: A UUID version 8.
        required: false
      - name: file_path
        type: FilePath
        description: A valid file path.
        required: false
      - name: directory_path
        type: DirectoryPath
        description: A valid directory path.
        required: false
      - name: base64_bytes
        type: Base64Bytes
        description: A base64 encoded byte string.
        required: false
      - name: base64_str
        type: Base64Str
        description: A base64 encoded string.
        required: false
      - name: base64_url_bytes
        type: Base64UrlBytes
        description: A base64 URL-safe encoded byte string.
        required: false
      - name: base64_url_str
        type: Base64UrlStr
        description: A base64 URL-safe encoded string.
        required: false
      - name: any_url
        type: AnyUrl
        description: Any valid URL.
        required: false
      - name: any_http_url
        type: AnyHttpUrl
        description: Any valid HTTP or HTTPS URL.
        required: false
      - name: http_url
        type: HttpUrl
        description: A valid HTTP or HTTPS URL.
        required: false
      - name: any_websocket_url
        type: AnyWebsocketUrl
        description: Any valid WebSocket or secure WebSocket URL.
        required: false
      - name: websocket_url
        type: WebsocketUrl
        description: A valid WebSocket or secure WebSocket URL.
        required: false
      - name: file_url
        type: FileUrl
        description: A valid file URL.
        required: false
      - name: ftp_url
        type: FtpUrl
        description: A valid FTP or FTPS URL.
        required: false
      - name: postgres_dsn
        type: PostgresDsn
        description: A valid PostgreSQL DSN.
        required: false
      - name: cockroach_dsn
        type: CockroachDsn
        description: A valid CockroachDB DSN.
        required: false
      - name: amqp_dsn
        type: AmqpDsn
        description: A valid AMQP DSN.
        required: false
      - name: redis_dsn
        type: RedisDsn
        description: A valid Redis DSN.
        required: false
      - name: mongo_dsn
        type: MongoDsn
        description: A valid MongoDB DSN.
        required: false
      - name: kafka_dsn
        type: KafkaDsn
        description: A valid Kafka DSN.
        required: false
      - name: nats_dsn
        type: NatsDsn
        description: A valid NATS DSN.
        required: false
      - name: mysql_dsn
        type: MySQLDsn
        description: A valid MySQL DSN.
        required: false
      - name: mariadb_dsn
        type: MariaDBDsn
        description: A valid MariaDB DSN.
        required: false
      - name: clickhouse_dsn
        type: ClickHouseDsn
        description: A valid ClickHouse DSN.
        required: false
      - name: snowflake_dsn
        type: SnowflakeDsn
        description: A valid Snowflake DSN.
        required: false
      - name: email_str
        type: EmailStr
        description: A valid email address.
        required: false
      - name: name_email
        type: NameEmail
        description: A valid name and email address.
        required: false
      - name: ipvany_address
        type: IPvAnyAddress
        description: A valid IPv4 or IPv6 address.
        required: false
"""
    yaml_data = """
id: test
strict_bool: true
markdown: |
  # Hello World
  
  This is some random markdown.
  [Link to Google](https://www.google.com)
      
positive_int: 42
negative_int: -42
non_positive_int: -1
non_negative_int: 0
strict_int: 100
positive_float: 3.14
negative_float: -3.14
non_positive_float: -0.1
non_negative_float: 0.0
strict_float: 2.718
finite_float: 1.618
strict_str: "Hello, World!"
uuid1: "550e8400-e29b-11d4-a716-446655440000"
uuid3: "550e8400-e29b-31d4-a716-446655440000"
uuid4: "550e8400-e29b-41d4-a716-446655440000"
uuid5: "550e8400-e29b-51d4-a716-446655440000"
uuid6: "550e8400-e29b-61d4-a716-446655440000"
uuid7: "550e8400-e29b-71d4-a716-446655440000"
uuid8: "550e8400-e29b-81d4-a716-446655440000"
file_path: "./features/data/thing.yaml"
directory_path: "./features/data/"
base64_bytes: "SGVsbG8sIFdvcmxkIQ=="
base64_str: "SGVsbG8sIFdvcmxkIQ=="
base64_url_bytes: "SHc_dHc-TXc=="
base64_url_str: "SHc_dHc-TXc=="
any_url: "https://example.com"
any_http_url: "http://example.com"
http_url: "http://example.com"
any_websocket_url: "ws://example.com/socket"
websocket_url: "ws://example.com/socket"
file_url: "file:///path/to/file.txt"
ftp_url: "ftp://example.com/resource"
postgres_dsn: "postgresql://user:password@localhost:5432/dbname"
cockroach_dsn: "cockroachdb://user:password@localhost:26257/dbname"
amqp_dsn: "amqp://user:password@localhost:5672/vhost"
redis_dsn: "redis://localhost:6379/0"
mongo_dsn: "mongodb://mongodb0.example.com:27017"
kafka_dsn: "kafka://localhost:9092"
nats_dsn: "nats://localhost:4222"
mysql_dsn: "mysql://user:password@localhost:3306/dbname"
mariadb_dsn: "mariadb://user:password@localhost:3306/dbname"
clickhouse_dsn: "clickhouse://user:password@localhost:8123/dbname"
snowflake_dsn: "snowflake://user:password@account/dbname/schema?warehouse=wh"
email_str: "user@example.com"
name_email: "User <user@example.com>"
ipvany_address: "192.0.2.1"
"""
    run_eval_command(yaml_data, yasl, "thing", True)

def test_dir_inputs_good():
    yasl_path = "./data/dir_test"
    yaml_path = "./data/dir_test"
    cwd = os.getcwd()
    os.chdir(str((Path(__file__).parent.parent.parent / "features").resolve()))
    run_eval_command_with_paths(str(Path(yasl_path).absolute()), str(Path(yaml_path).absolute()), None, True)
    os.chdir(cwd)

def test_dir_inputs_bad():
    yasl_path = "./data/bad_dir_test"
    yaml_path = "./data/bad_dir_test"
    cwd = os.getcwd()

    os.chdir(str((Path(__file__).parent.parent.parent / "features").resolve()))
    run_eval_command_with_paths(str(Path(yasl_path).absolute()), str(Path(yaml_path).absolute()), None, False)
    os.chdir(cwd)

def test_map_type__str_good():
    yasl = TODO_YASL
    yaml_data = """
task_list:
  task_01:
    description:  Buy coffee.
    owner: Jim
    complete: false
  task_02:
    description: Lead morning standup.
    owner: Jim
    complete: false
  task_03:
    description: Refine Backlog.
    owner: Jim
    complete: false
"""
    run_eval_command(yaml_data, yasl, "list_of_tasks", True)

def test_map_type_int_good():
    yasl = """
types:
  - name: task
    description: A thing to do.
    namespace: dynamic
    properties:
      - name: description
        type: str
        description: A description of the task.
        required: true
      - name: owner
        type: str
        description: The person responsible for the task.
        required: false
      - name: complete
        type: bool
        description: Is the task finished? True if yes, false if no.
        required: true
        default: false
  - name: list_of_tasks
    description: A list of tasks to complete.
    namespace: dynamic
    properties:
      - name: task_list
        type: map(int, task)
        description: A list of tasks to do.
        required: true
"""
    yaml_data = """
task_list:
  1:
    description:  Buy coffee.
    owner: Jim
    complete: false
  2:
    description: Lead morning standup.
    owner: Jim
    complete: false
  3:
    description: Refine Backlog.
    owner: Jim
    complete: false
"""
    run_eval_command(yaml_data, yasl, "list_of_tasks", True)

def test_map_type_bool_bad():
    yasl = """
types:
  - name: task
    description: A thing to do.
    namespace: dynamic
    properties:
      - name: description
        type: str
        description: A description of the task.
        required: true
      - name: owner
        type: str
        description: The person responsible for the task.
        required: false
      - name: complete
        type: bool
        description: Is the task finished? True if yes, false if no.
        required: true
        default: false
  - name: list_of_tasks
    description: A list of tasks to complete.
    namespace: dynamic
    properties:
      - name: task_list
        type: map(bool, task)
        description: A list of tasks to do.
        required: true
"""
    yaml_data = """
task_list:
  true:
    description:  Buy coffee.
    owner: Jim
    complete: false
  false:
    description: Lead morning standup.
    owner: Jim
    complete: false
"""
    run_eval_command(yaml_data, yasl, "list_of_tasks", False)

def test_map_type_bad():
    yasl = """
types:
  - name: task
    description: A thing to do.
    namespace: dynamic
    properties:
      - name: description
        type: str
        description: A description of the task.
        required: true
      - name: owner
        type: str
        description: The person responsible for the task.
        required: false
      - name: complete
        type: bool
        description: Is the task finished? True if yes, false if no.
        required: true
        default: false
  - name: list_of_tasks
    description: A list of tasks to complete.
    namespace: dynamic
    properties:
      - name: task_list
        type: map(str, junk_task)
        description: A list of tasks to do.
        required: true
"""
    yaml_data = """
task_list:
  task_01:
    description:  Buy coffee.
    owner: Jim
    complete: false
  task_02:
    description: Lead morning standup.
    owner: Jim
    complete: false
"""
    run_eval_command(yaml_data, yasl, "list_of_tasks", False)

def test_map_type_enum_key_good():
    yasl = """
types:
  - name: task
    description: A thing to do.
    namespace: dynamic
    properties:
      - name: description
        type: str
        description: A description of the task.
        required: true
      - name: owner
        type: str
        description: The person responsible for the task.
        required: false
      - name: complete
        type: bool
        description: Is the task finished? True if yes, false if no.
        required: true
        default: false
  - name: list_of_tasks
    description: A list of tasks to complete.
    namespace: dynamic
    properties:
      - name: task_list
        type: map(taskkey, task)
        description: A list of tasks to do.
        required: true
enums:
  - name: taskkey
    namespace: acme
    description: The type of shape.
    values:
      - task_01
      - task_02
"""
    yaml_data = """
task_list:
  task_01:
    description:  Buy coffee.
    owner: Jim
    complete: false
  task_02:
    description: Lead morning standup.
    owner: Jim
    complete: false
"""
    run_eval_command(yaml_data, yasl, "list_of_tasks", True)

def test_map_type_enum_value_bad():
    yasl = """
types:
  - name: task
    description: A thing to do.
    namespace: dynamic
    properties:
      - name: description
        type: str
        description: A description of the task.
        required: true
      - name: owner
        type: str
        description: The person responsible for the task.
        required: false
      - name: complete
        type: bool
        description: Is the task finished? True if yes, false if no.
        required: true
        default: false
  - name: list_of_tasks
    description: A list of tasks to complete.
    namespace: dynamic
    properties:
      - name: task_list
        type: map(taskkey, task)
        description: A list of tasks to do.
        required: true
enums:
  - name: taskkey
    namespace: acme
    description: The type of shape.
    values:
      - task_01
      - task_02
"""
    yaml_data = """
task_list:
  task_01:
    description:  Buy coffee.
    owner: Jim
    complete: false
  task_03:
    description: Lead morning standup.
    owner: Jim
    complete: false
"""
    run_eval_command(yaml_data, yasl, "list_of_tasks", False)

def test_map_nested_value_good():
    yasl = """
types:
  - name: task
    description: A thing to do.
    namespace: dynamic
    properties:
      - name: description
        type: str
        description: A description of the task.
        required: true
      - name: owner
        type: str
        description: The person responsible for the task.
        required: false
      - name: complete
        type: bool
        description: Is the task finished? True if yes, false if no.
        required: true
        default: false
  - name: feature
    description: A list of tasks to complete.
    namespace: dynamic
    properties:
      - name: feature
        type: str
        description: The feature name.
        required: true
      - name: task_list
        type: map(str, task)
        description: A list of tasks to do.
        required: true
  - name: project
    description: A project with tasks.
    namespace: dynamic
    properties:
      - name: project_name
        type: str
        description: The name of the project.
        required: true
      - name: features
        type: feature[]
        description: The tasks for the project.
        required: true
"""
    yaml_data = """
project_name: Important Project
features:
  - feature: Initial Setup
    task_list:
      task_01:
        description:  Buy coffee.
        owner: Jim
        complete: false
      task_02:
        description: Lead morning standup.
        owner: Jim
        complete: false
"""
    run_eval_command(yaml_data, yasl, "project", True)

def test_empty_markdown():
    yasl = """
types:
  - name: thing
    namespace: acme
    description: Information about a thing.
    properties:
      - name: id
        type: str
        description: The unique identifier for the thing.
        required: true
      - name: markdown
        type: markdown
        description: A markdown value
        required: true
"""
    yaml_data = """
id: test
markdown: ""
"""
    run_eval_command(yaml_data, yasl, "thing", False)