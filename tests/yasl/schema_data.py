CUSTOMER_LIST_YASL = """
definitions:
  acme:
    description: Acme Corporation schema definitions.
    enums:
      customer_status:
        description: The status of the customer.
        values:
          - active
          - inactive
    types:
      customer:
        description: Information about a customer.
        properties:
          name:
            type: str
            description: The customer's name.
            required: true
            unique: true
          age:
            type: int
            description: The customer's age.
            required: false
          email:
            type: str
            description:  The customer's email address.
            required: true
          status:
            type: customer_status
            description: The customer's status.
            required: true
      customer_list:
        description: A list of customers.
        properties:
          customers:
            type: customer[]
            description: Information about a customer.
            list_min: 2
            list_max: 3
      account:
        description: Information about an account.
        properties:
          id:
            type: str
            description: The unique identifier for the account.
            required: true
          account_rep:
            type: str
            description: The name of the account representative.
            required: true
          customer_name:
            type: ref[customer.name]
            description: The name of the customer associated with the account.
            required: true
      business:
        description: A list of accounts.
        properties:
          business_name:
            type: str
            description: The name of the business.
            required: true
          customers:
            type: customer[]
            description: Information about a list of customers.
            required: true
          accounts:
            type: account[]
            description: Information about an account.
            required: true
"""

NAMESPACE_CUSTOMER_LIST_YASL = """
definitions:
    acme:
        description: Acme Corporation schema definitions.
        enums:
            customer_status:
                description: The status of the customer.
                values:
                    - active
                    - inactive
        types:
            customer:
                description: Information about a customer.
                properties:
                    name:
                        type: str
                        description: The customer's name.
                        required: true
                        unique: true
                    age:
                        type: int
                        description: The customer's age.
                        required: false
                    email:
                        type: str
                        description:  The customer's email address.
                        required: true
                    status:
                        type: customer_status
                        description: The customer's status.
                        required: true
            customer_list:
                description: A list of customers.
                properties:
                    customers:
                        type: acme.customer[]
                        description: Information about a customer.
                        list_min: 2
                        list_max: 3
            account:
                description: Information about an account.
                properties:
                    id:
                        type: str
                        description: The unique identifier for the account.
                        required: true
                    account_rep:
                        type: str
                        description: The name of the account representative.
                        required: true
                    customer_name:
                        type: ref[acme.customer.name]
                        description: The name of the customer associated with the account.
                        required: true
            business:
                description: A list of accounts.
                properties:
                    business_name:
                        type: str
                        description: The name of the business.
                        required: true
                    customers:
                        type: acme.customer[]
                        description: Information about a list of customers.
                        required: true
                    accounts:
                        type: acme.account[]
                        description: Information about an account.
                        required: true
"""

PERSON_YASL = """
definitions:
    acme:
        description: Acme Corporation schema definitions.
        types:
            person:
                description: Information about a person.
                properties:
                    name:
                        type: str
                        description: The person's name.
                        required: true
                        str_min: 5
                        str_max: 15
                        str_regex: '^[A-Za-z ]+$'
                    age:
                        type: int
                        description: The person's age.
                        required: true
                        ge: 18
                        lt: 125
                        whole_number: true
                        multiple_of: 2
                        exclude:
                            - 64
                    birthday:
                        type: date
                        description: The person's birthday.
                        required: false
                        after: "1900-01-01"
                        before: "2050-12-31"
                    favorite_time:
                        type: time
                        description: The person's favorite time of day.
                        required: false
                    office:
                        type: any
                        description: The person's office number, or true / false to indicate need.
                        required: false
                        any_of:
                            - int
                            - bool
                    bio:
                        type: path
                        description: Path to a bio file.
                        required: false
                        is_file: true
                        path_exists: false
                        file_ext:
                            - txt
                            - md
                    home_directory:
                        type: path
                        description: Path to the person's home directory.
                        required: false
                        is_dir: true
                        path_exists: true
                    website:
                        type: url
                        description: The person's website.
                        required: false
                        url_base: www.example.com
                        url_protocols:
                            - http
                            - https
"""

PERSON_WEBSITE_REACHABLE_YAML = """
definitions:
    acme:
        description: Acme Corporation schema definitions.
        types:
            person:
                description: Information about a person.
                properties:
                    name:
                        type: str
                        description: The person's name.
                        required: true
                        str_min: 5
                        str_max: 15
                        str_regex: '^[A-Za-z ]+$'
                    website:
                        type: url
                        description: The person's website.
                        required: false
                        url_reachable: true
"""

SHAPE_YASL = """
definitions:
  acme:
    types:
      shape:
        description: Information about a shape.
        properties:
          name:
              type: str
              description: The name of the shape.
              required: true
          type:
              type: ShapeType
              description: The type of shape.
              required: true
          radius:
              type: float
              description: The radius of the circle.
              required: false
              gt: 0
          side_length:
              type: float
              description: The length of the side of the square or triangle.
              required: false
              gt: 0
          color:
              type: str
              description: The color of the shape.
              required: false
          colour:
              type: str
              description: The color of the shape (British spelling).
              required: false
          location:
              type: str
              description: The location of the shape.
              required: false
          orientation:
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
      ShapeType:
        description: The type of shape.
        values:
          - circle
          - square
          - triangle
"""

TODO_YASL = """
definitions:
    dynamic:
        types:
            task:
                description: A thing to do.
                properties:
                    description:
                        type: str
                        description: A description of the task.
                        required: true
                    owner:
                        type: str
                        description: The person responsible for the task.
                        required: false
                    complete:
                        type: bool
                        description: Is the task finished? True if yes, false if no.
                        required: true
                        default: false
            list_of_tasks:
                description: A list of tasks to complete.
                properties:
                    task_list:
                        type: map[str, task]
                        description: A list of tasks to do.
                        required: true
"""

TODO_ENUM_MAP_YASL = """
definitions:
    dynamic:
        types:
            task:
                description: A thing to do.
                properties:
                    description:
                        type: str
                        description: A description of the task.
                        required: true
                    owner:
                        type: str
                        description: The person responsible for the task.
                        required: false
                    complete:
                        type: bool
                        description: Is the task finished? True if yes, false if no.
                        required: true
                        default: false
            list_of_tasks:
                description: A list of tasks to complete.
                properties:
                    task_list:
                        type: map[taskkey, task]
                        description: A list of tasks to do.
                        required: true
        enums:
            taskkey:
                description: The type of shape.
                values:
                - task_01
                - task_02
"""

TODO_MIXED_NAMESPACE_YASL = """
definitions:
    something:
        types:
            task:
                description: A thing to do.
                properties:
                    description:
                        type: str
                        description: A description of the task.
                        required: true
                    owner:
                        type: str
                        description: The person responsible for the task.
                        required: false
                    complete:
                        type: bool
                        description: Is the task finished? True if yes, false if no.
                        required: true
                        default: false
    dynamic:
        types:
            list_of_tasks:
                description: A list of tasks to complete.
                properties:
                    task_list:
                        type: map[other.taskkey, something.task]
                        description: A list of tasks to do.
                        required: true
    other:
        enums:
            taskkey:
                description: The type of task.
                values:
                - task_01
                - task_02
                - task_03
"""

TODO_NESTED_MAP_YASL = """
definitions:
    dynamic:
        types:
            task:
                description: A thing to do.
                properties:
                    description:
                        type: str
                        description: A description of the task.
                        required: true
                    owner:
                        type: str
                        description: The person responsible for the task.
                        required: false
                    complete:
                        type: bool
                        description: Is the task finished? True if yes, false if no.
                        required: true
                        default: false
            feature:
                description: A list of tasks to complete.
                properties:
                    feature:
                        type: str
                        description: The feature name.
                        required: true
                    task_list:
                        type: map[str, task]
                        description: A list of tasks to do.
                        required: true
            project:
                description: A project with tasks.
                properties:
                    project_name:
                        type: str
                        description: The name of the project.
                        required: true
                    features:
                        type: feature[]
                        description: The tasks for the project.
                        required: true
"""

TODO_INT_MAP_YASL = """
definitions:
    dynamic:
        types:
            task:
                description: A thing to do.
                namespace: dynamic
                properties:
                    description:
                        type: str
                        description: A description of the task.
                        required: true
                    owner:
                        type: str
                        description: The person responsible for the task.
                        required: false
                    complete:
                        type: bool
                        description: Is the task finished? True if yes, false if no.
                        required: true
                        default: false
            list_of_tasks:
                description: A list of tasks to complete.
                namespace: dynamic
                properties:
                    task_list:
                        type: map[int, task]
                        description: A list of tasks to do.
                        required: true
"""

TODO_BOOL_MAP_YASL = """
definitions:
    dynamic:
        types:
            task:
                description: A thing to do.
                namespace: dynamic
                properties:
                    description:
                        type: str
                        description: A description of the task.
                        required: true
                    owner:
                        type: str
                        description: The person responsible for the task.
                        required: false
                    complete:
                        type: bool
                        description: Is the task finished? True if yes, false if no.
                        required: true
                        default: false
            list_of_tasks:
                description: A list of tasks to complete.
                namespace: dynamic
                properties:
                    task_list:
                        type: map[bool, task]
                        description: A list of tasks to do.
                        required: true
"""

TODO_BAD_MAP_VALUE_YASL = """
definitions:
    dynamic:
        types:
            task:
                description: A thing to do.
                namespace: dynamic
                properties:
                    description:
                        type: str
                        description: A description of the task.
                        required: true
                    owner:
                        type: str
                        description: The person responsible for the task.
                        required: false
                    complete:
                        type: bool
                        description: Is the task finished? True if yes, false if no.
                        required: true
                        default: false
            list_of_tasks:
                description: A list of tasks to complete.
                namespace: dynamic
                properties:
                    task_list:
                        type: map[str, junktask]
                        description: A list of tasks to do.
                        required: true
"""

PYDANTIC_TYPES_YASL = """
definitions:
    pydantic:
        types:
            thing:
                description: Information about a thing.
                properties:
                    id:
                        type: str
                        description: The unique identifier for the thing.
                        required: true
                    strict_bool:
                        type: StrictBool
                        description: A strict boolean value.
                        required: false
                    markdown:
                        type: markdown
                        description: A markdown value
                        required: false
                    positive_int:
                        type: PositiveInt
                        description: A positive integer value.
                        required: false
                    negative_int:
                        type: NegativeInt
                        description: A negative integer value.
                        required: false
                    non_positive_int:
                        type: NonPositiveInt
                        description: A non-positive integer value.
                        required: false
                    non_negative_int:
                        type: NonNegativeInt
                        description: A non-negative integer value.
                        required: false
                    strict_int:
                        type: StrictInt
                        description: A strict integer value.
                        required: false
                    positive_float:
                        type: PositiveFloat
                        description: A positive float value.
                        required: false
                    negative_float:
                        type: NegativeFloat
                        description: A negative float value.
                        required: false
                    non_positive_float:
                        type: NonPositiveFloat
                        description: A non-positive float value.
                        required: false
                    non_negative_float:
                        type: NonNegativeFloat
                        description: A non-negative float value.
                        required: false
                    strict_float:
                        type: StrictFloat
                        description: A strict float value.
                        required: false
                    finite_float:
                        type: FiniteFloat
                        description: A finite float value (not NaN or infinite).
                        required: false
                    strict_str:
                        type: StrictStr
                        description: A strict string value.
                        required: false
                    uuid1:
                        type: UUID1
                        description: A UUID version 1.
                        required: false
                    uuid3:
                        type: UUID3
                        description: A UUID version 3.
                        required: false
                    uuid4:
                        type: UUID4
                        description: A UUID version 4.
                        required: false
                    uuid5:
                        type: UUID5
                        description: A UUID version 5.
                        required: false
                    uuid6:
                        type: UUID6
                        description: A UUID version 6.
                        required: false
                    uuid7:
                        type: UUID7
                        description: A UUID version 7.
                        required: false
                    uuid8:
                        type: UUID8
                        description: A UUID version 8.
                        required: false
                    file_path:
                        type: FilePath
                        description: A valid file path.
                        required: false
                    directory_path:
                        type: DirectoryPath
                        description: A valid directory path.
                        required: false
                    base64_bytes:
                        type: Base64Bytes
                        description: A base64 encoded byte string.
                        required: false
                    base64_str:
                        type: Base64Str
                        description: A base64 encoded string.
                        required: false
                    base64_url_bytes:
                        type: Base64UrlBytes
                        description: A base64 URL-safe encoded byte string.
                        required: false
                    base64_url_str:
                        type: Base64UrlStr
                        description: A base64 URL-safe encoded string.
                        required: false
                    any_url:
                        type: AnyUrl
                        description: Any valid URL.
                        required: false
                    any_http_url:
                        type: AnyHttpUrl
                        description: Any valid HTTP or HTTPS URL.
                        required: false
                    http_url:
                        type: HttpUrl
                        description: A valid HTTP or HTTPS URL.
                        required: false
                    any_websocket_url:
                        type: AnyWebsocketUrl
                        description: Any valid WebSocket or secure WebSocket URL.
                        required: false
                    websocket_url:
                        type: WebsocketUrl
                        description: A valid WebSocket or secure WebSocket URL.
                        required: false
                    file_url:
                        type: FileUrl
                        description: A valid file URL.
                        required: false
                    ftp_url:
                        type: FtpUrl
                        description: A valid FTP or FTPS URL.
                        required: false
                    postgres_dsn:
                        type: PostgresDsn
                        description: A valid PostgreSQL DSN.
                        required: false
                    cockroach_dsn:
                        type: CockroachDsn
                        description: A valid CockroachDB DSN.
                        required: false
                    amqp_dsn:
                        type: AmqpDsn
                        description: A valid AMQP DSN.
                        required: false
                    redis_dsn:
                        type: RedisDsn
                        description: A valid Redis DSN.
                        required: false
                    mongo_dsn:
                        type: MongoDsn
                        description: A valid MongoDB DSN.
                        required: false
                    kafka_dsn:
                        type: KafkaDsn
                        description: A valid Kafka DSN.
                        required: false
                    nats_dsn:
                        type: NatsDsn
                        description: A valid NATS DSN.
                        required: false
                    mysql_dsn:
                        type: MySQLDsn
                        description: A valid MySQL DSN.
                        required: false
                    mariadb_dsn:
                        type: MariaDBDsn
                        description: A valid MariaDB DSN.
                        required: false
                    clickhouse_dsn:
                        type: ClickHouseDsn
                        description: A valid ClickHouse DSN.
                        required: false
                    snowflake_dsn:
                        type: SnowflakeDsn
                        description: A valid Snowflake DSN.
                        required: false
                    email_str:
                        type: EmailStr
                        description: A valid email address.
                        required: false
                    name_email:
                        type: NameEmail
                        description: A valid name and email address.
                        required: false
                    ipvany_address:
                        type: IPvAnyAddress
                        description: A valid IPv4 or IPv6 address.
                        required: false
"""

MARKDOWN_YASL = """
definitions:
    acme:
        types:
            thing:
                description: Information about a thing.
                properties:
                    id:
                        type: str
                        description: The unique identifier for the thing.
                        required: true
                    markdown:
                        type: markdown
                        description: A markdown value
                        required: true
"""

TASK_BAD_NAMESPACE_REF_YASL = """
definitions:
    main:
        types:
            task:
                description: A thing to do.
                namespace: main
                properties:
                    description:
                        type: str
                        description: A description of the task.
                        required: true
                    owner:
                        type: str
                        description: The person responsible for the task.
                        required: false
                    complete:
                        type: bool
                        description: Is the task finished? True if yes, false if no.
                        required: true
                        default: false
    other:
        types:
            list_of_tasks:
                description: A list of tasks to complete.
                namespace: other
                properties:
                    task_list:
                        type: map[int, notmain.task]
                        description: A list of tasks to do.
                        required: true
"""