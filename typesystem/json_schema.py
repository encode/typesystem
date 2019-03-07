from typesystem.fields import Field, Float, Integer, Union, String, Boolean, Object, Array
import typing


def from_json_schema(data: typing.Any) -> Field:
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
    type_strings = data.get('type', [])
    if isinstance(type_strings, str):
        type_strings = {type_strings}
    else:
        type_strings = set(type_strings)

    if not type_strings:
        type_strings = {
            'null', 'boolean', 'object',
            'array', 'number', 'string'
        }

    if 'integer' in type_strings and 'number' in type_strings:
        type_strings.remove('integer')

    allow_null = False
    if 'null' in type_strings:
        allow_null = True
        type_strings.remove('null')

    return (type_strings, allow_null)


def from_json_schema_type(data: dict, type_string: str, allow_null: bool) -> Field:
    if type_string == 'number':
        kwargs = {
            'minimum': data.get('minimum', None),
            'maximum': data.get('maximum', None),
            'exclusive_minimum': data.get('exclusiveMinimum', None),
            'exclusive_maximum': data.get('exclusiveMaximum', None),
            'allow_null': allow_null
        }
        return Float(**kwargs)
    elif type_string == 'integer':
        kwargs = {
            'minimum': data.get('minimum', None),
            'maximum': data.get('maximum', None),
            'exclusive_minimum': data.get('exclusiveMinimum', None),
            'exclusive_maximum': data.get('exclusiveMaximum', None),
            'allow_null': allow_null
        }
        return Integer(**kwargs)
    elif type_string == 'string':
        return String(allow_blank=True)
    elif type_string == 'boolean':
        return Boolean()
    elif type_string == 'array':
        return Array()
    elif type_string == 'object':
        return Object()
