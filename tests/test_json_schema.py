import json
import os
import re

import pytest

import typesystem
from typesystem.json_schema import JSONSchema, from_json_schema, to_json_schema

filenames = [
    "additionalItems.json",
    "additionalProperties.json",
    "allOf.json",
    "anyOf.json",
    "boolean_schema.json",
    "const.json",
    # "contains.json",
    "default.json",
    # "definitions.json",
    "definitionsRef.json",
    # "dependencies.json",
    "enum.json",
    "exclusiveMaximum.json",
    "exclusiveMinimum.json",
    "if-then-else.json",
    "items.json",
    "maxItems.json",
    "maxLength.json",
    "maxProperties.json",
    "maximum.json",
    "minItems.json",
    "minLength.json",
    "minProperties.json",
    "minimum.json",
    "multipleOf.json",
    "not.json",
    "oneOf.json",
    "pattern.json",
    "patternProperties.json",
    "properties.json",
    "propertyNames.json",
    # "ref.json",
    # "refRemote.json",
    "required.json",
    "type.json",
    "uniqueItems.json",
]


def load_test_cases():
    loaded = []

    for filename in filenames:
        path = os.path.join("tests", "jsonschema", "draft7", filename)
        content = open(path, "rb").read()
        test_suite = json.loads(content.decode("utf-8"))
        for test_cases in test_suite:
            description = test_cases["description"]
            schema = test_cases["schema"]
            for test in test_cases["tests"]:
                test_description = test["description"]
                test_data = test["data"]
                test_valid = test["valid"]
                full_description = "%s : %s - %s" % (
                    filename,
                    description,
                    test_description,
                )
                case = (schema, test_data, test_valid, full_description)
                loaded.append(case)

    return loaded


test_cases = load_test_cases()


@pytest.mark.parametrize("schema,data,is_valid,description", test_cases)
def test_json_schema(schema, data, is_valid, description):
    validator = from_json_schema(schema)
    value, error = validator.validate_or_error(data, strict=True)
    if is_valid:
        assert error is None, description
    else:
        assert error is not None, description


@pytest.mark.parametrize("schema,data,is_valid,description", test_cases)
def test_json_schema_validator(schema, data, is_valid, description):
    """
    Use the `JSONSchema` field to validate all the test case schemas.
    """
    JSONSchema.validate(schema)


@pytest.mark.parametrize("schema,data,is_valid,description", test_cases)
def test_to_from_json_schema(schema, data, is_valid, description):
    """
    Test that marshalling to and from JSON schema doens't affect the
    behavior of the validation.

    Ie. `new_field = from_json_schema(to_json_schema(initial_field))` should
    always result in `new_field` having the same behavior as `initial_field`.
    """
    validator = from_json_schema(schema)

    value_before_convert, error_before_convert = validator.validate_or_error(
        data, strict=True
    )

    schema_after = to_json_schema(validator)
    validator = from_json_schema(schema_after)

    value_after_convert, error_after_convert = validator.validate_or_error(
        data, strict=True
    )

    assert error_before_convert == error_after_convert
    assert value_before_convert == value_after_convert


def test_schema_to_json_schema():
    class BookingSchema(typesystem.Schema):
        start_date = typesystem.Date(title="Start date")
        end_date = typesystem.Date(title="End date")
        room = typesystem.Choice(
            title="Room type",
            choices=[
                ("double", "Double room"),
                ("twin", "Twin room"),
                ("single", "Single room"),
            ],
        )
        include_breakfast = typesystem.Boolean(title="Include breakfast", default=False)

    schema = to_json_schema(BookingSchema)

    assert schema == {
        "type": "object",
        "properties": {
            "start_date": {"type": "string", "format": "date", "minLength": 1},
            "end_date": {"type": "string", "format": "date", "minLength": 1},
            "room": {"enum": ["double", "twin", "single"]},
            "include_breakfast": {"type": "boolean", "default": False},
        },
        "required": ["start_date", "end_date", "room"],
    }


class CustomField(typesystem.Field):
    pass


def test_to_json_schema_invalid_field():
    field = CustomField()
    with pytest.raises(ValueError) as exc_info:
        to_json_schema(field)

    expected = "Cannot convert field type 'CustomField' to JSON Schema"
    assert str(exc_info.value) == expected


def test_to_json_schema_complex_regular_expression():
    field = typesystem.String(pattern=re.compile("foo", re.IGNORECASE | re.VERBOSE))
    with pytest.raises(ValueError) as exc_info:
        to_json_schema(field)

    expected = (
        "Cannot convert regular expression with non-standard flags "
        "to JSON schema: RegexFlag."
    )
    assert str(exc_info.value).startswith(expected)
