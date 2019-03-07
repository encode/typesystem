import typing

from typesystem.fields import (
    NO_DEFAULT,
    Any,
    Array,
    Boolean,
    Choice,
    Field,
    Float,
    Integer,
    Never,
    Null,
    Object,
    String,
    Union,
)

TYPE_CONSTRAINTS = {
    "additionalItems",
    "additionalProperties",
    "boolean_schema",
    "contains",
    "dependencies",
    "exclusiveMaximum",
    "exclusiveMinimum",
    "items",
    "maxItems",
    "maxLength",
    "maxProperties",
    "maximum",
    "minItems",
    "minLength",
    "minProperties",
    "minimum",
    "multipleOf",
    "pattern",
    "patternProperties",
    "properties",
    "propertyNames",
    "required",
    "type",
    "uniqueItems",
}

# "allOf.json",
# "anyOf.json",
# "const.json",
# "enum.json",
# "if-then-else.json",
# "not.json",
# "oneOf.json",


def from_json_schema(data: typing.Union[bool, dict]) -> Field:
    if isinstance(data, bool):
        return {True: Any(), False: Never()}[data]

    constraints = []  # typing.List[Field]
    if any([property_name in data for property_name in TYPE_CONSTRAINTS]):
        constraints.append(type_from_json_schema(data))
    if "enum" in data:
        constraints.append(enum_from_json_schema(data))

    if len(constraints) == 1:
        return constraints[0]
    return Any()


def type_from_json_schema(data: dict) -> Field:
    """
    Build a typed field or union of typed fields from a JSON schema object.
    """
    type_strings, allow_null = get_valid_types(data)

    if len(type_strings) > 1:
        items = [
            from_json_schema_type(data, type_string=type_string, allow_null=False)
            for type_string in type_strings
        ]
        return Union(any_of=items, allow_null=allow_null)

    if len(type_strings) == 0:
        return {True: Null(), False: Never()}[allow_null]

    type_string = type_strings.pop()
    return from_json_schema_type(data, type_string=type_string, allow_null=allow_null)


def get_valid_types(data: dict) -> typing.Tuple[typing.Set[str], bool]:
    """
    Returns a two-tuple of `(type_strings, allow_null)`.
    """

    type_strings = data.get("type", [])
    if isinstance(type_strings, str):
        type_strings = {type_strings}
    else:
        type_strings = set(type_strings)

    if not type_strings:
        type_strings = {"null", "boolean", "object", "array", "number", "string"}

    if "number" in type_strings:
        type_strings.discard("integer")

    allow_null = False
    if "null" in type_strings:
        allow_null = True
        type_strings.remove("null")

    return (type_strings, allow_null)


def from_json_schema_type(data: dict, type_string: str, allow_null: bool) -> Field:
    """
    Build a typed field from a JSON schema object.
    """

    if type_string == "number":
        kwargs = {
            "allow_null": allow_null,
            "minimum": data.get("minimum", None),
            "maximum": data.get("maximum", None),
            "exclusive_minimum": data.get("exclusiveMinimum", None),
            "exclusive_maximum": data.get("exclusiveMaximum", None),
            "multiple_of": data.get("multipleOf", None),
            "default": data.get("default", NO_DEFAULT),
        }
        return Float(**kwargs)

    elif type_string == "integer":
        kwargs = {
            "allow_null": allow_null,
            "minimum": data.get("minimum", None),
            "maximum": data.get("maximum", None),
            "exclusive_minimum": data.get("exclusiveMinimum", None),
            "exclusive_maximum": data.get("exclusiveMaximum", None),
            "multiple_of": data.get("multipleOf", None),
            "default": data.get("default", NO_DEFAULT),
        }
        return Integer(**kwargs)

    elif type_string == "string":
        min_length = data.get("minLength", 0)
        kwargs = {
            "allow_null": allow_null,
            "allow_blank": min_length == 0,
            "min_length": min_length if min_length > 1 else None,
            "max_length": data.get("maxLength", None),
            "pattern": data.get("pattern", None),
            "default": data.get("default", NO_DEFAULT),
        }
        return String(**kwargs)

    elif type_string == "boolean":
        kwargs = {"allow_null": allow_null, "default": data.get("default", NO_DEFAULT)}
        return Boolean(**kwargs)

    elif type_string == "array":
        items = data.get("items", None)
        if items is None:
            items_argument = None  # type: typing.Union[None, Field, typing.List[Field]]
        elif isinstance(items, list):
            items_argument = [from_json_schema(item) for item in items]
        else:
            items_argument = from_json_schema(items)

        additional_items = data.get("additionalItems", None)
        if additional_items is None:
            additional_items_argument = True  # type: typing.Union[bool, Field]
        elif isinstance(additional_items, bool):
            additional_items_argument = additional_items
        else:
            additional_items_argument = from_json_schema(additional_items)

        kwargs = {
            "allow_null": allow_null,
            "min_items": data.get("minItems", 0),
            "max_items": data.get("maxItems", None),
            "additional_items": additional_items_argument,
            "items": items_argument,
            "unique_items": data.get("uniqueItems", False),
            "default": data.get("default", NO_DEFAULT),
        }
        return Array(**kwargs)

    elif type_string == "object":
        properties = data.get("properties", None)
        if properties is None:
            properties_argument = None  # type: typing.Optional[typing.Dict[str, Field]]
        else:
            properties_argument = {
                key: from_json_schema(value) for key, value in properties.items()
            }

        pattern_properties = data.get("patternProperties", None)
        if pattern_properties is None:
            pattern_properties_argument = (
                None
            )  # type: typing.Optional[typing.Dict[str, Field]]
        else:
            pattern_properties_argument = {
                key: from_json_schema(value)
                for key, value in pattern_properties.items()
            }

        additional_properties = data.get("additionalProperties", None)
        if additional_properties is None:
            additional_properties_argument = (
                None
            )  # type: typing.Union[None, bool, Field]
        elif isinstance(additional_properties, bool):
            additional_properties_argument = additional_properties
        else:
            additional_properties_argument = from_json_schema(additional_properties)

        property_names = data.get("propertyNames", None)
        if property_names is None:
            property_names_argument = None  # type: typing.Optional[Field]
        else:
            property_names_argument = from_json_schema(property_names)

        kwargs = {
            "allow_null": allow_null,
            "properties": properties_argument,
            "pattern_properties": pattern_properties_argument,
            "additional_properties": additional_properties_argument,
            "property_names": property_names_argument,
            "min_properties": data.get("minProperties", None),
            "max_properties": data.get("maxProperties", None),
            "required": data.get("required", None),
            "default": data.get("default", NO_DEFAULT),
        }
        return Object(**kwargs)

    assert False, f"Invalid argument type_string={type_string!r}"  # pragma: no cover


def enum_from_json_schema(data: dict) -> Field:
    choices = [(item, item) for item in data["enum"]]
    kwargs = {"choices": choices, "default": data.get("default", NO_DEFAULT)}
    return Choice(**kwargs)
