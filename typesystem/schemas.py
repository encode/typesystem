import typing
from abc import ABCMeta
from collections.abc import Mapping

from typesystem.base import ValidationError, ValidationResult
from typesystem.fields import Field, Object


class SchemaMetaclass(ABCMeta):
    def __new__(
        cls: type, name: str, bases: typing.Sequence[type], attrs: dict
    ) -> type:
        fields = {}  # type: typing.Dict[str, Field]

        for key, value in list(attrs.items()):
            if isinstance(value, Field):
                attrs.pop(key)
                fields[key] = value

        # If this class is subclassing other Schema classes, add their fields.
        for base in reversed(bases):
            base_fields = getattr(base, "fields", {})
            for key, value in base_fields.items():
                if isinstance(value, Field) and key not in fields:
                    fields[key] = value

        #  Sort fields by their actual position in the source code,
        # using `Field._creation_counter`
        attrs["fields"] = dict(
            sorted(fields.items(), key=lambda item: item[1]._creation_counter)
        )

        return super(SchemaMetaclass, cls).__new__(  # type: ignore
            cls, name, bases, attrs
        )


class Schema(Mapping, metaclass=SchemaMetaclass):
    fields = {}  # type: typing.Dict[str, Field]

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
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
                value, error = schema.validate_or_error(value)
                if error:
                    class_name = self.__class__.__name__
                    error_text = " ".join(
                        [message.text for message in error.messages()]
                    )
                    message = (
                        f"Invalid argument {key!r} for {class_name}(). {error_text}"
                    )
                    raise TypeError(message)
                setattr(self, key, value)
            elif schema.has_default():
                setattr(self, key, schema.get_default_value())

        if kwargs:
            key = list(kwargs.keys())[0]
            class_name = self.__class__.__name__
            message = f"{key!r} is an invalid keyword argument for {class_name}()."
            raise TypeError(message)

    @classmethod
    def make_validator(cls: typing.Type["Schema"], *, strict: bool = False) -> Field:
        required = [key for key, value in cls.fields.items() if not value.has_default()]
        return Object(
            properties=cls.fields,
            required=required,
            additional_properties=False if strict else None,
        )

    @classmethod
    def validate(
        cls: typing.Type["Schema"], value: typing.Any, *, strict: bool = False
    ) -> "Schema":
        validator = cls.make_validator(strict=strict)
        value = validator.validate(value, strict=strict)
        return cls(value)

    @classmethod
    def validate_or_error(
        cls: typing.Type["Schema"], value: typing.Any, *, strict: bool = False
    ) -> ValidationResult:
        try:
            value = cls.validate(value, strict=strict)
        except ValidationError as error:
            return ValidationResult(value=None, error=error)
        return ValidationResult(value=value, error=None)

    @property
    def is_sparse(self) -> bool:
        # A schema is sparsely populated if it does not include attributes
        # for all its fields.
        return bool([key for key in self.fields.keys() if not hasattr(self, key)])

    def __eq__(self, other: typing.Any) -> bool:
        if not isinstance(other, self.__class__):
            return False

        for key in self.fields.keys():
            if getattr(self, key) != getattr(other, key):
                return False
        return True

    def __getitem__(self, key: typing.Any) -> typing.Any:
        if key not in self.fields or not hasattr(self, key):
            raise KeyError(key)
        field = self.fields[key]
        value = getattr(self, key)
        return field.serialize(value)

    def __iter__(self) -> typing.Iterator[str]:
        for key in self.fields:
            if hasattr(self, key):
                yield key

    def __len__(self) -> int:
        return len([key for key in self.fields if hasattr(self, key)])

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        arguments = {
            key: getattr(self, key) for key in self.fields.keys() if hasattr(self, key)
        }
        argument_str = ", ".join(
            [f"{key}={value!r}" for key, value in arguments.items()]
        )
        sparse_indicator = " [sparse]" if self.is_sparse else ""
        return f"{class_name}({argument_str}){sparse_indicator}"
