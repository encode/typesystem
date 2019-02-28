import decimal
import re
import typing
from math import isfinite

from typesystem import formats
from typesystem.base import ErrorMessage, ValidationError, ValidationResult

NO_DEFAULT = object()

FORMATS = {
    "date": formats.DateFormat(),
    "time": formats.TimeFormat(),
    "datetime": formats.DateTimeFormat(),
}


class Field:
    errors = {}  # type: typing.Dict[str, str]
    _creation_counter = 0

    def __init__(
        self,
        *,
        title: str = "",
        description: str = "",
        default: typing.Any = NO_DEFAULT,
        allow_null: bool = False,
    ):
        assert isinstance(title, str)
        assert isinstance(description, str)

        if allow_null and default is NO_DEFAULT:
            default = None

        if default is not NO_DEFAULT:
            self.default = default

        self.title = title
        self.description = description
        self.allow_null = allow_null

        # We need this global counter to determine what order fields have
        # been declared in when used with `Schema`.
        self._creation_counter = Field._creation_counter
        Field._creation_counter += 1

    def validate(self, value: typing.Any, *, strict: bool = False) -> ValidationResult:
        result = self.validate_value(value, strict=strict)

        if isinstance(result, ValidationError):
            return ValidationResult(value=None, error=result)
        return ValidationResult(value=result, error=None)

    def validate_value(
        self, value: typing.Any, *, strict: bool = False
    ) -> typing.Union[typing.Any, ValidationError]:
        raise NotImplementedError()  # pragma: no cover

    def serialize(self, obj: typing.Any) -> typing.Any:
        return obj

    def has_default(self) -> bool:
        return hasattr(self, "default")

    def error(self, code: str) -> ValidationError:
        text = self.errors[code].format(**self.__dict__)
        return ValidationError(text=text, code=code)

    def error_message(self, code: str, *, index: list = None) -> ErrorMessage:
        text = self.errors[code].format(**self.__dict__)
        return ErrorMessage(text=text, code=code, index=index)


class String(Field):
    errors = {
        "type": "Must be a string.",
        "null": "May not be null.",
        "blank": "Must not be blank.",
        "max_length": "Must have no more than {max_length} characters.",
        "min_length": "Must have at least {min_length} characters.",
        "pattern": "Must match the pattern /{pattern}/.",
        "format": "Must be a valid {format}.",
    }

    def __init__(
        self,
        *,
        allow_blank: bool = False,
        max_length: int = None,
        min_length: int = None,
        pattern: str = None,
        format: str = None,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(**kwargs)

        assert max_length is None or isinstance(max_length, int)
        assert min_length is None or isinstance(min_length, int)
        assert pattern is None or isinstance(pattern, str)
        assert format is None or isinstance(format, str)

        self.allow_blank = allow_blank
        self.max_length = max_length
        self.min_length = min_length
        self.pattern = pattern
        self.format = format

    def validate_value(
        self, value: typing.Any, *, strict: bool = False
    ) -> typing.Union[typing.Any, ValidationError]:
        if value is None and self.allow_null:
            return None
        elif value is None:
            return self.error("null")
        elif self.format in FORMATS and FORMATS[self.format].is_native_type(value):
            return value
        elif not isinstance(value, str):
            return self.error("type")

        if not self.allow_blank and not value:
            return self.error("blank")

        if self.min_length is not None:
            if len(value) < self.min_length:
                return self.error("min_length")

        if self.max_length is not None:
            if len(value) > self.max_length:
                return self.error("max_length")

        if self.pattern is not None:
            if not re.search(self.pattern, value):
                return self.error("pattern")

        if self.format in FORMATS:
            return FORMATS[self.format].validate(value)

        return value

    def serialize(self, obj: typing.Any) -> typing.Any:
        if self.format in FORMATS:
            return FORMATS[self.format].serialize(obj)
        return obj


class NumericType(Field):
    """
    Base class for both `Number` and `Integer`.
    """

    numeric_type = None  # type: type
    errors = {
        "type": "Must be a number.",
        "null": "May not be null.",
        "integer": "Must be an integer.",
        "finite": "Must be finite.",
        "minimum": "Must be greater than or equal to {minimum}.",
        "exclusive_minimum": "Must be greater than {exclusive_minimum}.",
        "maximum": "Must be less than or equal to {maximum}.",
        "exclusive_maximum": "Must be less than {exclusive_maximum}.",
        "multiple_of": "Must be a multiple of {multiple_of}.",
    }

    def __init__(
        self,
        *,
        minimum: typing.Union[int, float, decimal.Decimal] = None,
        maximum: typing.Union[int, float, decimal.Decimal] = None,
        exclusive_minimum: typing.Union[int, float, decimal.Decimal] = None,
        exclusive_maximum: typing.Union[int, float, decimal.Decimal] = None,
        precision: str = None,
        multiple_of: int = None,
        **kwargs: typing.Any,
    ):
        super().__init__(**kwargs)

        assert minimum is None or isinstance(minimum, self.numeric_type)
        assert maximum is None or isinstance(maximum, self.numeric_type)
        assert exclusive_minimum is None or isinstance(
            exclusive_minimum, self.numeric_type
        )
        assert exclusive_maximum is None or isinstance(
            exclusive_maximum, self.numeric_type
        )
        assert multiple_of is None or isinstance(multiple_of, int)

        self.minimum = minimum
        self.maximum = maximum
        self.exclusive_minimum = exclusive_minimum
        self.exclusive_maximum = exclusive_maximum
        self.multiple_of = multiple_of
        self.precision = precision

    def validate_value(
        self, value: typing.Any, *, strict: bool = False
    ) -> typing.Union[typing.Any, ValidationError]:
        if value is None and self.allow_null:
            return None
        elif value is None:
            return self.error("null")
        elif isinstance(value, bool):
            return self.error("type")
        elif (
            self.numeric_type is int
            and isinstance(value, float)
            and not value.is_integer()
        ):
            return self.error("integer")
        elif not isinstance(value, (int, float)) and strict:
            return self.error("type")
        elif isinstance(value, float) and not isfinite(value):
            return self.error("finite")

        try:
            value = self.numeric_type(value)
        except (TypeError, ValueError):
            return self.error("type")

        if self.precision is not None:
            quantize_val = decimal.Decimal(self.precision)
            decimal_val = decimal.Decimal(value)
            decimal_val = decimal_val.quantize(
                quantize_val, rounding=decimal.ROUND_HALF_UP
            )
            value = self.numeric_type(decimal_val)

        if self.minimum is not None and value < self.minimum:
            return self.error("minimum")

        if self.exclusive_minimum is not None and value <= self.exclusive_minimum:
            return self.error("exclusive_minimum")

        if self.maximum is not None and value > self.maximum:
            return self.error("maximum")

        if self.exclusive_maximum is not None and value >= self.exclusive_maximum:
            return self.error("exclusive_maximum")

        if self.multiple_of is not None:
            if value % self.multiple_of:
                return self.error("multiple_of")

        return value


class Integer(NumericType):
    numeric_type = int


class Float(NumericType):
    numeric_type = float


class Decimal(NumericType):
    numeric_type = decimal.Decimal

    def serialize(self, obj: typing.Any) -> typing.Any:
        return float(obj)


class Boolean(Field):
    errors = {"type": "Must be a boolean.", "null": "May not be null."}
    coerce_values = {
        "true": True,
        "false": False,
        "on": True,
        "off": False,
        "1": True,
        "0": False,
        "": False,
        1: True,
        0: False,
    }
    coerce_null_values = {"", "null", "none"}

    def validate_value(
        self, value: typing.Any, *, strict: bool = False
    ) -> typing.Union[typing.Any, ValidationError]:
        if value is None and self.allow_null:
            return None

        elif value is None:
            return self.error("null")

        elif not isinstance(value, bool):
            if strict:
                return self.error("type")

            if isinstance(value, str):
                value = value.lower()

            if self.allow_null and value in self.coerce_null_values:
                return None

            try:
                value = self.coerce_values[value]
            except KeyError:
                return self.error("type")

        return value


class Choice(Field):
    errors = {"null": "May not be null.", "choice": "Not a valid choice."}

    def __init__(
        self, *, choices: typing.Union[dict, typing.Sequence], **kwargs: typing.Any
    ) -> None:
        super().__init__(**kwargs)
        if isinstance(choices, dict):
            #  Instantiated with a dictionary.
            self.choice_items = list(choices.items())
        elif all([isinstance(choice, str) for choice in choices]):
            # Instantiated with a list of strings.
            self.choice_items = [(choice, choice) for choice in choices]
        else:
            # Instantiated with a list of two-tuples.
            assert all([len(item) == 2 for item in choices])
            self.choice_items = list(choices)
        self.choice_dict = dict(self.choice_items)

    def validate_value(
        self, value: typing.Any, *, strict: bool = False
    ) -> typing.Union[typing.Any, ValidationError]:
        if value is None and self.allow_null:
            return None
        elif value is None:
            return self.error("null")
        elif value not in self.choice_dict:
            return self.error("choice")
        return value


class Object(Field):
    errors = {
        "type": "Must be an object.",
        "null": "May not be null.",
        "invalid_key": "All object keys must be strings.",
        "required": "This field is required.",
        "invalid_property": "Invalid property name.",
        "empty": "Must not be empty.",
        "max_properties": "Must have no more than {max_properties} properties.",
        "min_properties": "Must have at least {min_properties} properties.",
    }

    def __init__(
        self,
        *,
        properties: typing.Dict[str, Field] = None,
        pattern_properties: typing.Dict[str, Field] = None,
        additional_properties: typing.Union[bool, None, Field] = True,
        min_properties: int = None,
        max_properties: int = None,
        required: typing.Sequence[str] = None,
        coerce: type = None,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(**kwargs)

        properties = {} if (properties is None) else dict(properties)
        pattern_properties = (
            {} if (pattern_properties is None) else dict(pattern_properties)
        )
        required = list(required) if isinstance(required, (list, tuple)) else required
        required = [] if (required is None) else required

        assert all(isinstance(k, str) for k in properties.keys())
        assert all(isinstance(v, Field) for v in properties.values())
        assert all(isinstance(k, str) for k in pattern_properties.keys())
        assert all(isinstance(v, Field) for v in pattern_properties.values())
        assert additional_properties in (None, True, False) or isinstance(
            additional_properties, Field
        )
        assert min_properties is None or isinstance(min_properties, int)
        assert max_properties is None or isinstance(max_properties, int)
        assert all(isinstance(i, str) for i in required)

        self.properties = properties
        self.pattern_properties = pattern_properties
        self.additional_properties = additional_properties
        self.min_properties = min_properties
        self.max_properties = max_properties
        self.required = required
        self.coerce = coerce

    def validate_value(
        self, value: typing.Any, *, strict: bool = False
    ) -> typing.Union[typing.Any, ValidationError]:
        if value is None and self.allow_null:
            return None
        elif value is None:
            return self.error("null")
        elif not isinstance(value, (dict, typing.Mapping)):
            return self.error("type")

        validated = {}
        error_messages = []

        # Ensure all property keys are strings.
        for key in value.keys():
            if not isinstance(key, str):
                return self.error("invalid_key")

        # Min/Max properties
        if self.min_properties is not None:
            if len(value) < self.min_properties:
                if self.min_properties == 1:
                    return self.error("empty")
                else:
                    return self.error("min_properties")
        if self.max_properties is not None:
            if len(value) > self.max_properties:
                return self.error("max_properties")

        # Required properties
        for key in self.required:
            if key not in value:
                message = self.error_message("required", index=[key])
                error_messages.append(message)

        # Properties
        for key, child_schema in self.properties.items():
            if key not in value:
                if child_schema.has_default():
                    validated[key] = child_schema.default
                continue
            item = value[key]
            child_value, error = child_schema.validate(item, strict=strict)
            if not error:
                validated[key] = child_value
            else:
                error_messages += error.messages(add_prefix=key)

        # Pattern properties
        if self.pattern_properties:
            for key in list(value.keys()):
                for pattern, child_schema in self.pattern_properties.items():
                    if isinstance(key, str) and re.search(pattern, key):
                        item = value[key]
                        child_value, error = child_schema.validate(item, strict=strict)
                        if not error:
                            validated[key] = child_value
                        else:
                            error_messages += error.messages(add_prefix=key)

        # Additional properties
        validated_keys = set(validated.keys())
        error_keys = set(
            [message.index[0] for message in error_messages if message.index]
        )

        remaining = [
            key for key in value.keys() if key not in validated_keys | error_keys
        ]

        if self.additional_properties is True:
            for key in remaining:
                validated[key] = value[key]
        elif self.additional_properties is False:
            for key in remaining:
                message = self.error_message("invalid_property", index=[key])
                error_messages.append(message)
        elif self.additional_properties is not None:
            assert isinstance(self.additional_properties, Field)
            child_schema = self.additional_properties
            for key in remaining:
                item = value[key]
                child_value, error = child_schema.validate(item, strict=strict)
                if not error:
                    validated[key] = child_value
                else:
                    error_messages += error.messages(add_prefix=key)

        if error_messages:
            return ValidationError(messages=error_messages)

        if self.coerce is not None:
            return self.coerce(validated)

        return validated


# class Array(Field):
#     errors = {
#         'type': 'Must be an array.',
#         'null': 'May not be null.',
#         'empty': 'Must not be empty.',
#         'exact_items': 'Must have {min_items} items.',
#         'min_items': 'Must have at least {min_items} items.',
#         'max_items': 'Must have no more than {max_items} items.',
#         'additional_items': 'May not contain additional items.',
#         'unique_items': 'This item is not unique.',
#     }
#
#     def __init__(self, items=None, additional_items=None, min_items=None,
#                  max_items=None, unique_items=False, **kwargs):
#         super().__init__(**kwargs)
#
#         items = list(items) if isinstance(items, (list, tuple)) else items
#
#         assert items is None or hasattr(items, 'validate') or (
#             isinstance(items, list) and
#             all(hasattr(i, 'validate') for i in items)
#         )
#         assert additional_items in (None, True, False) or hasattr(additional_items, 'validate')
#         assert min_items is None or isinstance(min_items, int)
#         assert max_items is None or isinstance(max_items, int)
#         assert isinstance(unique_items, bool)
#
#         self.items = items
#         self.additional_items = additional_items
#         self.min_items = min_items
#         self.max_items = max_items
#         self.unique_items = unique_items
#
#     def validate(self, value, definitions=None, allow_coerce=False):
#         if value is None and self.allow_null:
#             return None
#         elif value is None:
#             self.error('null')
#         elif not isinstance(value, list):
#             self.error('type')
#
#         definitions = self.get_definitions(definitions)
#         validated = []
#
#         if self.min_items is not None and self.min_items == self.max_items and len(value) != self.min_items:
#             self.error('exact_items')
#         if self.min_items is not None and len(value) < self.min_items:
#             if self.min_items == 1:
#                 self.error('empty')
#             self.error('min_items')
#         elif self.max_items is not None and len(value) > self.max_items:
#             self.error('max_items')
#         elif isinstance(self.items, list) and (self.additional_items is False) and len(value) > len(self.items):
#             self.error('additional_items')
#
#         # Ensure all items are of the right type.
#         errors = {}
#         if self.unique_items:
#             seen_items = Uniqueness()
#
#         for pos, item in enumerate(value):
#             try:
#                 if isinstance(self.items, list):
#                     if pos < len(self.items):
#                         item = self.items[pos].validate(
#                             item,
#                             definitions=definitions,
#                             allow_coerce=allow_coerce
#                         )
#                     elif isinstance(self.additional_items, Validator):
#                         item = self.additional_items.validate(
#                             item,
#                             definitions=definitions,
#                             allow_coerce=allow_coerce
#                         )
#                 elif self.items is not None:
#                     item = self.items.validate(
#                         item,
#                         definitions=definitions,
#                         allow_coerce=allow_coerce
#                     )
#
#                 if self.unique_items:
#                     if item in seen_items:
#                         self.error('unique_items')
#                     else:
#                         seen_items.add(item)
#
#                 validated.append(item)
#             except ValidationError as exc:
#                 errors[pos] = exc.messages
#
#         if errors:
#             error_messages = []
#             for key, messages in errors.items():
#                 for message in messages:
#                     index = [key] if message.index is None else [key] + message.index
#                     error_message = ErrorMessage(message.text, message.code, index)
#                     error_messages.append(error_message)
#             raise ValidationError(error_messages)
#
#         return validated


class Text(String):
    def __init__(self, **kwargs: typing.Any) -> None:
        super().__init__(format="text", **kwargs)


class Date(String):
    def __init__(self, **kwargs: typing.Any) -> None:
        super().__init__(format="date", **kwargs)


class Time(String):
    def __init__(self, **kwargs: typing.Any) -> None:
        super().__init__(format="time", **kwargs)


class DateTime(String):
    def __init__(self, **kwargs: typing.Any) -> None:
        super().__init__(format="datetime", **kwargs)
