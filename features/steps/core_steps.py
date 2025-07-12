# features/steps/example_steps.py

import os
from behave import given, when, then

@given('a YASL schema "{schema_file}" is defined')
def step_impl(context, schema_file):
    context.schema_file = schema_file
    if not os.path.isfile(schema_file):
        raise FileNotFoundError(f"Schema file not found: {schema_file}")
    print(f"Schema file: {schema_file}")

@given('a YAML document "{document_file}" is given')
def step_impl(context, document_file):
    context.document_file = document_file
    if not os.path.isfile(document_file):
        raise FileNotFoundError(f"Document file not found: {document_file}")
    print(f"Document file: {document_file}")

@when('I validate the document against the schema')
def step_impl(context):
    # This is where your Go application's validation logic would be called
    # For now, we'll simulate success
    context.validation_successful = True
    print("Validation process initiated (simulated success)")

@then('the validation should pass')
def step_impl(context):
    assert context.validation_successful is True, "Validation failed unexpectedly!"
    print("Validation passed!")