# Quickstart: YASL Presence Attribute

**Feature**: `001-yasl-presence-attribute`

## Defining Field Presence

The `presence` attribute controls whether a field is required, preferred, or optional.

### Required Fields

Fields marked as `required` MUST be present in the data. Missing fields cause a validation **ERROR**.

```yaml
# schema.yasl
definitions:
  User:
    properties:
      username:
        type: str
        presence: required
```

```yaml
# data.yaml (Invalid)
# Missing 'username'
email: "user@example.com"
```

### Preferred Fields

Fields marked as `preferred` SHOULD be present. Missing fields cause a validation **WARNING**, but the data is considered valid.

```yaml
# schema.yasl
definitions:
  User:
    properties:
      description:
        type: str
        presence: preferred
```

```yaml
# data.yaml (Valid with Warning)
# Missing 'description'
username: "jdoe"
```

### Optional Fields

Fields marked as `optional` (or with `presence` omitted) MAY be present. Missing fields are ignored.

```yaml
# schema.yasl
definitions:
  User:
    properties:
      notes:
        type: str
        presence: optional # or omit entirely
```

```yaml
# data.yaml (Valid)
# Missing 'notes'
username: "jdoe"
```
