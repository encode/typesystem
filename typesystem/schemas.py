from abc import ABCMeta
from collections.abc import Mapping

from typesystem.fields import Field, Object


class SchemaMetaclass(ABCMeta):
    def __new__(cls, name, bases, attrs):
        fields = []
        for key, value in list(attrs.items()):
            if isinstance(value, Field):
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
        return super(SchemaMetaclass, cls).__new__(cls, name, bases, attrs)


class Schema(Mapping, metaclass=SchemaMetaclass):
    def __init__(self, *args, **kwargs):
        if args:
            assert len(args) == 1
            assert not kwargs
            item = args[0]
            if isinstance(item, dict):
                for key in self.fields.keys():
                    if key in item:
                        setattr(self, key, item[key])
            else:
                for key in self.fields.keys():
                    if hasattr(item, key):
                        setattr(self, key, getattr(item, key))
            return

        for key, schema in self.fields.items():
            if key in kwargs:
                value = kwargs.pop(key)
                value, errors = schema.validate(value)
                if errors:
                    class_name = self.__class__.__name__
                    error_text = list(errors)[0].text
                    message = (
                        f"Invalid argument {key!r} for {class_name}(). {error_text}"
                    )
                    raise TypeError(message)
                setattr(self, key, value)
            elif schema.has_default():
                setattr(self, key, schema.default)

        if kwargs:
            key = list(kwargs.keys())[0]
            class_name = self.__class__.__name__
            message = f"{key!r} is an invalid keyword argument for {class_name}()."
            raise TypeError(message)

    @classmethod
    def validate(cls, value, strict=False):
        required = [key for key, value in cls.fields.items() if not value.has_default()]
        validator = Object(
            properties=cls.fields,
            required=required,
            additional_properties=False if strict else None,
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

    def __getitem__(self, key):
        if key not in self.fields or not hasattr(self, key):
            raise KeyError(key)
        field = self.fields[key]
        value = getattr(self, key)
        return field.serialize(value)

    def __iter__(self):
        for key in self.fields:
            if hasattr(self, key):
                yield key

    def __len__(self):
        return len([key for key in self.fields if hasattr(self, key)])
