# YASL - YAML Advanced Schema Language

YASL is an advanced schema language & validation tools for YAML. 
It supports definition and validation of data structures with primitives, enumerations, and composition of defined types.

## Motivation

Add some thoughts on why this may be valuable.

## Usage

To use YASL you must first define your data schema in a YASL file as described in the Defining YASL Schemas section below.
Once you have a schema and a corresponding data file, you run the YASL command line tool.

```bash
yasl <schema> <data> <model_name>
```

YASL provides various options.
Here's the full usage info provided by the command line tool.

```bash
user@system:~/repos/myproject$ yasl -h
usage: yasl [-h] [--version] [--quiet] [--verbose] [--output {text,json,yaml}] [schema] [yaml] [model_name]

YASL - YAML Advanced Schema Language CLI Tool

positional arguments:
  schema                YASL schema file
  yaml                  YAML data file
  model_name            YASL schema name for the yaml data file (optional)

options:
  -h, --help            show this help message and exit
  --version             Show version information and exit
  --quiet               Suppress output except for errors
  --verbose             Enable verbose output
  --output {text,json,yaml}
                        Set output format (text, json, yaml). Default is text.
```

Note that all options must be provided before the file arguments.

## Defining YASL Schemas

At the heart of YASL is the schema definition.
The intent is to make schema definition as simple and familiar as possible by using the same YAML format that you are using for your data.
There are a few key concepts to consider when defining your YASL schema: primitives, enumerations, and data types.
Once you've mastered these, you'll want to consider things like data validation, referential integrity, and version control.

### Comments

YASL is just YAML, so comments work the same way.
Start your comment with a `#` and everything after that is comment text.
You can do full or partial line comments.

### YASL Primitives

YASL supports the "normal" primitive types as well as a few "extended" types commonly used in modern data sets.
These should be immediately familiar.
YASL takes one further step by defining optional validators for each primitive type which can be provided as part of the field definition.
The following sections define each of the YASL primitives and the associated validators.

#### String

A string is text, generally alphanumeric and special characters.
YASL uses the same string handling as YAML.
The string primitive is represented by the type name `str` when defining fields in schemas.

String validators include:

- `str_min`: int - The minimum length of the string. Default: none.
- `str_max`: int - The maximum length of the string. Default: none.
- `str_regex`: str[] - List of regular expression validation rules. Default: none.

#### Integer

An integer is a whole number value.
YASL uses the same integer handling as YAML.
The integer primitive is represented by the type name `int` when defining fields in schemas.

Integer validators include:

- `gt`: int - Value must be greater than the parameter.
- `ge`: int - Value must be greater than or equal to the parameter.
- `lt`: int - Value must be less than the parameter.
- `le`: int - Value must be less than or equal to the parameter.
- `exclude`: int[] - List of unallowed values.  Default: none.
- `multiple_of`: int - Value must be a multiple of the parameter.

#### Float

A number is a floating point number value.
YASL uses the same number handling as YAML.
The number primitive is represented by the type name `float` when defining fields in schemas.

Float validators include:

- `gt`: int - Value must be greater than the parameter.
- `ge`: int - Value must be greater than or equal to the parameter.
- `lt`: int - Value must be less than the parameter.
- `le`: int - Value must be less than or equal to the parameter.
- `exclude`: int[] - List of unallowed values.  Default: none.
- `multiple_of`: int - Value must be a multiple of the parameter.
- `whole_number`: bool - Force the float to be a whole number (i.e. no decimal places).

#### Boolean

A boolean is a true / false value.
YASL uses the same boolean handling as YAML.
The boolean primitive is represented by the type name `bool` when defining fields in schemas.

There are no YASL validators for boolean values.

#### Date

A date is a date formatted value.
YASL uses ISO 8601 formatting for date types.
The date primitive is represented by the type name `date` when defining fields in schemas.

Date validators include:

- `before`: date - Require value to be before a specific date.  Default: none.
- `after`: date - Require value to be after a specific date.  Default: none.

#### Time

A time is a time formatted value.
YASL uses ISO 8601 formatting for date types.
The time primitive is represented by the type name `time` when defining fields in schemas.

Time validators include:

- `before`: time - Require value to be before a specific time.  Default: none.
- `after`: time - Require value to be after a specific time.  Default: none.

#### Datetime

A datetime is a datetime formatted value.
YASL uses ISO 8601 formatting for date types.
The datetime primitive is represented by the type name `datetime` when defining fields in schemas.

Datetime validators include:

- `before`: datetime - Require value to be before a specific datetime.  Default: none.
- `after`: datetime - Require value to be after a specific datetime.  Default: none.

#### Path

A path is a file system location value.
YASL uses Linux path formatting (i.e. directory/directory/file.ext) for path types.
The path primitive is represented by the type name `path` when defining fields in schemas.

Path validators include:

- `path_exists`: bool - Require value to be present on the file system.  Default: false.
- `is_dir`: bool - Requires value to be a directory and exist on the file system.  Default: false.
- `is_file`: bool - Requires value to be a file and exist on the file system. Default: false.
- `file_ext`: str[] - A list of permitted file extensions.

#### URL

A URL is a universal record locator value as commonly used for internet addresses.
YASL accepts a URL as any string that can be resolved as a network location, including protocol, port, address, etc.
The url primitive is represented by the type name `url` when defining fields in schemas.

URL validators include:

- `url_base`: str - The required base value for the URL (i.e. www.mycompany.com).  Default: none.
- `url_protocols`: str[] - List of allowable network protocols (i.e. http, https). Default: none.
- `url_reachable`: bool - Require the value to be reachable on the current network (i.e. Status=200 for HTTP). Default: false.

#### Reference

A reference is used to refere to a data element within the YAML being evaluated by YASL.
The ref primitive is represented by the type name `ref(target)` where target specified the custom type and field being referenced.
These target fields must be unique as designated by the `unique` attribute in the target field to avoid value collisions.
YASL expects the value to exist in the YAML being evaluated, but this can be overridden by setting `no_ref_check = true` in the property definition for the reference.

#### Any

An any is a catch all that allow the value to be of any type.
The any primitive is represented by the type name `any` when defining fields in schemas.

Any validators include:

- `any_of`: str[] - List of allowed type names for the any field.

#### Pydantic Types

YASL supports all [Pydantic types](https://docs.pydantic.dev/latest/api/types/) [and Pydantic Network types](https://docs.pydantic.dev/latest/api/networks/).

### YASL Enumeration Definitions

YASL enumerations are a simple way to establish prefined values as a usable type for use in schemas.

An enumeration definition may look like...
```yaml
enum:
  name: color
  values:
    - RED
    - BLUE
    - GREEN

enum:
  name: size
  values:
    - SMALL
    - MEDIUM
    - LARGE
```

Once defined, enumerations can be used as types within type definitions.
Here's an example of using the above enumerations as fields within a type definition.

```yaml
type_def:
  name: baloon
  description: A baloon product.
  fields:
    - name: brand
      type: str
      description: The brand name of the baloon.
    - name: size
      type: size
      description: The size of the baloon.
    - name: color
      type: color
      description: The color of the baloon.
```

### YASL Type Definitions

YASL intends to provide a simple but powerful means of defining complex data types for YAML data set validation.

These type definitions have the following attributes:

- `name`: str - The unique name of the type definition within the package context.
- `namespace` (optional): str - Establishes a named context for the type within which it must be unique.
- `description` (optional): str - A description of the type definition.
- `properties`: property[] - List of data fields for the type.
- `validators` (optional): validator - Special validators to establish field definition constraints.

### Type Properties

Type definition properties allow you to establish the composition structure of YAML data within your YASL schema.
Not only do these serve to support data validation, they also provide a method of data documentation.

Properties have the following attributes:

- `name`: str - The name of the field which must be unique within the type definition.
- `namespace` (optional): str - The namespace containing the type definition if not using primitive types.  Default: same package as the type_def.
- `type`: type - The name of the primitive, enumeration, or type definition of the field.
- `description` (optional): str - A brief summary of the field.
- `required` (optional): bool - True if the field must be present in the data set, false otherwise.  Default: true.
- `unique` (optional): bool - True if the field must be unique across all type_def uses in the data set.  Default: false.
- `default` (optional): any - The default value of the field if not provided.  The value type must match the type field.

In addition to these fields, the primitive validators from above may be included as desired based on the type.

### Type Validators

YASL recognizes there can be complexities and conditionals to consider when defining data types.
Type validators allow you to establish constraints on your type definitions.
The available validators provide for the basic definition of common data constraints in your schema.

YASL provides the following type validators:

- `only_one`: str[] - List of mutually exclusive property names where only one may be present.
- `at_least_one`: str[] - List of property names where one or more must be present.
- `if_then`: IfThen[] - List of conditional checks.
  - `eval`: str - Name of a property in the `type_def`.
  - `value`: str[] - List of values to compare to `eval` for equivalence (i.e. `true` for a bool, `42` for int, etc.).
  - `present`: str[] (optional) - list of property names in the `type_def` that must be present if the check is `true`.
  - `absent`: str[] (optional) - list of property names in the `type_def` that must be absent of the check is `true`.  Default: none.
