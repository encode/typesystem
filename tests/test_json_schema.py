import json
import os

import pytest

from typesystem.json_schema import from_json_schema

filenames = [
    "additionalItems.json",
    "additionalProperties.json",
    # "allOf.json",
    # "anyOf.json",
    "boolean_schema.json",
    # "const.json",
    # "contains.json",
    "default.json",
    # "definitions.json",
    # "dependencies.json",
    # "enum.json",
    "exclusiveMaximum.json",
    "exclusiveMinimum.json",
    # "if-then-else.json",
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
    # "not.json",
    # "oneOf.json",
    "pattern.json",
    "patternProperties.json",
    "properties.json",
    # "propertyNames.json",
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
