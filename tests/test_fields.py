import datetime

from typesystem.base import ErrorMessage, ValidationError
from typesystem.fields import (
    Boolean,
    Choice,
    Date,
    DateTime,
    Float,
    Integer,
    Object,
    String,
    Time,
)


def test_string():
    validator = String()
    validated = validator.validate("abc")
    assert validated
    assert validated.is_valid
    assert validated.value == "abc"
    assert validated.error is None

    validator = String()
    value, error = validator.validate("")
    assert error == ValidationError(text="Must not be blank.", code="blank")

    validator = String()
    value, error = validator.validate(None)
    assert error == ValidationError(text="May not be null.", code="null")

    validator = String()
    value, error = validator.validate(123)
    assert error == ValidationError(text="Must be a string.", code="type")

    validator = String(max_length=10)
    value, error = validator.validate("abc" * 10)
    assert error == ValidationError(
        text="Must have no more than 10 characters.", code="max_length"
    )

    validator = String(min_length=3)
    value, error = validator.validate("a")
    assert error == ValidationError(
        text="Must have at least 3 characters.", code="min_length"
    )

    validator = String(allow_blank=False)
    value, error = validator.validate("")
    assert error == ValidationError(text="Must not be blank.", code="blank")

    validator = String(allow_null=True)
    value, error = validator.validate(None)
    assert value is None
    assert error is None

    validator = String(pattern="^[abc]*$")
    value, error = validator.validate("cba")
    assert value == "cba"

    validator = String(pattern="^[abc]*$")
    value, error = validator.validate("cbxa")
    assert error == ValidationError(
        text="Must match the pattern /^[abc]*$/.", code="pattern"
    )


def test_integer():
    validator = Integer()
    value, error = validator.validate(123)
    assert value == 123

    validator = Integer()
    value, error = validator.validate("123")
    assert value == 123

    validator = Integer()
    value, error = validator.validate(123.0)
    assert value == 123

    validator = Integer()
    value, error = validator.validate(None)
    assert error == ValidationError(text="May not be null.", code="null")

    validator = Integer()
    value, error = validator.validate("abc")
    assert error == ValidationError(text="Must be a number.", code="type")

    validator = Integer()
    value, error = validator.validate(True)
    assert error == ValidationError(text="Must be a number.", code="type")

    validator = Integer()
    value, error = validator.validate(123.1)
    assert error == ValidationError(text="Must be an integer.", code="integer")

    validator = Integer()
    value, error = validator.validate(float("inf"))
    assert error == ValidationError(text="Must be an integer.", code="integer")

    validator = Integer()
    value, error = validator.validate(float("nan"))
    assert error == ValidationError(text="Must be an integer.", code="integer")

    validator = Integer()
    value, error = validator.validate("123", strict=True)
    assert error == ValidationError(text="Must be a number.", code="type")

    validator = Integer(allow_null=True)
    value, error = validator.validate(None)
    assert value is None
    assert error is None

    validator = Integer(maximum=10)
    value, error = validator.validate(100)
    assert error == ValidationError(
        text="Must be less than or equal to 10.", code="maximum"
    )

    validator = Integer(maximum=10)
    value, error = validator.validate(10)
    assert value == 10

    validator = Integer(minimum=3)
    value, error = validator.validate(1)
    assert error == ValidationError(
        text="Must be greater than or equal to 3.", code="minimum"
    )

    validator = Integer(minimum=3)
    value, error = validator.validate(3)
    assert value == 3

    validator = Integer(exclusive_maximum=10)
    value, error = validator.validate(10)
    assert error == ValidationError(
        text="Must be less than 10.", code="exclusive_maximum"
    )

    validator = Integer(exclusive_minimum=3)
    value, error = validator.validate(3)
    assert error == ValidationError(
        text="Must be greater than 3.", code="exclusive_minimum"
    )

    validator = Integer(multiple_of=10)
    value, error = validator.validate(5)
    assert error == ValidationError(
        text="Must be a multiple of 10.", code="multiple_of"
    )


def test_float():
    validator = Float()
    value, error = validator.validate(123.1)
    assert value == 123.1

    validator = Float()
    value, error = validator.validate(123)
    assert value == 123.0

    validator = Float()
    value, error = validator.validate("123.1")
    assert value == 123.1

    validator = Float()
    value, error = validator.validate(None)
    assert error == ValidationError(text="May not be null.", code="null")

    validator = Float()
    value, error = validator.validate("abc")
    assert error == ValidationError(text="Must be a number.", code="type")

    validator = Float()
    value, error = validator.validate(True)
    assert error == ValidationError(text="Must be a number.", code="type")

    validator = Float()
    value, error = validator.validate(float("inf"))
    assert error == ValidationError(text="Must be finite.", code="finite")

    validator = Float()
    value, error = validator.validate(float("nan"))
    assert error == ValidationError(text="Must be finite.", code="finite")

    validator = Float()
    value, error = validator.validate("123", strict=True)
    assert error == ValidationError(text="Must be a number.", code="type")

    validator = Float(allow_null=True)
    value, error = validator.validate(None)
    assert value is None
    assert error is None

    validator = Float(maximum=10.0)
    value, error = validator.validate(100.0)
    assert error == ValidationError(
        text="Must be less than or equal to 10.0.", code="maximum"
    )

    validator = Float(maximum=10.0)
    value, error = validator.validate(10.0)
    assert value == 10.0

    validator = Float(minimum=3.0)
    value, error = validator.validate(1.0)
    assert error == ValidationError(
        text="Must be greater than or equal to 3.0.", code="minimum"
    )

    validator = Float(minimum=3.0)
    value, error = validator.validate(3.0)
    assert value == 3.0

    validator = Float(exclusive_maximum=10.0)
    value, error = validator.validate(10.0)
    assert error == ValidationError(
        text="Must be less than 10.0.", code="exclusive_maximum"
    )

    validator = Float(exclusive_minimum=3.0)
    value, error = validator.validate(3.0)
    assert error == ValidationError(
        text="Must be greater than 3.0.", code="exclusive_minimum"
    )

    validator = Float(precision="0.01")
    value, error = validator.validate("123.456")
    assert value == 123.46


def test_boolean():
    validator = Boolean()
    value, error = validator.validate(True)
    assert value is True

    validator = Boolean()
    value, error = validator.validate(False)
    assert value is False

    validator = Boolean()
    value, error = validator.validate("True")
    assert value is True

    validator = Boolean()
    value, error = validator.validate(1)
    assert value is True

    validator = Boolean()
    value, error = validator.validate(None)
    assert error == ValidationError(text="May not be null.", code="null")

    validator = Boolean()
    value, error = validator.validate(2)
    assert error == ValidationError(text="Must be a boolean.", code="type")

    validator = Boolean(allow_null=True)
    value, error = validator.validate(None)
    assert value is None
    assert error is None

    validator = Boolean(allow_null=True)
    value, error = validator.validate("")
    assert value is None
    assert error is None

    validator = Boolean()
    value, error = validator.validate("True", strict=True)
    assert error == ValidationError(text="Must be a boolean.", code="type")


def test_choice():
    validator = Choice(choices=["red", "blue", "green"])
    value, error = validator.validate("red")
    assert value == "red"

    validator = Choice(choices=["red", "blue", "green"])
    value, error = validator.validate("foo")
    assert error == ValidationError(text="Not a valid choice.", code="choice")

    validator = Choice(choices=["red", "blue", "green"])
    validated = validator.validate(None)
    assert validated.errors == ValidationError(text="May not be null.", code="null")

    validator = Choice(choices=["red", "blue", "green"], allow_null=True)
    value, error = validator.validate(None)
    assert value is None
    assert error is None

    validator = Choice(choices={"R": "red", "B": "blue", "G": "green"})
    value, error = validator.validate("Z")
    assert error == ValidationError(text="Not a valid choice.", code="choice")

    validator = Choice(choices={"R": "red", "B": "blue", "G": "green"})
    value, error = validator.validate("R")
    assert value == "R"

    validator = Choice(choices=[("R", "red"), ("B", "blue"), ("G", "green")])
    value, error = validator.validate("Z")
    assert error == ValidationError(text="Not a valid choice.", code="choice")

    validator = Choice(choices=[("R", "red"), ("B", "blue"), ("G", "green")])
    value, error = validator.validate("R")
    assert value == "R"


def test_object():
    validator = Object()
    value, error = validator.validate({})
    assert value == {}

    validator = Object()
    value, error = validator.validate(None)
    assert dict(error) == {"": "May not be null."}

    validator = Object()
    value, error = validator.validate(123)
    assert dict(error) == {"": "Must be an object."}

    validator = Object()
    value, error = validator.validate({1: 123})
    assert dict(error) == {"": "All object keys must be strings."}

    validator = Object(allow_null=True)
    value, error = validator.validate(None)
    assert value is None
    assert error is None

    validator = Object(min_properties=1)
    value, error = validator.validate({})
    assert dict(error) == {"": "Must not be empty."}

    validator = Object(min_properties=1)
    value, error = validator.validate({"a": 1})
    assert value == {"a": 1}

    validator = Object(min_properties=2)
    value, error = validator.validate({})
    assert dict(error) == {"": "Must have at least 2 properties."}

    validator = Object(min_properties=2)
    value, error = validator.validate({"a": 1, "b": 2})
    assert value == {"a": 1, "b": 2}

    validator = Object(max_properties=2)
    value, error = validator.validate({})
    assert value == {}

    validator = Object(max_properties=2)
    value, error = validator.validate({"a": 1, "b": 2, "c": 3})
    assert dict(error) == {"": "Must have no more than 2 properties."}

    validator = Object(required=["example"])
    value, error = validator.validate({"example": 123})
    assert value == {"example": 123}

    validator = Object(required=["example"])
    value, error = validator.validate({})
    assert dict(error) == {"example": "This field is required."}

    validator = Object(properties={"example": Integer()})
    value, error = validator.validate({"example": "123"})
    assert value == {"example": 123}

    validator = Object(properties={"example": Integer()})
    value, error = validator.validate({"example": "abc"})
    assert dict(error) == {"example": "Must be a number."}

    validator = Object(pattern_properties={"^x-.*$": Integer()})
    value, error = validator.validate({"x-example": "123"})
    assert value == {"x-example": 123}

    validator = Object(pattern_properties={"^x-.*$": Integer()})
    value, error = validator.validate({"x-example": "abc"})
    assert dict(error) == {"x-example": "Must be a number."}

    validator = Object(properties={"example": Integer(default=0)})
    value, error = validator.validate({"example": "123"})
    assert value == {"example": 123}

    validator = Object(properties={"example": Integer(default=0)})
    value, error = validator.validate({})
    assert value == {"example": 0}

    validator = Object(additional_properties=False)
    value, error = validator.validate({"example": "123"})
    assert dict(error) == {"example": "Invalid property name."}

    validator = Object(additional_properties=True)
    value, error = validator.validate({"example": "abc"})
    assert value == {"example": "abc"}

    validator = Object(additional_properties=None)
    value, error = validator.validate({"example": "abc"})
    assert value == {}

    validator = Object(additional_properties=Integer())
    value, error = validator.validate({"example": "123"})
    assert value == {"example": 123}

    validator = Object(additional_properties=Integer())
    value, error = validator.validate({"example": "abc"})
    assert dict(error) == {"example": "Must be a number."}

    validator = Object(properties={"example": Integer()})
    value, error = validator.validate({"example": "123"})
    assert value == {"example": 123}

    validator = Object(properties={"example": Integer()})
    value, error = validator.validate({"example": "abc"})
    assert dict(error) == {"example": "Must be a number."}

    validator = Object(additional_properties=Object(additional_properties=Integer()))
    value, error = validator.validate({"example": {"nested": "123"}})
    assert value == {"example": {"nested": 123}}

    validator = Object(additional_properties=Object(additional_properties=Integer()))
    value, error = validator.validate({"example": {"nested": "abc"}})
    assert dict(error) == {"example": {"nested": "Must be a number."}}


def test_date():
    validator = Date()
    value, error = validator.validate("2049-01-01")
    assert value == datetime.date(2049, 1, 1)

    validator = Date()
    value, error = validator.validate(datetime.date(2049, 1, 1))
    assert value == datetime.date(2049, 1, 1)

    validator = Date()
    value, error = validator.validate("20490101")
    assert error == ValidationError(text="Must be a valid date format.", code="format")

    validator = Date()
    value, error = validator.validate("2049-01-32")
    assert error == ValidationError(text="Must be a real date.", code="invalid")


def test_time():
    validator = Time()
    value, error = validator.validate("12:00:01")
    assert value == datetime.time(12, 0, 1)

    validator = Time()
    value, error = validator.validate("12:00:01.001")
    assert value == datetime.time(12, 0, 1, 1000)

    validator = Time()
    value, error = validator.validate("12:00:01.000001")
    assert value == datetime.time(12, 0, 1, 1)

    validator = Time()
    value, error = validator.validate(datetime.time(12, 0, 1))
    assert value == datetime.time(12, 0, 1)

    validator = Time()
    value, error = validator.validate("12.00.01")
    assert error == ValidationError(text="Must be a valid time format.", code="format")

    validator = Time()
    value, error = validator.validate("12:00:60")
    assert error == ValidationError(text="Must be a real time.", code="invalid")


def test_datetime():
    validator = DateTime()
    value, error = validator.validate("2049-1-1 12:00:00")
    assert value == datetime.datetime(2049, 1, 1, 12, 0, 0)

    tzinfo = datetime.timezone.utc
    validator = DateTime()
    value, error = validator.validate("2049-1-1 12:00:00Z")
    assert value == datetime.datetime(2049, 1, 1, 12, 0, 0, tzinfo=tzinfo)

    tzinfo = datetime.timezone(-datetime.timedelta(hours=2, minutes=30))
    validator = DateTime()
    value, error = validator.validate("2049-1-1 12:00:00-0230")
    assert value == datetime.datetime(2049, 1, 1, 12, 0, 0, tzinfo=tzinfo)

    validator = DateTime()
    value, error = validator.validate(datetime.datetime(2049, 1, 1, 12, 0, 0))
    assert value == datetime.datetime(2049, 1, 1, 12, 0, 0)

    validator = DateTime()
    value, error = validator.validate("2049:01:01 12:00:00")
    assert error == ValidationError(
        text="Must be a valid datetime format.", code="format"
    )

    validator = DateTime()
    value, error = validator.validate("2049-01-01 12:00:60")
    assert error == ValidationError(text="Must be a real datetime.", code="invalid")


def test_errors_dict_interface():
    """
    `validated.errors` should present a dict-like interface.
    """
    validator = Object(properties={"example": Integer()})
    validated = validator.validate({"example": "abc"})
    assert dict(validated.errors) == {"example": "Must be a number."}

    validator = Object(properties={"example": Integer()})
    validated = validator.validate({"example": "abc"})
    assert validated.errors["example"] == "Must be a number."

    validator = Object(additional_properties=Object(additional_properties=Integer()))
    validated = validator.validate({"example": {"nested": "abc"}})
    assert dict(validated.errors) == {"example": {"nested": "Must be a number."}}

    validator = Integer()
    validated = validator.validate("abc")
    assert validated.errors[""] == "Must be a number."

    validator = Integer()
    validated = validator.validate("abc")
    assert dict(validated.errors) == {"": "Must be a number."}


def test_error_messages_interface():
    """
    `errors.messages()` should return a list of ErrorMessage instances.
    """
    validator = Integer()
    value, error = validator.validate("abc")
    assert error.messages() == [ErrorMessage(text="Must be a number.", code="type")]
