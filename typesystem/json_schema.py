"""
Provides 'typesystem.from_json_schema()' and 'typesystem.to_json_schema()'.
"""
import re
import typing

from typesystem.composites import AllOf, IfThenElse, NeverMatch, Not, OneOf
from typesystem.fields import (
    NO_DEFAULT,
    Any,
    Array,
    Boolean,
    Choice,
    Const,
    Decimal,
    Field,
    Float,
    Integer,
    Number,
    Object,
    String,
    Union,
)
from typesystem.schemas import Definitions, Reference, Schema

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


definitions = Definitions()

JSONSchema = (
    Object(
        properties={
            "$ref": String(),
            "type": String() | Array(items=String()),
            "enum": Array(unique_items=True, min_items=1),
            "definitions": Object(
                additional_properties=Reference("JSONSchema", definitions=definitions)
            ),
            # String
            "minLength": Integer(minimum=0),
            "maxLength": Integer(minimum=0),
            "pattern": String(format="regex"),
            "format": String(),
            # Numeric
            "minimum": Number(),
            "maximum": Number(),
            "exclusiveMinimum": Number(),
            "exclusiveMaximum": Number(),
            "multipleOf": Number(exclusive_minimum=0),
            # Object
            "properties": Object(
                additional_properties=Reference("JSONSchema", definitions=definitions)
            ),
            "minProperties": Integer(minimum=0),
            "maxProperties": Integer(minimum=0),
            "patternProperties": Object(
                additional_properties=Reference("JSONSchema", definitions=definitions)
            ),
            "additionalProperties": (
                Reference("JSONSchema", definitions=definitions) | Boolean()
            ),
            "required": Array(items=String(), unique_items=True),
            # Array
            "items": (
                Reference("JSONSchema", definitions=definitions)
                | Array(
                    items=Reference("JSONSchema", definitions=definitions), min_items=1
                )
            ),
            "additionalItems": (
                Reference("JSONSchema", definitions=definitions) | Boolean()
            ),
            "minItems": Integer(minimum=0),
            "maxItems": Integer(minimum=0),
            "uniqueItems": Boolean(),
        }
    )
    | Boolean()
)

definitions["JSONSchema"] = JSONSchema


def from_json_schema(
    data: typing.Union[bool, dict], definitions: Definitions = None
) -> Field:
    if isinstance(data, bool):
        return {True: Any(), False: NeverMatch()}[data]

    if definitions is None:
        definitions = Definitions()
        for key, value in data.get("definitions", {}).items():
            ref = f"#/definitions/{key}"
            definitions[ref] = from_json_schema(value, definitions=definitions)

    if "$ref" in data:
        return ref_from_json_schema(data, definitions=definitions)

    constraints = []  # typing.List[Field]
    if any([property_name in data for property_name in TYPE_CONSTRAINTS]):
        constraints.append(type_from_json_schema(data, definitions=definitions))
    if "enum" in data:
        constraints.append(enum_from_json_schema(data, definitions=definitions))
    if "const" in data:
        constraints.append(const_from_json_schema(data, definitions=definitions))
    if "allOf" in data:
        constraints.append(all_of_from_json_schema(data, definitions=definitions))
    if "anyOf" in data:
        constraints.append(any_of_from_json_schema(data, definitions=definitions))
    if "oneOf" in data:
        constraints.append(one_of_from_json_schema(data, definitions=definitions))
    if "not" in data:
        constraints.append(not_from_json_schema(data, definitions=definitions))
    if "if" in data:
        constraints.append(if_then_else_from_json_schema(data, definitions=definitions))

    if len(constraints) == 1:
        return constraints[0]
    elif len(constraints) > 1:
        return AllOf(constraints)
    return Any()


def type_from_json_schema(data: dict, definitions: Definitions) -> Field:
    """
    Build a typed field or union of typed fields from a JSON schema object.
    """
    type_strings, allow_null = get_valid_types(data)

    if len(type_strings) > 1:
        items = [
            from_json_schema_type(
                data, type_string=type_string, allow_null=False, definitions=definitions
            )
            for type_string in type_strings
        ]
        return Union(any_of=items, allow_null=allow_null)

    if len(type_strings) == 0:
        return {True: Const(None), False: NeverMatch()}[allow_null]

    type_string = type_strings.pop()
    return from_json_schema_type(
        data, type_string=type_string, allow_null=allow_null, definitions=definitions
    )


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


def from_json_schema_type(
    data: dict, type_string: str, allow_null: bool, definitions: Definitions
) -> Field:
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
            "coerce_types": False,
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
            "coerce_types": False,
        }
        return Integer(**kwargs)

    elif type_string == "string":
        min_length = data.get("minLength", 0)
        kwargs = {
            "allow_null": allow_null,
            "allow_blank": min_length == 0,
            "min_length": min_length if min_length > 1 else None,
            "max_length": data.get("maxLength", None),
            "format": data.get("format"),
            "pattern": data.get("pattern", None),
            "default": data.get("default", NO_DEFAULT),
            "coerce_types": False,
        }
        return String(**kwargs)

    elif type_string == "boolean":
        kwargs = {
            "allow_null": allow_null,
            "default": data.get("default", NO_DEFAULT),
            "coerce_types": False,
        }
        return Boolean(**kwargs)

    elif type_string == "array":
        items = data.get("items", None)
        if items is None:
            items_argument: typing.Union[None, Field, typing.List[Field]] = None
        elif isinstance(items, list):
            items_argument = [
                from_json_schema(item, definitions=definitions) for item in items
            ]
        else:
            items_argument = from_json_schema(items, definitions=definitions)

        additional_items = data.get("additionalItems", None)
        if additional_items is None:
            additional_items_argument: typing.Union[bool, Field] = True
        elif isinstance(additional_items, bool):
            additional_items_argument = additional_items
        else:
            additional_items_argument = from_json_schema(
                additional_items, definitions=definitions
            )

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
            properties_argument: typing.Optional[typing.Dict[str, Field]] = None
        else:
            properties_argument = {
                key: from_json_schema(value, definitions=definitions)
                for key, value in properties.items()
            }

        pattern_properties = data.get("patternProperties", None)
        if pattern_properties is None:
            pattern_properties_argument: typing.Optional[typing.Dict[str, Field]] = None
        else:
            pattern_properties_argument = {
                key: from_json_schema(value, definitions=definitions)
                for key, value in pattern_properties.items()
            }

        additional_properties = data.get("additionalProperties", None)
        if additional_properties is None:
            additional_properties_argument: typing.Union[None, bool, Field] = None
        elif isinstance(additional_properties, bool):
            additional_properties_argument = additional_properties
        else:
            additional_properties_argument = from_json_schema(
                additional_properties, definitions=definitions
            )

        property_names = data.get("propertyNames", None)
        if property_names is None:
            property_names_argument: typing.Optional[Field] = None
        else:
            property_names_argument = from_json_schema(
                property_names, definitions=definitions
            )

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


def ref_from_json_schema(data: dict, definitions: Definitions) -> Field:
    reference_string = data["$ref"]
    assert reference_string.startswith("#/"), "Unsupported $ref style in document."
    return Reference(to=reference_string, definitions=definitions)


def enum_from_json_schema(data: dict, definitions: Definitions) -> Field:
    choices = [(item, item) for item in data["enum"]]
    kwargs = {"choices": choices, "default": data.get("default", NO_DEFAULT)}
    return Choice(**kwargs)


def const_from_json_schema(data: dict, definitions: Definitions) -> Field:
    const = data["const"]
    kwargs = {"const": const, "default": data.get("default", NO_DEFAULT)}
    return Const(**kwargs)


def all_of_from_json_schema(data: dict, definitions: Definitions) -> Field:
    all_of = [from_json_schema(item, definitions=definitions) for item in data["allOf"]]
    kwargs = {"all_of": all_of, "default": data.get("default", NO_DEFAULT)}
    return AllOf(**kwargs)


def any_of_from_json_schema(data: dict, definitions: Definitions) -> Field:
    any_of = [from_json_schema(item, definitions=definitions) for item in data["anyOf"]]
    kwargs = {"any_of": any_of, "default": data.get("default", NO_DEFAULT)}
    return Union(**kwargs)


def one_of_from_json_schema(data: dict, definitions: Definitions) -> Field:
    one_of = [from_json_schema(item, definitions=definitions) for item in data["oneOf"]]
    kwargs = {"one_of": one_of, "default": data.get("default", NO_DEFAULT)}
    return OneOf(**kwargs)


def not_from_json_schema(data: dict, definitions: Definitions) -> Field:
    negated = from_json_schema(data["not"], definitions=definitions)
    kwargs = {"negated": negated, "default": data.get("default", NO_DEFAULT)}
    return Not(**kwargs)


def if_then_else_from_json_schema(data: dict, definitions: Definitions) -> Field:
    if_clause = from_json_schema(data["if"], definitions=definitions)
    then_clause = (
        from_json_schema(data["then"], definitions=definitions)
        if "then" in data
        else None
    )
    else_clause = (
        from_json_schema(data["else"], definitions=definitions)
        if "else" in data
        else None
    )
    kwargs = {
        "if_clause": if_clause,
        "then_clause": then_clause,
        "else_clause": else_clause,
        "default": data.get("default", NO_DEFAULT),
    }
    return IfThenElse(**kwargs)  # type: ignore


def to_json_schema(
    arg: typing.Union[Field, Definitions], _definitions: dict = None
) -> typing.Union[bool, dict]:

    if isinstance(arg, Any):
        return True
    elif isinstance(arg, NeverMatch):
        return False

    field: typing.Optional[Field]
    data: dict = {}
    is_root = _definitions is None
    definitions = {} if _definitions is None else _definitions

    if isinstance(arg, Field):
        field = arg
    elif isinstance(arg, Definitions):
        field = None
        for key, value in arg.items():
            definitions[key] = to_json_schema(value, _definitions=definitions)

    if isinstance(field, Reference):
        data["$ref"] = f"#/definitions/{field.to}"
        definitions[field.to] = to_json_schema(field.target, _definitions=definitions)

    elif isinstance(field, String):
        data["type"] = ["string", "null"] if field.allow_null else "string"
        data.update(get_standard_properties(field))
        if field.min_length is not None or not field.allow_blank:
            data["minLength"] = field.min_length or 1
        if field.max_length is not None:
            data["maxLength"] = field.max_length
        if field.pattern_regex is not None:
            if field.pattern_regex.flags != re.RegexFlag.UNICODE:
                flags = re.RegexFlag(field.pattern_regex.flags)
                raise ValueError(
                    "Cannot convert regular expression with non-standard flags "
                    f"to JSON schema: {flags!s}"
                )
            data["pattern"] = field.pattern_regex.pattern
        if field.format is not None:
            data["format"] = field.format

    elif isinstance(field, (Integer, Float, Decimal)):
        base_type = "integer" if isinstance(field, Integer) else "number"
        data["type"] = [base_type, "null"] if field.allow_null else base_type
        data.update(get_standard_properties(field))
        if field.minimum is not None:
            data["minimum"] = field.minimum
        if field.maximum is not None:
            data["maximum"] = field.maximum
        if field.exclusive_minimum is not None:
            data["exclusiveMinimum"] = field.exclusive_minimum
        if field.exclusive_maximum is not None:
            data["exclusiveMaximum"] = field.exclusive_maximum
        if field.multiple_of is not None:
            data["multipleOf"] = field.multiple_of

    elif isinstance(field, Boolean):
        data["type"] = ["boolean", "null"] if field.allow_null else "boolean"
        data.update(get_standard_properties(field))

    elif isinstance(field, Array):
        data["type"] = ["array", "null"] if field.allow_null else "array"
        data.update(get_standard_properties(field))
        if field.min_items is not None:
            data["minItems"] = field.min_items
        if field.max_items is not None:
            data["maxItems"] = field.max_items
        if field.items is not None:
            if isinstance(field.items, (list, tuple)):
                data["items"] = [
                    to_json_schema(item, _definitions=definitions)
                    for item in field.items
                ]
            else:
                data["items"] = to_json_schema(field.items, _definitions=definitions)
        if field.additional_items is not None:
            if isinstance(field.additional_items, bool):
                data["additionalItems"] = field.additional_items
            else:
                data["additionalItems"] = to_json_schema(
                    field.additional_items, _definitions=definitions
                )
        if field.unique_items is not False:
            data["uniqueItems"] = True

    elif isinstance(field, Object):
        data["type"] = ["object", "null"] if field.allow_null else "object"
        data.update(get_standard_properties(field))
        if field.properties:
            data["properties"] = {
                key: to_json_schema(value, _definitions=definitions)
                for key, value in field.properties.items()
            }
        if field.pattern_properties:
            data["patternProperties"] = {
                key: to_json_schema(value, _definitions=definitions)
                for key, value in field.pattern_properties.items()
            }
        if field.additional_properties is not None:
            if isinstance(field.additional_properties, bool):
                data["additionalProperties"] = field.additional_properties
            else:
                data["additionalProperties"] = to_json_schema(
                    field.additional_properties, _definitions=definitions
                )
        if field.property_names is not None:
            data["propertyNames"] = to_json_schema(
                field.property_names, _definitions=definitions
            )
        if field.max_properties is not None:
            data["maxProperties"] = field.max_properties
        if field.min_properties is not None:
            data["minProperties"] = field.min_properties
        if field.required:
            data["required"] = field.required

    elif isinstance(field, Schema):
        data["type"] = ["object", "null"] if field.allow_null else "object"
        data.update(get_standard_properties(field))
        if field.fields:
            data["properties"] = {
                key: to_json_schema(value, _definitions=definitions)
                for key, value in field.fields.items()
            }
        if field.required:
            data["required"] = field.required

    elif isinstance(field, Choice):
        data["enum"] = [key for key, value in field.choices]
        data.update(get_standard_properties(field))

    elif isinstance(field, Const):
        data["const"] = field.const
        data.update(get_standard_properties(field))

    elif isinstance(field, Union):
        data["anyOf"] = [
            to_json_schema(item, _definitions=definitions) for item in field.any_of
        ]
        data.update(get_standard_properties(field))

    elif isinstance(field, OneOf):
        data["oneOf"] = [
            to_json_schema(item, _definitions=definitions) for item in field.one_of
        ]
        data.update(get_standard_properties(field))

    elif isinstance(field, AllOf):
        data["allOf"] = [
            to_json_schema(item, _definitions=definitions) for item in field.all_of
        ]
        data.update(get_standard_properties(field))

    elif isinstance(field, IfThenElse):
        data["if"] = to_json_schema(field.if_clause, _definitions=definitions)
        if field.then_clause is not None:
            data["then"] = to_json_schema(field.then_clause, _definitions=definitions)
        if field.else_clause is not None:
            data["else"] = to_json_schema(field.else_clause, _definitions=definitions)
        data.update(get_standard_properties(field))

    elif isinstance(field, Not):
        data["not"] = to_json_schema(field.negated, _definitions=definitions)
        data.update(get_standard_properties(field))

    elif field is not None:
        name = type(field).__qualname__
        raise ValueError(f"Cannot convert field type {name!r} to JSON Schema")

    if is_root and definitions:
        data["definitions"] = definitions
    return data


def get_standard_properties(field: Field) -> dict:
    data = {}
    if field.has_default():
        data["default"] = field.default
    return data
