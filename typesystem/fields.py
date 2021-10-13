import decimal
import re
import typing
from math import isfinite

from typesystem import formats
from typesystem.base import Message, ValidationError, ValidationResult
from typesystem.unique import Uniqueness

NO_DEFAULT = object()

FORMATS = {
    "date": formats.DateFormat(),
    "time": formats.TimeFormat(),
    "datetime": formats.DateTimeFormat(),
    "uuid": formats.UUIDFormat(),
    "email": formats.EmailFormat(),
    "ipaddress": formats.IPAddressFormat(),
    "url": formats.URLFormat(),
}


class Field:
    errors: typing.Dict[str, str] = {}

    def __init__(
        self,
        *,
        title: str = "",
        description: str = "",
        default: typing.Any = NO_DEFAULT,
        allow_null: bool = False,
        read_only: bool = False,
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
        self.read_only = read_only

    def validate(self, value: typing.Any) -> typing.Any:
        raise NotImplementedError()  # pragma: no cover

    def validate_or_error(self, value: typing.Any) -> ValidationResult:
        try:
            value = self.validate(value)
        except ValidationError as error:
            return ValidationResult(value=None, error=error)
        return ValidationResult(value=value, error=None)

    def serialize(self, obj: typing.Any) -> typing.Any:
        return obj

    def has_default(self) -> bool:
        return hasattr(self, "default")

    def get_default_value(self) -> typing.Any:
        default = getattr(self, "default", None)
        if callable(default):
            return default()
        return default

    def validation_error(self, code: str) -> ValidationError:
        text = self.get_error_text(code)
        return ValidationError(text=text, code=code)

    def get_error_text(self, code: str) -> str:
        return self.errors[code].format(**self.__dict__)

    def __or__(self, other: "Field") -> "Union":
        if isinstance(self, Union):
            any_of = self.any_of
        else:
            any_of = [self]

        if isinstance(other, Union):
            any_of += other.any_of
        else:
            any_of += [other]

        return Union(any_of=any_of)


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
        trim_whitespace: bool = True,
        max_length: int = None,
        min_length: int = None,
        pattern: typing.Union[str, typing.Pattern] = None,
        format: str = None,
        coerce_types: bool = True,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(**kwargs)

        assert max_length is None or isinstance(max_length, int)
        assert min_length is None or isinstance(min_length, int)
        assert pattern is None or isinstance(pattern, (str, typing.Pattern))
        assert format is None or isinstance(format, str)

        if allow_blank and not self.has_default():
            self.default = ""

        self.allow_blank = allow_blank
        self.trim_whitespace = trim_whitespace
        self.max_length = max_length
        self.min_length = min_length
        self.format = format
        self.coerce_types = coerce_types

        if pattern is None:
            self.pattern = None
            self.pattern_regex = None
        elif isinstance(pattern, str):
            self.pattern = pattern
            self.pattern_regex = re.compile(pattern)
        else:
            self.pattern = pattern.pattern
            self.pattern_regex = pattern

    def validate(self, value: typing.Any) -> typing.Any:
        if value is None and self.allow_null:
            return None
        elif value is None and self.allow_blank and self.coerce_types:
            # Leniently cast nulls to empty strings if allow_blank.
            return ""
        elif value is None:
            raise self.validation_error("null")
        elif self.format in FORMATS and FORMATS[self.format].is_native_type(value):
            return value
        elif not isinstance(value, str):
            raise self.validation_error("type")

        # The null character is always invalid.
        value = value.replace("\0", "")

        # Strip leading/trailing whitespace by default.
        if self.trim_whitespace:
            value = value.strip()

        if not self.allow_blank and not value:
            if self.allow_null and self.coerce_types:
                # Leniently cast empty strings (after trimming) to null if allow_null.
                return None
            raise self.validation_error("blank")

        if self.min_length is not None:
            if len(value) < self.min_length:
                raise self.validation_error("min_length")

        if self.max_length is not None:
            if len(value) > self.max_length:
                raise self.validation_error("max_length")

        if self.pattern_regex is not None:
            if not self.pattern_regex.search(value):
                raise self.validation_error("pattern")

        if self.format in FORMATS:
            return FORMATS[self.format].validate(value)

        return value

    def serialize(self, obj: typing.Any) -> typing.Any:
        if self.format in FORMATS:
            return FORMATS[self.format].serialize(obj)
        return obj


class Number(Field):
    numeric_type: typing.Optional[type] = None
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
        multiple_of: typing.Union[int, float, decimal.Decimal] = None,
        coerce_types: bool = True,
        **kwargs: typing.Any,
    ):
        super().__init__(**kwargs)

        assert minimum is None or isinstance(minimum, (int, float, decimal.Decimal))
        assert maximum is None or isinstance(maximum, (int, float, decimal.Decimal))
        assert exclusive_minimum is None or isinstance(
            exclusive_minimum, (int, float, decimal.Decimal)
        )
        assert exclusive_maximum is None or isinstance(
            exclusive_maximum, (int, float, decimal.Decimal)
        )
        assert multiple_of is None or isinstance(
            multiple_of, (int, float, decimal.Decimal)
        )

        self.minimum = minimum
        self.maximum = maximum
        self.exclusive_minimum = exclusive_minimum
        self.exclusive_maximum = exclusive_maximum
        self.multiple_of = multiple_of
        self.precision = precision
        self.coerce_types = coerce_types

    def validate(self, value: typing.Any) -> typing.Any:
        if value is None and self.allow_null:
            return None
        elif value == "" and self.allow_null and self.coerce_types:
            return None
        elif value is None:
            raise self.validation_error("null")
        elif isinstance(value, bool):
            raise self.validation_error("type")
        elif (
            self.numeric_type is int
            and isinstance(value, float)
            and not value.is_integer()
        ):
            raise self.validation_error("integer")
        elif not isinstance(value, (int, float)) and not self.coerce_types:
            raise self.validation_error("type")

        try:
            if isinstance(value, str):
                # Casting to a decimal first gives more lenient parsing.
                value = decimal.Decimal(value)
            if self.numeric_type is not None:
                value = self.numeric_type(value)
        except (TypeError, ValueError, decimal.InvalidOperation):
            raise self.validation_error("type")

        if not isfinite(value):
            # inf, -inf, nan, are all invalid.
            raise self.validation_error("finite")

        if self.precision is not None:
            numeric_type = self.numeric_type or type(value)
            quantize_val = decimal.Decimal(self.precision)
            decimal_val = decimal.Decimal(value)
            decimal_val = decimal_val.quantize(
                quantize_val, rounding=decimal.ROUND_HALF_UP
            )
            value = numeric_type(decimal_val)

        if self.minimum is not None and value < self.minimum:
            raise self.validation_error("minimum")

        if self.exclusive_minimum is not None and value <= self.exclusive_minimum:
            raise self.validation_error("exclusive_minimum")

        if self.maximum is not None and value > self.maximum:
            raise self.validation_error("maximum")

        if self.exclusive_maximum is not None and value >= self.exclusive_maximum:
            raise self.validation_error("exclusive_maximum")

        if self.multiple_of is not None:
            if isinstance(self.multiple_of, int):
                if value % self.multiple_of:
                    raise self.validation_error("multiple_of")
            else:
                if not (value * (1 / self.multiple_of)).is_integer():
                    raise self.validation_error("multiple_of")

        return value


class Integer(Number):
    numeric_type = int


class Float(Number):
    numeric_type = float


class Decimal(Number):
    numeric_type = decimal.Decimal

    def serialize(self, obj: typing.Any) -> typing.Any:
        return None if obj is None else float(obj)


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

    def __init__(self, *, coerce_types: bool = True, **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)
        self.coerce_types = coerce_types

    def validate(self, value: typing.Any) -> typing.Any:
        if value is None and self.allow_null:
            return None

        elif value is None:
            raise self.validation_error("null")

        elif not isinstance(value, bool):
            if not self.coerce_types:
                raise self.validation_error("type")

            if isinstance(value, str):
                value = value.lower()

            if self.allow_null and value in self.coerce_null_values:
                return None

            try:
                value = self.coerce_values[value]
            except (KeyError, TypeError):
                raise self.validation_error("type")

        return value


class Choice(Field):
    errors = {
        "null": "May not be null.",
        "required": "This field is required.",
        "choice": "Not a valid choice.",
    }

    def __init__(
        self,
        *,
        choices: typing.Sequence[typing.Union[str, typing.Tuple[str, str]]] = None,
        coerce_types: bool = True,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(**kwargs)
        self.choices = [
            (choice if isinstance(choice, (tuple, list)) else (choice, choice))
            for choice in choices or []
        ]
        self.coerce_types = coerce_types
        assert all(len(choice) == 2 for choice in self.choices)

    def validate(self, value: typing.Any) -> typing.Any:
        if value is None and self.allow_null:
            return None
        elif value is None:
            raise self.validation_error("null")
        elif value not in Uniqueness([key for key, value in self.choices]):
            if value == "":
                if self.allow_null and self.coerce_types:
                    return None
                raise self.validation_error("required")
            raise self.validation_error("choice")
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
        property_names: Field = None,
        min_properties: int = None,
        max_properties: int = None,
        required: typing.Sequence[str] = None,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(**kwargs)

        if isinstance(properties, Field):
            additional_properties = properties
            properties = None

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
        self.property_names = property_names
        self.min_properties = min_properties
        self.max_properties = max_properties
        self.required = required

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
            elif self.property_names is not None:
                _, error = self.property_names.validate_or_error(key)
                if error is not None:
                    text = self.get_error_text("invalid_property")
                    message = Message(text=text, code="invalid_property", index=[key])
                    error_messages.append(message)

        # Min/Max properties
        if self.min_properties is not None:
            if len(value) < self.min_properties:
                if self.min_properties == 1:
                    raise self.validation_error("empty")
                else:
                    raise self.validation_error("min_properties")
        if self.max_properties is not None:
            if len(value) > self.max_properties:
                raise self.validation_error("max_properties")

        # Required properties
        for key in self.required:
            if key not in value:
                text = self.get_error_text("required")
                message = Message(text=text, code="required", index=[key])
                error_messages.append(message)

        # Properties
        for key, child_schema in self.properties.items():
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

        # Pattern properties
        if self.pattern_properties:
            for key in list(value.keys()):
                for pattern, child_schema in self.pattern_properties.items():
                    if isinstance(key, str) and re.search(pattern, key):
                        item = value[key]
                        child_value, error = child_schema.validate_or_error(item)
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
                text = self.get_error_text("invalid_property")
                message = Message(text=text, code="invalid_property", key=key)
                error_messages.append(message)
        elif self.additional_properties is not None:
            assert isinstance(self.additional_properties, Field)
            child_schema = self.additional_properties
            for key in remaining:
                item = value[key]
                child_value, error = child_schema.validate_or_error(item)
                if not error:
                    validated[key] = child_value
                else:
                    error_messages += error.messages(add_prefix=key)

        if error_messages:
            raise ValidationError(messages=error_messages)

        return validated


class Array(Field):
    errors = {
        "type": "Must be an array.",
        "null": "May not be null.",
        "empty": "Must not be empty.",
        "exact_items": "Must have {min_items} items.",
        "min_items": "Must have at least {min_items} items.",
        "max_items": "Must have no more than {max_items} items.",
        "additional_items": "May not contain additional items.",
        "unique_items": "Items must be unique.",
    }

    def __init__(
        self,
        items: typing.Union[Field, typing.Sequence[Field]] = None,
        additional_items: typing.Union[Field, bool] = False,
        min_items: int = None,
        max_items: int = None,
        exact_items: int = None,
        unique_items: bool = False,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(**kwargs)

        items = list(items) if isinstance(items, (list, tuple)) else items

        assert (
            items is None
            or isinstance(items, Field)
            or (isinstance(items, list) and all(isinstance(i, Field) for i in items))
        )
        assert isinstance(additional_items, bool) or isinstance(additional_items, Field)
        assert min_items is None or isinstance(min_items, int)
        assert max_items is None or isinstance(max_items, int)
        assert isinstance(unique_items, bool)

        if isinstance(items, list):
            if min_items is None:
                min_items = len(items)
            if max_items is None and (additional_items is False):
                max_items = len(items)

        if exact_items is not None:
            min_items = exact_items
            max_items = exact_items

        self.items = items
        self.additional_items = additional_items
        self.min_items = min_items
        self.max_items = max_items
        self.unique_items = unique_items

    def validate(self, value: typing.Any) -> typing.Any:
        if value is None and self.allow_null:
            return None
        elif value is None:
            raise self.validation_error("null")
        elif not isinstance(value, list):
            raise self.validation_error("type")

        if (
            self.min_items is not None
            and self.min_items == self.max_items
            and len(value) != self.min_items
        ):
            raise self.validation_error("exact_items")
        if self.min_items is not None and len(value) < self.min_items:
            if self.min_items == 1:
                raise self.validation_error("empty")
            raise self.validation_error("min_items")
        elif self.max_items is not None and len(value) > self.max_items:
            raise self.validation_error("max_items")

        # Ensure all items are of the right type.
        validated = []
        error_messages: typing.List[Message] = []
        if self.unique_items:
            seen_items = Uniqueness()

        for pos, item in enumerate(value):
            validator = None
            if isinstance(self.items, list):
                if pos < len(self.items):
                    validator = self.items[pos]
                elif isinstance(self.additional_items, Field):
                    validator = self.additional_items
            elif self.items is not None:
                validator = self.items

            if validator is None:
                validated.append(item)
            else:
                item, error = validator.validate_or_error(item)
                if error:
                    error_messages += error.messages(add_prefix=pos)
                else:
                    validated.append(item)

            if self.unique_items:
                if item in seen_items:
                    text = self.get_error_text("unique_items")
                    message = Message(text=text, code="unique_items", key=pos)
                    error_messages.append(message)
                else:
                    seen_items.add(item)

        if error_messages:
            raise ValidationError(messages=error_messages)

        return validated

    def serialize(self, obj: typing.Any) -> typing.Any:
        if obj is None:
            return None

        if isinstance(self.items, list):
            return [
                serializer.serialize(value)
                for serializer, value in zip(self.items, obj)
            ]

        if self.items is None:
            return obj

        return [self.items.serialize(value) for value in obj]


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


class Union(Field):
    errors = {"null": "May not be null.", "union": "Did not match any valid type."}

    def __init__(self, any_of: typing.List[Field], **kwargs: typing.Any):
        super().__init__(**kwargs)

        self.any_of = any_of
        if any([child.allow_null for child in any_of]):
            self.allow_null = True

    def validate(self, value: typing.Any) -> typing.Any:
        if value is None and self.allow_null:
            return None
        elif value is None:
            raise self.validation_error("null")

        candidate_errors = []
        for child in self.any_of:
            validated, error = child.validate_or_error(value)
            if error is None:
                return validated
            else:
                # If a child returned anything other than a type error, then
                # it is a candidate for returning as the primary error.
                messages = error.messages()
                if (
                    len(messages) != 1
                    or messages[0].code != "type"
                    or messages[0].index
                ):
                    candidate_errors.append(error)

        if len(candidate_errors) == 1:
            # If exactly one child was of the correct type, then we can use
            # the error from the child.
            raise candidate_errors[0]
        raise self.validation_error("union")


class Any(Field):
    """
    Always matches.
    """

    def validate(self, value: typing.Any) -> typing.Any:
        return value


class Const(Field):
    """
    Only ever matches the given given value.
    """

    errors = {"only_null": "Must be null.", "const": "Must be the value '{const}'."}

    def __init__(self, const: typing.Any, **kwargs: typing.Any):
        assert "allow_null" not in kwargs
        super().__init__(**kwargs)
        self.const = const

    def validate(self, value: typing.Any) -> typing.Any:
        if value != self.const:
            if self.const is None:
                raise self.validation_error("only_null")
            raise self.validation_error("const")
        return value


class UUID(String):
    def __init__(self, **kwargs: typing.Any) -> None:
        super().__init__(format="uuid", **kwargs)


class Email(String):
    def __init__(self, **kwargs: typing.Any) -> None:
        super().__init__(format="email", **kwargs)


class Password(String):
    def __init__(self, **kwargs: typing.Any) -> None:
        super().__init__(format="password", **kwargs)


class IPAddress(String):
    def __init__(self, **kwargs: typing.Any) -> None:
        super().__init__(format="ipaddress", **kwargs)


class URL(String):
    def __init__(self, **kwargs: typing.Any) -> None:
        super().__init__(format="url", **kwargs)
