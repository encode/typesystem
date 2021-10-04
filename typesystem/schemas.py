import typing
from collections.abc import MutableMapping

from typesystem.base import ValidationError
from typesystem.fields import Field, Message


class Schema(Field):
    errors = {
        "type": "Must be an object.",
        "null": "May not be null.",
        "invalid_key": "All object keys must be strings.",
        "required": "This field is required.",
    }

    def __init__(
        self,
        fields: typing.Dict[str, Field],
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(**kwargs)
        self.fields = fields
        self.required = [
            key
            for key, field in fields.items()
            if not (field.read_only or field.has_default())
        ]

    def validate(self, value: typing.Any) -> typing.Any:
        if value is None and self.allow_null:
            return None
        elif value is None:
            raise self.validation_error("null")
        elif not isinstance(value, (dict, typing.Mapping)):
            raise self.validation_error("type")

        validated = {}
        error_messages = []

        # Ensure all property keys are strings.
        for key in value.keys():
            if not isinstance(key, str):
                text = self.get_error_text("invalid_key")
                message = Message(text=text, code="invalid_key", index=[key])
                error_messages.append(message)

        # Required properties
        for key in self.required:
            if key not in value:
                text = self.get_error_text("required")
                message = Message(text=text, code="required", index=[key])
                error_messages.append(message)

        # Properties
        for key, child_schema in self.fields.items():
            if child_schema.read_only:
                continue

            if key not in value:
                if child_schema.has_default():
                    validated[key] = child_schema.get_default_value()
                continue
            item = value[key]
            child_value, error = child_schema.validate_or_error(item)
            if not error:
                validated[key] = child_value
            else:
                error_messages += error.messages(add_prefix=key)

        if error_messages:
            raise ValidationError(messages=error_messages)

        return validated

    def serialize(
        self, obj: typing.Any
    ) -> typing.Optional[typing.Dict[str, typing.Any]]:
        if obj is None:
            return None

        is_mapping = isinstance(obj, dict)

        ret = {}
        for key, field in self.fields.items():
            try:
                value = obj[key] if is_mapping else getattr(obj, key)
            except (KeyError, AttributeError):
                continue
            ret[key] = field.serialize(value)
        return ret


class Definitions(MutableMapping):
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


class Reference(Field):
    errors = {"null": "May not be null."}

    def __init__(
        self,
        to: str,
        definitions: Definitions,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(**kwargs)
        self.to = to
        self.definitions = definitions

    @property
    def target(self) -> typing.Any:
        return self.definitions[self.to]

    def validate(self, value: typing.Any) -> typing.Any:
        if value is None and self.allow_null:
            return None
        elif value is None:
            raise self.validation_error("null")

        return self.target.validate(value)

    def serialize(self, obj: typing.Any) -> typing.Any:
        if obj is None:
            return None
        return dict(obj)
