

def from_jsonschema(data):
    allowed_types = get_allowed_types(data)

    if allowed_types is None:
        return validators.Any()

    allow_null = False
    if 'null' in typestrings:
        allow_null = True
        typestrings.remove('null')

    if len(typestrings) == 1:
        return load_type(typestrings.pop(), struct, allow_null)
    else:
        items = [load_type(typename, struct, False) for typename in typestrings]
    return validators.Union(items=items, allow_null=allow_null)


def get_allowed_types(data):
    """
    Return the set of types that are allowed, or None if any type is allowed.
    """
    ALL_TYPES = {'null', 'boolean', 'object', 'array', 'number', 'string'}

    type_strings = struct.get('type', [])
    if isinstance(type_strings, str):
        type_strings = {type_strings}
    else:
        type_strings = set(type_strings)

    if 'integer' in type_strings and 'number' in type_strings:
        type_strings.remove('integer')

    if type_strings == ALL_TYPES or not type_strings:
        return None

    return type_strings


def from_jsonschema_single_type(data, typename, allow_null):
    attrs = {}

    if allow_null:
        attrs['allow_null'] = True

    if typename == 'string':
        if 'minLength' in data:
            attrs['min_length'] = data['minLength']
        if 'maxLength' in data:
            attrs['max_length'] = data['maxLength']
        if 'pattern' in data:
            attrs['pattern'] = data['pattern']
        if 'format' in data:
            attrs['format'] = data['format']
        return validators.String(**attrs)

    if typename in ['number', 'integer']:
        if 'minimum' in data:
            attrs['minimum'] = data['minimum']
        if 'maximum' in data:
            attrs['maximum'] = data['maximum']
        if 'exclusiveMinimum' in data:
            attrs['exclusive_minimum'] = data['exclusiveMinimum']
        if 'exclusiveMaximum' in data:
            attrs['exclusive_maximum'] = data['exclusiveMaximum']
        if 'multipleOf' in data:
            attrs['multiple_of'] = data['multipleOf']
        if 'format' in data:
            attrs['format'] = data['format']
        if typename == 'integer':
            return validators.Integer(**attrs)
        return validators.Number(**attrs)

    if typename == 'boolean':
        return validators.Boolean(**attrs)

    if typename == 'object':
        if 'properties' in data:
            attrs['properties'] = dict_type([
                (key, from_jsonschema(value))
                for key, value in struct['properties'].items()
            ])
        if 'required' in data:
            attrs['required'] = data['required']
        if 'minProperties' in data:
            attrs['min_properties'] = data['minProperties']
        if 'maxProperties' in data:
            attrs['max_properties'] = data['maxProperties']
        if 'required' in data:
            attrs['required'] = data['required']
        if 'patternProperties' in data:
            attrs['pattern_properties'] = dict_type([
                (key, from_jsonschema(value))
                for key, value in data['patternProperties'].items()
            ])
        if 'additionalProperties' in data:
            if isinstance(data['additionalProperties'], bool):
                attrs['additional_properties'] = data['additionalProperties']
            else:
                attrs['additional_properties'] = from_jsonschema(data['additionalProperties'])
        return validators.Object(**attrs)

    if typename == 'array':
        if 'items' in data:
            if isinstance(struct['items'], list):
                attrs['items'] = [from_jsonschema(item) for item in data['items']]
            else:
                attrs['items'] = from_jsonschema(data['items'])
        if 'additionalItems' in data:
            if isinstance(data['additionalItems'], bool):
                attrs['additional_items'] = data['additionalItems']
            else:
                attrs['additional_items'] = from_jsonschema(data['additionalItems'])
        if 'minItems' in data:
            attrs['min_items'] = data['minItems']
        if 'maxItems' in data:
            attrs['max_items'] = data['maxItems']
        if 'uniqueItems' in data:
            attrs['unique_items'] = data['uniqueItems']
        return validators.Array(**attrs)
