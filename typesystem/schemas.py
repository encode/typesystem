import typing
from abc import ABCMeta
from collections.abc import Mapping, MutableMapping

from typesystem.base import ValidationError, ValidationResult
from typesystem.fields import Array, Field, Object


class SchemaDefinitions(MutableMapping):
    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        self._definitions = dict(*args, **kwargs)  # type: dict

    def __getitem__(self, key: typing.Any) -> typing.Any:
        return self._definitions[key]

    def __iter__(self) -> typing.Iterator[typing.Any]:
        return iter(self._definitions)

    def __len__(self) -> int:
        return len(self._definitions)

    def __setitem__(self, key: typing.Any, value: typing.Any) -> None:
        assert (
            key not in self._definitions
        ), r"Definition for {key!r} has already been set."
        self._definitions[key] = value

    def __delitem__(self, key: typing.Any) -> None:
        del self._definitions[key]


def set_definitions(field: Field, definitions: SchemaDefinitions) -> None:
    """
    Recursively set the definitions that string-referenced `Reference` fields
    should use.
    """
    if isinstance(field, Reference) and field.definitions is None:
        field.definitions = definitions
    elif isinstance(field, Array):
        if field.items is not None:
            if isinstance(field.items, (tuple, list)):
                for child in field.items:
                    set_definitions(child, definitions)
            else:
                set_definitions(field.items, definitions)
    elif isinstance(field, Object):
        for child in field.properties.values():
            set_definitions(child, definitions)


class SchemaMetaclass(ABCMeta):
    def __new__(
        cls: type,
        name: str,
        bases: typing.Sequence[type],
        attrs: dict,
        definitions: SchemaDefinitions = None,
    ) -> type:
        fields: typing.Dict[str, Field] = {}

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

        # Add the definitions to any `Reference` fields that we're including.
        if definitions is not None:
            for field in fields.values():
                set_definitions(field, definitions)

        #  Sort fields by their actual position in the source code,
        # using `Field._creation_counter`
        attrs["fields"] = dict(
            sorted(fields.items(), key=lambda item: item[1]._creation_counter)
        )

        new_type = super(SchemaMetaclass, cls).__new__(  # type: ignore
            cls, name, bases, attrs
        )
        if definitions is not None:
            definitions[name] = new_type
        return new_type


class Schema(Mapping, metaclass=SchemaMetaclass):
    fields: typing.Dict[str, Field] = {}

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
        try:
            field = self.fields[key]
            value = getattr(self, key)
        except (KeyError, AttributeError):
            raise KeyError(key) from None
        else:
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


class Reference(Field):
    errors = {"null": "May not be null."}

    def __init__(
        self,
        to: typing.Union[str, typing.Type[Schema]],
        definitions: typing.Mapping = None,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(**kwargs)
        self.to = to
        self.definitions = definitions
        if isinstance(to, str):
            self._target_string = to
        else:
            assert issubclass(to, Schema)
            self._target = to

    @property
    def target_string(self) -> str:
        if not hasattr(self, "_target_string"):
            self._target_string = self._target.__name__
        return self._target_string

    @property
    def target(self) -> typing.Union[Field, typing.Type[Schema]]:
        if not hasattr(self, "_target"):
            assert (
                self.definitions is not None
            ), "String reference missing 'definitions'."
            self._target = self.definitions[self.to]
        return self._target

    def validate(self, value: typing.Any, *, strict: bool = False) -> typing.Any:
        if value is None and self.allow_null:
            return None
        elif value is None:
            raise self.validation_error("null")
        return self.target.validate(value, strict=strict)

    def serialize(self, obj: typing.Any) -> typing.Any:
        if obj is None:
            return None
        return dict(obj)
