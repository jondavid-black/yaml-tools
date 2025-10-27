# features/steps/example_steps.py

import subprocess
import os
from behave import given, when, then

def run_cli(args):
    filtered_args = [item for item in args if item is not None]
    result = subprocess.run(
        ["yasl"] + filtered_args,
        capture_output=True,
        text=True
    )
    return result

@given('a YASL schema "{schema_file}" is provided')
def step_impl(context, schema_file):
    context.schema_argument = schema_file
    if not os.path.exists(schema_file):
        raise FileNotFoundError(f"Schema file not found: {schema_file}")
    print(f"Schema file: {schema_file}")

@given('a YAML document "{document_file}" is provided')
def step_impl(context, document_file):
    context.document_argument = document_file
    if not os.path.exists(document_file):
        raise FileNotFoundError(f"Document file not found: {document_file}")
    print(f"Document file: {document_file}")

@given(u'the model name "{model_name}" is provided')
def step_impl(context, model_name):
    context.model_name = model_name

@when('I run the YASL CLI with provided arguments')
def step_impl(context):
    # This is where your Go application's validation logic would be called
    # For now, we'll simulate success
    result = run_cli([context.schema_argument, context.document_argument, getattr(context, "model_name", None)])
    print(f"CLI Output:\n{result.stdout}")
    context.validation_successful = result.returncode == 0

@then('the validation should pass')
def step_impl(context):
    assert context.validation_successful is True, "Validation failed unexpectedly!"
    print("Validation passed!")

@then('the validation should fail')
def step_impl(context):
    assert context.validation_successful is False, "Validation succeeded unexpectedly!"
    print("Validation failed as expected!")