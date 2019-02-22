from typesystem import validators

RESERVED_KEYS = ["validator"]
RESERVED_KEY_MESSAGE = (
    'Cannot use reserved name "%s" on Type "%s", '
    "as it clashes with the class interface."
)


class TypeMetaclass(type):
    def __new__(cls, name, bases, attrs):
        properties = []
        for key, value in list(attrs.items()):
            assert key not in RESERVED_KEYS, RESERVED_KEY_MESSAGE

            if hasattr(value, "validate"):
                attrs.pop(key)
                properties.append((key, value))

        # If this class is subclassing another Type, add that Type's properties.
        # Note that we loop over the bases in reverse. This is necessary in order
        # to maintain the correct order of properties.
        for base in reversed(bases):
            if hasattr(base, "validator"):
                properties = [
                    (key, base.validator.properties[key])
                    for key in base.validator.properties
                    if key not in attrs
                ] + properties

        properties = sorted(properties, key=lambda item: item[1]._creation_counter)
        required = [key for key, value in properties if not value.has_default()]

        attrs["validator"] = validators.Object(
            def_name=name,
            properties=properties,
            required=required,
            additional_properties=None,
        )
        attrs["_creation_counter"] = validators.Validator._creation_counter
        validators.Validator._creation_counter += 1
        ret = super(TypeMetaclass, cls).__new__(cls, name, bases, attrs)
        ret.validator.coerce = ret
        return ret


class Type(metaclass=TypeMetaclass):
    def __init__(self, *args, **kwargs):
        if args:
            assert len(args) == 1
            assert not kwargs
            item = dict(args[0])
        else:
            item = kwargs

        for key, schema in self.validator.properties.items():
            if key in item:
                setattr(self, key, item.pop(key))
            elif schema.has_default():
                setattr(self, key, schema.default)
            else:
                raise TypeError("Missing required argument {key!r}")

        if item:
            key = list(item.keys())[0]
            raise TypeError("Invalid argument {!r}")

    @classmethod
    def validate(cls, value, strict=False):
        return cls.validator.validate(value, strict=strict)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        for key in self.validator.properties.keys():
            if getattr(self, key) != getattr(other, key):
                return False
        return True
