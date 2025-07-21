# YASL Design

YASL provides YAML content and structure validation based on a defined schema.
The schema is a YAML file that allows users to define strongly typed data structures, enumerations, and data references.

## YASL Types & Structures

YASL allows for the definition of data type structures.
A type definition (denoted as `type_def`) consists of a name, description, a list of fields, and a list of structure validators.
Each `type_def` must be uniquely named within the scope of the schema definition.
The `type_def` name field should correspond to the key that would be present in the yaml if the type were present as a standalone data entry.
Data types can be used in the same way you use primitives in structure definition.
YASL focuses on composition and does not currently support inheritance.
YASL types are essentially named data sets consisting of a collection of data fields.
Each data field is typed and may be defined with metadata to support content validation.
By default, each field is required unless overriden with the `required: false` metadata.
Other validation metadata is tailored to the primitive type of the field.
Primitive validation options are provided below in the primitive definitions.

Each field defined within a type has the following attributes:

- name: str - The name of the field as it would appear in the yaml file.  Default: none.
- package (optional): str - The context of the data type.  Default: none.
- description (optional): str - The description of the field. Default: none.
- type: type - The type of the field (primitive, enum name, or type name).  Default: none.
- required: bool - True if the field must be present, otherwise false.  Default: true.
- unique: bool - True if the value must not repeat across all type usage within the package, otherwise false.  Default: false.
- default (optional): any - The default value for the field.  It must be of the type defined in the `type` field. Default: none.

YASL allows you to define lists (aka arrays) by adding `[]` after the type name in a field definition.
Each list entry in the content will be validated based on the type specific attributes.
Lists may be further specified by the following list-specific attributes:

- list_min: int - The minimum length of the list.  Default: 0
- list_max: int - The maximum length of the list.  Default: none.

``` yaml
type_def:
  name: employee
  description: Information about a individual human.
  fields:
    - name: id
      type: str
      description: The employee ID within the HR system.
      str_min: 5
      str_max: 16
    - name: first_name
      type: str
      description: The first name of the person.
    - name: last_name
      type: str
      description:  The last name of the person.
    - name: middle_name
      type: str
      description:  The middle name or middile initial of the person.
      required: false
    - name: email
      type: str
      description: The person's email address.
      required: false
      regex:
        - ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$

type_def:
  name: team
  description: A collection of employees who work together regularly.
  fields:
    - name: name
      type: str
      description: The name of the team.
      str_min: 5
      str_max: 32
    - name: leader
      type: ref(employee.id)
      description: The designated individual to lead the team.
    - name: members
      type: ref(employee.id)[]
      description: A list of employees (by employee id) who are on the team.  Smallest possible team size is 3 (1 lead and 2 members).
      list_min: 2
  validators:
    - unique_values:
      - leader
      - members
```

## YASL Primitives

YASL provides common primitive data types for use in defining YAML content schemas.
Each primitive may be augmented with metadata when used to define fields within data structures.
YASL uses signed 64-bit data types for numerical data to allow for very small / large data values (i.e. Golang int64 range is -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807).
YASL provides the following primitive data types and their validation constraints:

- `str`: String - Represents textual data.
  - `min`: int - The minimum length of the string. Default: none.
  - `max`: int - The maximum length of the string. Default: none.
  - `regex`: str[] - List of regular expression validation rules. Default: none.
- `int`: Integer - Represents whole number values.
  - `min`: int - Minimum allowed value.  Default: none.
  - `max`: int - Maximum allowed value.  Default: none.
  - `exclude`: int[] - List of unallowed values.  Default: none.
- `num`:  Number - Represents floating point number values.
  - `min`: num - Minimum allowed value.  Default: none.
  - `max`: num - Maximum allowed value.  Default: none.
  - `exclude`: num[] - List of unallowed values.  Default: none.
- `bool`: Boolean - Represents binary data, either true or false.
- `date`: Date / Timestamp - Represents specific points in time.
  - `no_time`: bool - Allow data but no time value. Default: false.
  - `no_date`: bool - Allow time but no date value. Default: false.
  - `before`: date - Require value to be before a specific date-time.  Default: none.
  - `before_ref`: ref(date) - Require a value to be before a specific referenced date-time.  Default: none.
  - `after`: date - Require value to be after a specific date-time.  Default: none.
  - `after_ref`: ref(date) - Require a value to be after a specific referenced date-time.  Default: none.
- `path`: File System Path - Represents directory and file paths.
  - `regex`: str[] - List of regular expression validation rules.  Default: none.
  - `exists`: bool - Require value to be present on the file system.  Default: false.
  - `is_dir`: bool - Requires value to be a directory and exist on the file system.  Default: false.
  - `is_file`: bool - Requires value to be a file and exist on the file system. Default: false.
- `ref(target)`: Data Reference - Represents a reference to a data item as specified by a target string (i.e. type_def.name).
  - `multi`: bool - Indicates there may be more than 1 value result from searching for the target.  Default: false.
- `type`: Type Reference - Represents a named type (structure or enum).
- `any`: Allows any value, generally used if a type is to be inferred based on other data.

## YASL Enumerated Values

YASL allows for the definition of enumerated value types.
Enumerated values can be used in the same way you use primitives in structure definition.
During validation, YASL will ensure the content value is consistent with the enumerated type values.

``` yaml
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

type_def:
  name: baloon
  description: A baloon product.
  fields:
    - name: name
      type: str
      description: The brand name of the baloon.
    - name: size
      type: size
      description: The size of the baloon.
    - name: color
      type: color
      description: The color of the baloon.
```

## YASL Structure Validators

YASL allow for more complex evaluation of content using validators.
A validator is applied to the `type_def` and allows for cross-field content validation.
Below is a list of cross-field validators provided by YASL.

- `only_one`: str[] - List of mutually exclusive field names where only one may be present.
- `if_then`:
  - `if`: ref(type_def.fields.name) - Name of a field in the `type_def`. Default: none.
  - `not` (Optional): bool - invert the value equivalence (i.e. if not true).  Default: false.
  - `value`: any | `nil` - Value to compare to `if` for equivalence (i.e. `true` for a bool, `42` for int, `nil` for absence of data, etc.). Default: none.
  - `present`: ref(type_def.fields.name)[] - list of field names in the `type_def` that must be present if the check is `true`. Default: none.
  - `absent`: ref(type_def.fields.name)[] - list of field names in the `type_def` that must be absent of the check is `true`.  Default: none.

```yaml
type_def:
  name: basic_shape
  description: A basic geometric shape (circle, triangle, square, etc.)
  fields:
    - name: name
      type: str
      description: The name of the shape.
    - name: num_edges
      type: int
      description: The number of edges on the shape
      min: 1  # There are no shapes with 0 edges.
      exclude: 2  # 1 edge is a circle.  No shape with 2 edges.  3 or more edges is a polygon.
    - name: radius_len
      type: num
      description: The length of the radius (only for circles, i.e. shape with 1 edge)
      min: 0
    - name: edge_len
      type: num
      description: The length of the edge of the shape (only for polygons, i.e. shape with 2 or more edges)
      min: 0
  validators:
    - only_one:
      - radius_len
      - edge_len
    - if_then:
        if: num_edges
        value: 1
        present:
          - radius_len
        absent:
          - edge_len
    - if_then:
        if: num_edges
        not: true
        value: 1
        present:
          - edge_len
        absent:
          - radius_len
```

## Importing Data

For large or complex data sets, you will likely want to organize content in a more manageable way than a single file.
YASL provides an import capability that allows you to distribute content across the file system.

Imagine you're tracking data about your company's projects.
You need a way to define data structures that also leverage information about employees and teams.

`org.yasl`
``` yaml
type_def:
  name: employee
  description: Information about a individual human.
  fields:
    - name: id
      type: str
      description: The employee ID within the HR system.
      str_min: 5
      str_max: 16
    - name: first_name
      type: str
      description: The first name of the person.
    - name: last_name
      type: str
      description:  The last name of the person.
    - name: middle_name
      type: str
      description:  The middle name or middile initial of the person.
      required: false
    - name: email
      type: str
      description: The person's email address.
      required: false
      regex:
        - ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$

type_def:
  name: team
  description: A collection of employees who work together regularly.
  fields:
    - name: name
      type: str
      description: The name of the team.
      str_min: 5
      str_max: 32
    - name: leader
      type: ref(employee.id)
      description: The designated individual to lead the team.
    - name: members
      type: ref(employee.id)[]
      description: A list of employees (by employee id) who are on the team.  Smallest possible team size is 3 (1 lead and 2 members).
      list_min: 2
  validators:
    - unique_values:
      - leader
      - members
```

Given the `org.yasl` definitions of employees and teams, we need to define our project data structures to reuse these data definitions.  We don't want to repeat the definitions and cause a maintenance nightmare for ourselves.  Instead we will import `org.yasl` so that we have access to the defined data types.

`project.yasl`
```yaml
import:
  - ./org.yasl

enum:
  name: project_status
  values:
    - PROPOSED
    - DEFERRED
    - ACTIVE
    - PAUSED
    - COMPLETED

type_def:
  name: project
  description: A set of work intended to provide customer or business value.
  fields:
    - name: name
      type: str
      description: The name of the project.
      unique: true
      required: true
    - name: sow
      type: str
      description: The statement of work for the project.
      required: true
    - name: pm
      type: employee  # Using org.yasl definition of employee
      description: The individual serving as the project manager.
      required: true
    - name: teams
      type: team[] # using org.yasl definition of team
      description: The teams assigned to work the project.
      list_min: 1
      required: true
```

## Comments

YASL is just YAML, so comments work the same way.
Just start your comment with a `#` and everything after that is comment text.
You can do full or partial line comments.
