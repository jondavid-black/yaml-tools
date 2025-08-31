# YASL YAML Advanced Schema Language

YASL is an advanced schema language & validation tools for YAML. 
It supports definition and validation of data structures with primitives, enumerations, and composition of defined types.

## Motivation

Add some thoughts on why this may be valuable.

## Usage

To use YASL you must first define your data schema in a YASL file as described in the Defining YASL Schemas section below.
Once you have a schema and a corresponding data file, you run the YASL command line tool.

```bash
yasl data_file.yaml schema_file.yasl
```

YASL provides various options.
Here's the full usage info provided by the command line tool.

```bash
user@system:~/tools/yasl$ ./yasl -h
YASL - YAML Advanced Schema Language CLI
Usage:
  yasl <file.yaml> <file.yasl>
  yasl -yaml <file.yaml> -yasl <file.yasl>
Options:
  -yaml <file.yaml>     Path to the YAML file
  -yasl <file.yasl>     Path to the YASL file
  -V, --version         Print version and exit
  -h, --help            Show help and exit
  -q, --quiet           Run in quiet mode (errors only)
  -v, --verbose         Run in verbose mode (debug/trace)
  --output-type         Log output type: text, json, yaml
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

A string field definition within a defined type may look like...
```yaml
type_def:
  name: person
  description: A person data item.
  fields:
    - name: name
      type: str
      description: A person's full name.  Must include a first name, optional middle name(s), and a last name.
      str_min: 2
      str_max: 50
      str_regex: ^[A-Z][a-zA-Z]*\s(?:[A-Z][a-zA-Z]*\s)*[A-Z][a-zA-Z]*$
  
```

#### Integer

An integer is a whole number value.
YASL uses the same integer handling as YAML.
The integer primitive is represented by the type name `int` when defining fields in schemas.

Integer validators include:

- `min`: int - Minimum allowed value.  Default: none.
- `max`: int - Maximum allowed value.  Default: none.
- `exclude`: int[] - List of unallowed values.  Default: none.

An integer field definition within a defined type may look like...
```yaml
type_def:
  name: person
  description: A person data item.
  fields:
    - name: name
      type: str
      description: A person's full name
    - name: age
      type: int
      description: A person's age in years.
      min: 0
      max: 150
```

#### Number

A number is a real (i.e. floating point) number value.
YASL uses the same number handling as YAML.
The number primitive is represented by the type name `num` when defining fields in schemas.

Number validators include:

- `min`: num - Minimum allowed value.  Default: none.
- `max`: num - Maximum allowed value.  Default: none.
- `exclude`: num[] - List of unallowed values.  Default: none.

A number field definition within a defined type may look like...
```yaml
type_def:
  name: person
  description: A person data item.
  fields:
    - name: name
      type: str
      description: A person's full name
    - name: height
      type: int
      description: A person's height in meters.
      min: 0.0
      max: 2.9  # ~0.2m taller than the tallest person ever recorded
```

#### Boolean

A boolean is a true / false value.
YASL uses the same boolean handling as YAML.
The boolean primitive is represented by the type name `bool` when defining fields in schemas.

There are no YASL validators for boolean values.

A number field definition within a defined type may look like...
```yaml
type_def:
  name: person
  description: A person data item.
  fields:
    - name: name
      type: str
      description: A person's full name
    - name: citizen
      type: bool
      description: True if the person is a citizen, false otherwise.
```

#### Date

A date is a date timestamp value.
YASL uses ISO 8601 formatting for date types.
The date primitive is represented by the type name `date` when defining fields in schemas.

Date validators include:

- `date_format`: bool - The date format to use for date fields per ISO 8601. Default: YYYY-MM-DD HH:MM:SS:ssss.
- `before`: date - Require value to be before a specific date-time.  Default: none.
- `after`: date - Require value to be after a specific date-time.  Default: none.

A date field definition within a defined type may look like...
```yaml
type_def:
  name: person
  description: A person data item.
  fields:
    - name: name
      type: str
      description: A person's full name
    - name: birthdate
      type: date
      description: The date a person was born.
      date_format: YYYY-MM-DD
      after: 1907-03-03  # current oldest person is 117 yrs old, so 1 day before her birthday
```

#### Path

A path is a file system location value.
YASL uses Linux path formatting (i.e. directory/directory/file.ext) for path types.
The path primitive is represented by the type name `path` when defining fields in schemas.

Path validators include:

- `path_regex`: str[] - List of regular expression validation rules.  Default: none.
- `exists`: bool - Require value to be present on the file system.  Default: false.
- `is_dir`: bool - Requires value to be a directory and exist on the file system.  Default: false.
- `is_file`: bool - Requires value to be a file and exist on the file system. Default: false.

A path field definition within a defined type may look like...
```yaml
type_def:
  name: person
  description: A person data item.
  fields:
    - name: name
      type: str
      description: A person's full name
    - name: birth_certificate
      type: path
      description: A scan of the person's birth certificate.
      exists: true
      is_file: true
```

#### URL

A URL is a universal record locator value as commonly used for internet addresses.
YASL accepts a URL as any string that can be resolved as a network location, including protocol, port, address, etc.
The url primitive is represented by the type name `url` when defining fields in schemas.

URL validators include:

- `url_protocol`: str[] - List of allowable network protocols (i.e. http, https). Default: none.
- `url_reachable`: bool - Require the value to be reachable on the current network (i.e. Status=200 for HTTP). Default: false.

A URL field definition within a defined type may look like...
```yaml
type_def:
  name: person
  description: A person data item.
  fields:
    - name: name
      type: str
      description: A person's full name
    - name: bio
      type: url
      description: URL to a person's online bio.
      url_reachable: true
```

#### TYPE

A type is the name of a primitive, enumeration, or defined type.
YASL requires the type name to match a known defined type.
The type primitive is represented by the type name `type` when defining fields in schemas.

There are no YASL validators for type values.

#### Reference

A reference is used to refere to a data element within the YAML being evaluated by YASL.
The ref primitive is represented by the type name `ref(target)` where target orients the reference when defining fields in schemas.
Reference types are parameterized with the `target` of the reference location.
The format of the target emulates file system paths and allows for absolute and by-reference definition with the defined type structure of the schema.
Defining and using references can get complex, so a detailed description of references with examples is provided below.

Reference validators include:

- `ref_exists`: bool - True if reference target must exist in the data, false othersise. Default: true.
- `ref_multi`: bool - True if a reference target may return multiple values (i.e. act as a list), false otherwise. Default: false.
- `ref_filters`: ref_filter[] - List of filters defined by reference and value to constrain the ref lookup in the data set. Default: none.

#### Any

An any is a catch all that allow the value to be of any type.
The any primitive is represented by the type name `any` when defining fields in schemas.

Any validators include:

- `any_of`: type[] - List of allowed types for the any field.

An any field definition within a defined type may look like...
```yaml
type_def:
  name: person
  description: A person data item.
  fields:
    - name: name
      type: str
      description: A person's full name
    - name: favorite_pet
      type: any
      description: The person's favorite pet.
      any_of:  # The types of pets known to the schema
        - cat
        - dog
        - fish
        - bird
        - reptile
        - rabbit
```

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

_TODO:  Consider expanding on the `values` to allow for additional value definition such as descriptions or other metadata._

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

- name: str - The unique name of the type definition within the package context.
- package (optional): str - Establishes a named context for the type within which it must be unique.
- description (optional): str - A description of the type definition.
- root (optional): bool - True if the type can be a yaml document root, false otherwise (default false).
- type (optional): str - Used to indicate the type_def is a value or list rather than a structure.  Must be present if no properties are defined.
- properties (optional): property[] - List of data properties for the type.  Must be present if no type is defined.
- validators (optional): validator - Special validators to establish field definition constraints.

YASL type definitions are established layer-by-layer, with complex types being defined as compositions of other type definitions.
When defining fields, you may include the primitive validation tags provided above.
Validators are used to constrain how fields may be used in actual data sets.

Let's consider what a type definition may look like if it were defined by a YASL type definition.
It would begin with a `type_def` root tag and provide the attributes described above.

```yaml
type_def:
  name: type_def
  package: yasl.lang
  description: The definition for a YASL data structure.
  properties:
    - name: name
      type: string
      description: The name of the type definition.
      required: true
      unique: true
    - name: description
      type: string
      description: A description of the type definition.
      required: false
    - name: root
      type: bool
      description: True if the type can be a root element in a yaml document.
    - name: properties
      type: property[]
      description: The properties that make up the type definition.
      required: true
    - name: validators
      type: validators
      description: The validators that apply to the type definition.
      required: false
```

### Properties

Type definition properties allow you to establish the composition structure of YAML data within your YASL schema.
Not only do these serve to support data validation, they also provide a method of data documentation.

Properties have the following attributes:

- name: str - The name of the field which must be unique within the type definition.
- package (optional): str - The package containing the type definition if not using primitive types.  Default: same package as the type_def.
- type: type - The name of the primitive, enumeration, or type definition of the field.
- description (optional): str - A brief summary of the field.
- required (optional): bool - True if the field must be present in the data set, false otherwise.  Default: true.
- unique (optional): bool - True if the field must be unique across all type_def uses in the data set.  Default: false.
- default (optional): any - The default value of the field if not provided.  The value type must match the type field.

Let's look at what a field type definition would look like as defined in a YASL schema.

```yaml
type_def:
  name: property
  package: yasl.lang
  description: A property in a YASL type definition.
  properties:
    - name: name
      type: str
      description: The name of the property.
      required: true
    - name: package
      type: str
      description: The package in which the property type is defined.
      required: false
    - name: type
      type: type
      description: The name of the primitive, enum, or type_def that this property is typed as.
      required: true
    - name: description
      type: str
      description: A description of the property.
      required: false
    - name: required
      type: bool
      description: Whether the property is required.
      required: false
      default: true
    - name: unique
      type: bool
      description: Whether the property must be unique across instances of the type definition.
      required: false
      default: false
    - name: default
      type: any
      description: The default value for the property if not provided.
      required: false

    # list property constraints
    - name: list_min
      type: int
      description: The minimum number of items in a list property.
      required: false
      default: 0
    - name: list_max
      type: int
      description: The maximum number of items in a list property.
      required: false

    # int and num property constraints
    - name: min
      type: any
      of:
        - int
        - num
      description: The minimum value for int or num property.
      required: false
    - name: max
      type: any
      of:
        - int
        - num
      description: The maximum value for int or num property.
      required: false
    - name: exclude
      type: any[]
      of:
        - int
        - num
      description: A list of values that are excluded from valid values for the property.
      required: false

    # str property constraints
    - name: str_min
      type: int
      description: The minimum length of the str.
      required: false
    - name: str_len
      type: int
      description: The maximum length of the str.
      required: false
    - name: str_regex
      type: str[]
      description: A list of regular expressions a str field value must match.
      required: false

    # date property constraints
    - name: date_format
      type: str
      description: The date format to use for date property per ISO 8601.
      required: false
      default: YYYY-MM-DD HH:MM:SS:ssss
    - name: before
      type: date
      description: A date before which the property value must be.
      required: false
    - name: after
      type: date
      description: A date after which the property value must be.
      required: false

    # path property constraints
    - name: path_regex
      type: str[]
      description: A list of regular expressions a path property value must match.
      required: false
    - name: path_exists
      type: bool
      description: Whether the path property value must exist on the file system.
      required: false
    - name: is_dir
      type: bool
      description: Whether the path property value must be a directory.
      required: false
    - name: is_file
      type: bool
      description: Whether the path property value must be a file.
      required: false

    # url property constraints
    - name: url_protocol
      type: str[]
      description: A list of allowed protocols for the URL property (i.e. http, https).
      required: false
    - name: url_reachable
      type: bool
      description: Whether the URL property value must be reachable on the current network.
      required: false

    # any property constraints
    - name: any_of
      type: type[]
      description: A list of types that the any property value must match.
      required: false

    # ref property constraints
    - name: ref_exists
      type: bool
      description: Whether the reference property value must exist in the data.
      required: false
      default: true
    - name: ref_multi
      type: bool
      description: Whether the reference property may return multiple values (accounting for optional filters).
      required: false
      default: false
    - name: ref_filters
      type: ref_filter[]
      description: A list of filters to apply when resolving the reference property value.
      required: false
```

### Type Validators

YASL recognizes there can be complexities and conditionals to consider when defining data types.
Type validators allow you to establish constraints on your type definitions.
The available validators provide for the basic definition of common data constraints in your schema.

YASL provides the following type validators:

- `only_one`: str[] - List of mutually exclusive field names where only one may be present.
- `at_least_one`: str[] - List of field names where one or more must be present.
- `if_then`:
  - `if`: ref(../../fields/name) - Name of a field in the `type_def`. Default: none.
  - `not` (Optional): bool - invert the value equivalence (i.e. if not true).  Default: false.
  - `value`: any | `nil` - Value to compare to `if` for equivalence (i.e. `true` for a bool, `42` for int, `nil` for absence of data, etc.). Default: none.
  - `present`: ref(../../fields/name)[] - list of field names in the `type_def` that must be present if the check is `true`. Default: none.
  - `absent`: ref(../../fields/name)[] - list of field names in the `type_def` that must be absent of the check is `true`.  Default: none.

Let's look at what a type validators definition would look like as defined in a YASL schema.

```yaml
type_def:
  name: validators
  package: yasl.lang
  description: The validators that can be applied to a type definition.
  properties:
    - name: only_one
      type: ref(../fields/name)
      description: A list of field names that must not be present together.
      required: false
    - name: at_least_one
      type: ref(../fields/name)
      description: A list of field names where one or more must be present.
      required: false
    - name: if_then
      type: if_then
      description: A list of conditions that must be met for the type definition.
      required: false

type_def:
  name: if_then
  package: yasl.lang
  description: A condition that must be met for the type definition.
  properties:
    - name: if
      type: string
      description: The name of the field to evaluate.
      required: true
    - name: value
      type: any[]
      description: The values to compare to `if` field value for equivalence (or handled as `in` when more than 1 value is present)
      required: true
      list_min: 1
    - name: present
      type: ref(../../fields/name)[]
      description: A list of field names in the type definition that must be present if the condition is met.
      required: false
    - name: absent
      type: ref(../../fields/name)[]
      description: A list of field names in the type definition that must be absent if the condition is met.
      required: false
  validators:
    at_least_one:
      - present
      - absent
```

### Using YASL Reference Types

YASL allows you to use reference types within your type definition fields to ensure data referential integrity.

Since references can be a bit complex, let's start with a simple example.
Let's say we are tracking inventory in our used car dealership.
We need to ensure we know the make, model, and year of each car on the lot.
If we have data errors, the sales forms generated by our system become invalid which can cost us a lot of money to correct later.
To address this we'll create a simple data schema as follows:

```yaml
type_def:
  name: manufacturer
  description: The name of the automobile manufacturer.
  properties:
    - name: name
      type: str
      description: The name of the automobile manufacturer.
      unique: true
    - name: svc_rep
      type: str
      description: The name of our manufacturer service rep.
    - name: phone
      type: str
      description: The phone number of our service rep.

type_def:
  name: car
  description: A car for sale in our inventory.
  properties:
    - name: make
      type: ref(manufacturer/name)
      description: The automobile manufacturer.
    - name: model
      type: str
      description: The model name of the vehicle.
    - name: year
      type: int
      description: The year the vehicle was manufactured.
    - name: vin
      type: str
      description: The unique identifier on the vehicle.
      unique: true
```

With this schema established, we can define our inventory data as such and validate it using YASL.

```yaml
manufacturer:
  name: Ford
  svc_rep: John Geeen
  phone: 111-222-3333

manufacturer:
  name: Chevy
  svc_rep: Jane White
  phone: 222-333-4444

car:
  make: Ford  # Valid because we can trace the reference to a known manufacturer name.
  model: Thunderbird
  year: 2005
  vin: 2323883553423235323456-21352

car:
  make: Frod  # Invalid because there is no know manufacturer named Frod in our data set.
  model: F-150
  year: 2015
  vin: 2343262234566375221997-89615
```

### Absolute Reference Using Types, Not Overall Structure

YASL type definitions don't inherently restrict what type definition may or may not be used as root types.
But the field definitions can potentially infer structure based on whether you use explicit types or reference types.
This is a data design choice you must make for yourself, but YASL attempt to be as flexible as possible.
YASL will attempt to treat each data element defined by a `type_def` as an independent item whether it is a root definition or deeply burried within a data structure.
Let's take the above example but assume we have a large data model of global automotive manufacturers.
This data model organizes around macro economics starting with top level items such as global region, holding company, etc before getting down into specific manufacturing brands.
And our data model embeds all this data in a single monolithic structure rather than a decomposed structure using references.
At our little franchise lot, we just need the basic manufacturer data without all the global economics information.
The good news is YASL will handle that manufacturer data in exactly the same way whether it is defined as a root item or burried deep in a complex data structure.
The reference we use for `make` in our `car` schema does not need to change.
YASL will recognize the data definition and handle it as a `manufacturer` type no matter where it resides in the data set's structure.

### Relative Reference

Sometimes you may have a need to recognize specific structural relationships in your references.
Relative reference targets allow you to do this.
The reference fields showin in the `validators` YASL definitions above are a good example of this.
In this instance, our references are to specific data sets relative to the provided value and structure.
Specifically, we only care about field references for the type whichin which the validators are defined rather than all type definitions.
Using relative references allows you to remain "data relative" when defining and evaluating references in your type definitions.

### Reference Filters

Filters add a bit more flexibility and complexity to reference types.
To explain this, go back to our car lot example above.
We'll update the manufacturer type definition to account for the fact that service reps are regional rather than global.

```yaml
type_def:
  name: manufacturer
  description: The name of the automobile manufacturer.
  properties:
    - name: name
      type: str
      description: The name of the automobile manufacturer.
      unique: true
    - name: region
      type: str
      description: The manufacturer's support region.
    - name: svc_rep
      type: str
      description: The name of our manufacturer service rep.
    - name: phone
      type: str
      description: The phone number of our service rep.
```

Perhaps we need to reference a service representative but only for a specific manufacturer and region.
We can create a type def to do that.

```yaml
type_def:
  name: support_claim
  description:  An automotive support claim.
  properties:
    - name: id
      type: int
      description: The unique identifier of the support claim.
      unique: true
    - name: rep
      type: ref(manufacturer/svc_rep)
      description:  The name of the service representative.
      ref_filters:
        - target: manufacturer/region
          value: Midwest US
```

By filtering the reference, we can ensure that the value provided in the `rep` field actually matches the specific rep for our region.

### Importing Other YASL Files

YASL allows you to organize schema data as you see fit.  As a YAML file, you can