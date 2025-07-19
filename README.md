# YASL YAML Advanced Schema Language

YASL is an advanced schema language & validation tools for YAML. 
It supports validation of primitive data types, complex structures, enumerated values, and reference validation.
Designed for high performance in Go, YASL also provides convenient wrappers for Python and JavaScript, making it easy to integrate adavnced YAML validation into a variety of environments.

_Note:  At some point we may expand this to support JSON files as well.
Unfortunately, there is no good "out of the box" solution for JSON parsing that produces an abstract syntax tree (AST) with file location metadata (similar to Go's yaml.v3).
Given the importance of high quality user warning and error feedback (with specific file and location information), we'll limit ourselves to YAML for now._
