import datetime

from typesystem.base import ErrorMessage
from typesystem.validators import (
    Boolean,
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

    validator = String()
    validated = validator.validate(None)
    assert validated.errors == ["null"]

    validator = String()
    validated = validator.validate(123)
    assert validated.errors == ["type"]

    validator = String(max_length=10)
    validated = validator.validate("abc" * 10)
    assert validated.errors == ["max_length"]

    validator = String(min_length=3)
    validated = validator.validate("a")
    assert validated.errors == ["min_length"]

    validator = String(allow_blank=False)
    validated = validator.validate("")
    assert validated.errors == ["blank"]

    validator = String(allow_null=True)
    validated = validator.validate(None)
    assert validated.value is None

    validator = String(exact="example")
    validated = validator.validate("foo")
    assert validated.errors == ["exact"]

    validator = String(exact="example")
    validated = validator.validate("example")
    assert validated.value == "example"

    validator = String(enum=["red", "blue", "green"])
    validated = validator.validate("foo")
    assert validated.errors == ["enum"]

    validator = String(enum=["red", "blue", "green"])
    validated = validator.validate("red")
    assert validated.value == "red"

    validator = String(pattern="^[abc]*$")
    validated = validator.validate("cba")
    assert validated.value == "cba"

    validator = String(pattern="^[abc]*$")
    validated = validator.validate("cbxa")
    assert validated.errors == ["pattern"]


def test_integer():
    validator = Integer()
    validated = validator.validate(123)
    assert validated.value == 123

    validator = Integer()
    validated = validator.validate("123")
    assert validated.value == 123

    validator = Integer()
    validated = validator.validate(123.0)
    assert validated.value == 123

    validator = Integer()
    validated = validator.validate(None)
    assert validated.errors == ["null"]

    validator = Integer()
    validated = validator.validate("abc")
    assert validated.errors == ["type"]

    validator = Integer()
    validated = validator.validate(True)
    assert validated.errors == ["type"]

    validator = Integer()
    validated = validator.validate(123.1)
    assert validated.errors == ["integer"]

    validator = Integer()
    validated = validator.validate(float("inf"))
    assert validated.errors == ["integer"]

    validator = Integer()
    validated = validator.validate(float("nan"))
    assert validated.errors == ["integer"]

    validator = Integer()
    validated = validator.validate("123", strict=True)
    assert validated.errors == ["type"]

    validator = Integer(allow_null=True)
    validated = validator.validate(None)
    assert validated.value is None

    validator = Integer(maximum=10)
    validated = validator.validate(100)
    assert validated.errors == ["maximum"]

    validator = Integer(maximum=10)
    validated = validator.validate(10)
    assert validated.value == 10

    validator = Integer(minimum=3)
    validated = validator.validate(1)
    assert validated.errors == ["minimum"]

    validator = Integer(minimum=3)
    validated = validator.validate(3)
    assert validated.value == 3

    validator = Integer(exclusive_maximum=10)
    validated = validator.validate(10)
    assert validated.errors == ["exclusive_maximum"]

    validator = Integer(exclusive_minimum=3)
    validated = validator.validate(3)
    assert validated.errors == ["exclusive_minimum"]

    validator = Integer(enum=[1, 2, 3])
    validated = validator.validate(5)
    assert validated.errors == ["enum"]

    validator = Integer(enum=[123])
    validated = validator.validate(5)
    assert validated.errors == ["exact"]

    validator = Integer(exact=123)
    validated = validator.validate(5)
    assert validated.errors == ["exact"]

    validator = Integer(multiple_of=10)
    validated = validator.validate(5)
    assert validated.errors == ["multiple_of"]


def test_float():
    validator = Float()
    validated = validator.validate(123.1)
    assert validated.value == 123.1

    validator = Float()
    validated = validator.validate(123)
    assert validated.value == 123.0

    validator = Float()
    validated = validator.validate("123.1")
    assert validated.value == 123.1

    validator = Float()
    validated = validator.validate(None)
    assert validated.errors == ["null"]

    validator = Float()
    validated = validator.validate("abc")
    assert validated.errors == ["type"]

    validator = Float()
    validated = validator.validate(True)
    assert validated.errors == ["type"]

    validator = Float()
    validated = validator.validate(float("inf"))
    assert validated.errors == ["finite"]

    validator = Float()
    validated = validator.validate(float("nan"))
    assert validated.errors == ["finite"]

    validator = Float()
    validated = validator.validate("123", strict=True)
    assert validated.errors == ["type"]

    validator = Float(allow_null=True)
    validated = validator.validate(None)
    assert validated.value is None

    validator = Float(maximum=10.0)
    validated = validator.validate(100.0)
    assert validated.errors == ["maximum"]

    validator = Float(maximum=10.0)
    validated = validator.validate(10.0)
    assert validated.value == 10.0

    validator = Float(minimum=3.0)
    validated = validator.validate(1.0)
    assert validated.errors == ["minimum"]

    validator = Float(minimum=3.0)
    validated = validator.validate(3.0)
    assert validated.value == 3.0

    validator = Float(exclusive_maximum=10.0)
    validated = validator.validate(10.0)
    assert validated.errors == ["exclusive_maximum"]

    validator = Float(exclusive_minimum=3.0)
    validated = validator.validate(3.0)
    assert validated.errors == ["exclusive_minimum"]

    validator = Float(enum=[1.0, 2.0, 3.0])
    validated = validator.validate(5.0)
    assert validated.errors == ["enum"]

    validator = Float(enum=[123.0])
    validated = validator.validate(5.0)
    assert validated.errors == ["exact"]

    validator = Float(exact=123.0)
    validated = validator.validate(5.0)
    assert validated.errors == ["exact"]

    validator = Float(multiple_of=10.0)
    validated = validator.validate(5.0)
    assert validated.errors == ["multiple_of"]


def test_boolean():
    validator = Boolean()
    validated = validator.validate(True)
    assert validated.value is True

    validator = Boolean()
    validated = validator.validate(False)
    assert validated.value is False

    validator = Boolean()
    validated = validator.validate("True")
    assert validated.value is True

    validator = Boolean()
    validated = validator.validate(1)
    assert validated.value is True

    validator = Boolean()
    validated = validator.validate(None)
    assert validated.errors == ["null"]

    validator = Boolean()
    validated = validator.validate(2)
    assert validated.errors == ["type"]

    validator = Boolean(allow_null=True)
    validated = validator.validate(None)
    assert validated.value is None

    validator = Boolean(allow_null=True)
    validated = validator.validate("")
    assert validated.value is None

    validator = Boolean()
    validated = validator.validate("True", strict=True)
    assert validated.errors == ["type"]


def test_object():
    validator = Object()
    validated = validator.validate({})
    assert validated.value == {}

    validator = Object()
    validated = validator.validate(None)
    assert validated.errors == ["null"]

    validator = Object()
    validated = validator.validate(123)
    assert validated.errors == ["type"]

    validator = Object()
    validated = validator.validate({1: 123})
    assert validated.errors == ["invalid_key"]

    validator = Object(allow_null=True)
    validated = validator.validate(None)
    assert validated.value == None

    validator = Object(min_properties=1)
    validated = validator.validate({})
    assert validated.errors == ["empty"]

    validator = Object(min_properties=1)
    validated = validator.validate({"a": 1})
    assert validated.is_valid

    validator = Object(min_properties=2)
    validated = validator.validate({})
    assert validated.errors == ["min_properties"]

    validator = Object(min_properties=2)
    validated = validator.validate({"a": 1, "b": 2})
    assert validated.is_valid

    validator = Object(max_properties=2)
    validated = validator.validate({})
    assert validated.is_valid

    validator = Object(max_properties=2)
    validated = validator.validate({"a": 1, "b": 2, "c": 3})
    assert validated.errors == ["max_properties"]

    validator = Object(required=["example"])
    validated = validator.validate({"example": 123})
    assert validated.value == {"example": 123}

    validator = Object(required=["example"])
    validated = validator.validate({})
    assert validated.errors.to_dict(style="code") == {"example": "required"}

    validator = Object(properties={"example": Integer()})
    validated = validator.validate({"example": "123"})
    assert validated.value == {"example": 123}

    validator = Object(properties={"example": Integer()})
    validated = validator.validate({"example": "abc"})
    assert validated.errors.to_dict(style="code") == {"example": "type"}

    validator = Object(pattern_properties={"^x-.*$": Integer()})
    validated = validator.validate({"x-example": "123"})
    assert validated.value == {"x-example": 123}

    validator = Object(pattern_properties={"^x-.*$": Integer()})
    validated = validator.validate({"x-example": "abc"})
    assert validated.errors.to_dict(style="code") == {"x-example": "type"}

    validator = Object(properties={"example": Integer(default=0)})
    validated = validator.validate({"example": "123"})
    assert validated.value == {"example": 123}

    validator = Object(properties={"example": Integer(default=0)})
    validated = validator.validate({})
    assert validated.value == {"example": 0}

    validator = Object(additional_properties=False)
    validated = validator.validate({"example": "123"})
    assert validated.errors.to_dict(style="code") == {"example": "invalid_property"}

    validator = Object(additional_properties=True)
    validated = validator.validate({"example": "abc"})
    assert validated.value == {"example": "abc"}

    validator = Object(additional_properties=None)
    validated = validator.validate({"example": "abc"})
    assert validated.value == {}

    validator = Object(additional_properties=Integer())
    validated = validator.validate({"example": "123"})
    assert validated.value == {"example": 123}

    validator = Object(additional_properties=Integer())
    validated = validator.validate({"example": "abc"})
    assert validated.errors.to_dict(style="code") == {"example": "type"}

    validator = Object(properties={"example": Integer()})
    validated = validator.validate({"example": "123"})
    assert validated.value == {"example": 123}

    validator = Object(properties={"example": Integer()})
    validated = validator.validate({"example": "abc"})
    assert validated.errors.to_dict(style="code") == {"example": "type"}

    validator = Object(additional_properties=Object(additional_properties=Integer()))
    validated = validator.validate({"example": {"nested": "123"}})
    assert validated.value == {"example": {"nested": 123}}

    validator = Object(additional_properties=Object(additional_properties=Integer()))
    validated = validator.validate({"example": {"nested": "abc"}})
    assert validated.errors.to_dict(style="code") == {"example": {"nested": "type"}}


def test_date():
    validator = Date()
    validated = validator.validate("2049-01-01")
    assert validated.value == datetime.date(2049, 1, 1)

    validator = Date()
    validated = validator.validate(datetime.date(2049, 1, 1))
    assert validated.value == datetime.date(2049, 1, 1)

    validator = Date()
    validated = validator.validate("20490101")
    assert validated.errors == ["format"]

    validator = Date()
    validated = validator.validate("2049-01-32")
    assert validated.errors == ["invalid"]


def test_time():
    validator = Time()
    validated = validator.validate("12:00:01")
    assert validated.value == datetime.time(12, 0, 1)

    validator = Time()
    validated = validator.validate("12:00:01.001")
    assert validated.value == datetime.time(12, 0, 1, 1000)

    validator = Time()
    validated = validator.validate("12:00:01.000001")
    assert validated.value == datetime.time(12, 0, 1, 1)

    validator = Time()
    validated = validator.validate(datetime.time(12, 0, 1))
    assert validated.value == datetime.time(12, 0, 1)

    validator = Time()
    validated = validator.validate("12.00.01")
    assert validated.errors == ["format"]

    validator = Time()
    validated = validator.validate("12:00:60")
    assert validated.errors == ["invalid"]


def test_datetime():
    validator = DateTime()
    validated = validator.validate("2049-1-1 12:00:00")
    assert validated.value == datetime.datetime(2049, 1, 1, 12, 0, 0)

    tzinfo = datetime.timezone.utc
    validator = DateTime()
    validated = validator.validate("2049-1-1 12:00:00Z")
    assert validated.value == datetime.datetime(2049, 1, 1, 12, 0, 0, tzinfo=tzinfo)

    tzinfo = datetime.timezone(-datetime.timedelta(hours=2, minutes=30))
    validator = DateTime()
    validated = validator.validate("2049-1-1 12:00:00-0230")
    assert validated.value == datetime.datetime(2049, 1, 1, 12, 0, 0, tzinfo=tzinfo)

    validator = DateTime()
    validated = validator.validate(datetime.datetime(2049, 1, 1, 12, 0, 0))
    assert validated.value == datetime.datetime(2049, 1, 1, 12, 0, 0)

    validator = DateTime()
    validated = validator.validate("2049:01:01 12:00:00")
    assert validated.errors == ["format"]

    validator = DateTime()
    validated = validator.validate("2049-01-01 12:00:60")
    assert validated.errors == ["invalid"]


def test_validated_result_interface():
    validator = String()
    value, errors = validator.validate("abc")
    assert value == "abc"
    assert not errors


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


def test_errors_list_interface():
    """
    `validated.errors` should present a sequence interface.
    """
    validator = Integer()
    validated = validator.validate("abc")
    assert list(validated.errors) == [
        ErrorMessage(text="Must be a number.", code="type")
    ]

    validator = Integer()
    validated = validator.validate("abc")
    for error in validated.errors:
        assert error == ErrorMessage(text="Must be a number.", code="type")

    validator = Integer()
    validated = validator.validate("abc")
    assert len(validated.errors) == 1
