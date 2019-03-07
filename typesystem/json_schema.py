import typing

from typesystem.fields import (
    Any,
    Array,
    Boolean,
    Field,
    Float,
    Integer,
    Never,
    Object,
    String,
    Union,
)


def from_json_schema(data: typing.Union[bool, dict]) -> Field:
    if isinstance(data, bool):
        return {True: Any(), False: Never()}[data]

    type_strings, allow_null = get_valid_types(data)

    if len(type_strings) > 1:
        items = [
            from_json_schema_type(data, type_string=type_string, allow_null=False)
            for type_string in type_strings
        ]
        return Union(any_of=items, allow_null=allow_null)

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
    if type_string == "number":
        kwargs = {
            "allow_null": allow_null,
            "minimum": data.get("minimum", None),
            "maximum": data.get("maximum", None),
            "exclusive_minimum": data.get("exclusiveMinimum", None),
            "exclusive_maximum": data.get("exclusiveMaximum", None),
            "multiple_of": data.get("multipleOf", None),
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
        }
        return String(**kwargs)
    elif type_string == "boolean":
        kwargs = {"allow_null": allow_null}
        return Boolean(**kwargs)
    elif type_string == "array":
        items = data.get("items", None)
        if items is None:
            items_argument = (
                None
            )  # type: typing.Optional[typing.Union[Field, typing.List[Field]]]
        elif isinstance(items, list):
            items_argument = [from_json_schema(item) for item in items]
        else:
            items_argument = from_json_schema(items)

        kwargs = {
            "allow_null": allow_null,
            "min_items": data.get("minItems", 0),
            "max_items": data.get("maxItems", None),
            "additional_items": data.get("additionalItems", True),
            "items": items_argument,
        }
        return Array(**kwargs)
    elif type_string == "object":
        kwargs = {
            "allow_null": allow_null,
            "min_properties": data.get("minProperties", None),
            "max_properties": data.get("maxProperties", None),
            "required": data.get("required", None),
        }
        return Object(**kwargs)

    assert False, f"Invalid argument type_string={type_string!r}"  # pragma: no cover
