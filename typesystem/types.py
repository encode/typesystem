from typesystem import validators

RESERVED_KEYS = ["validator"]
RESERVED_KEY_MESSAGE = (
    'Cannot use reserved name "%s" on Type "%s", '
    "as it clashes with the class interface."
)


class TypeMetaclass(type):
    def __new__(cls, name, bases, attrs):
        fields = []
        for key, value in list(attrs.items()):
            assert key not in RESERVED_KEYS, RESERVED_KEY_MESSAGE

            if hasattr(value, "validate"):
                attrs.pop(key)
                fields.append((key, value))

        # If this class is subclassing another Type, add that Type's properties.
        # Note that we loop over the bases in reverse. This is necessary in order
        # to maintain the correct order of properties.
        for base in reversed(bases):
            if hasattr(base, "fields"):
                fields = [
                    (key, base.fields[key]) for key in base.fields if key not in attrs
                ] + fields

        fields = sorted(fields, key=lambda item: item[1]._creation_counter)
        attrs["fields"] = dict(fields)
        return super(TypeMetaclass, cls).__new__(cls, name, bases, attrs)


class Type(metaclass=TypeMetaclass):
    def __init__(self, *args, **kwargs):
        if args:
            assert len(args) == 1
            assert not kwargs
            item = dict(args[0])
        else:
            item = kwargs

        for key, schema in self.fields.items():
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
        required = [key for key, value in cls.fields.items() if not value.has_default()]
        validator = validators.Object(
            properties=cls.fields,
            required=required,
            additional_properties=None,
            coerce=cls,
        )
        return validator.validate(value, strict=strict)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        for key in self.fields.keys():
            if getattr(self, key) != getattr(other, key):
                return False
        return True
