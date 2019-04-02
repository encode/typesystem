import datetime
import decimal
import re
import uuid

from typesystem.base import Message, ValidationError
from typesystem.fields import (
    Array,
    Boolean,
    Choice,
    Const,
    Date,
    DateTime,
    Decimal,
    Float,
    Integer,
    Number,
    Object,
    String,
    Time,
    Union,
)


def test_string():
    validator = String()
    validated = validator.validate_or_error("abc")
    assert validated
    assert validated.value == "abc"
    assert validated.error is None

    validator = String()
    value, error = validator.validate_or_error("")
    assert error == ValidationError(text="Must not be blank.", code="blank")

    validator = String()
    value, error = validator.validate_or_error(None)
    assert error == ValidationError(text="May not be null.", code="null")

    validator = String()
    value, error = validator.validate_or_error(123)
    assert error == ValidationError(text="Must be a string.", code="type")

    validator = String(max_length=10)
    value, error = validator.validate_or_error("abc" * 10)
    assert error == ValidationError(
        text="Must have no more than 10 characters.", code="max_length"
    )

    validator = String(min_length=3)
    value, error = validator.validate_or_error("a")
    assert error == ValidationError(
        text="Must have at least 3 characters.", code="min_length"
    )

    validator = String(allow_blank=False)
    value, error = validator.validate_or_error("")
    assert error == ValidationError(text="Must not be blank.", code="blank")

    validator = String(allow_blank=True)
    value, error = validator.validate_or_error("")
    assert value == ""

    validator = String(allow_blank=True)
    value, error = validator.validate_or_error(None)
    assert value == ""

    validator = String(allow_null=True)
    value, error = validator.validate_or_error(None)
    assert value is None
    assert error is None

    validator = String(allow_null=True)
    value, error = validator.validate_or_error("")
    assert value is None
    assert error is None

    validator = String(allow_null=True)
    value, error = validator.validate_or_error(" ")
    assert value is None
    assert error is None

    validator = String(pattern="^[abc]*$")
    value, error = validator.validate_or_error("cba")
    assert value == "cba"

    validator = String(pattern="^[abc]*$")
    value, error = validator.validate_or_error("cbxa")
    assert error == ValidationError(
        text="Must match the pattern /^[abc]*$/.", code="pattern"
    )

    validator = String(pattern=re.compile("ABC", re.IGNORECASE))
    value, error = validator.validate_or_error("abc")
    assert value == "abc"

    validator = String()
    value, error = validator.validate_or_error(" ")
    assert error == ValidationError(text="Must not be blank.", code="blank")

    validator = String()
    value, error = validator.validate_or_error(" test ")
    assert value == "test"

    validator = String(trim_whitespace=False)
    value, error = validator.validate_or_error(" ")
    assert value == " "

    validator = String(trim_whitespace=False)
    value, error = validator.validate_or_error(" test ")
    assert value == " test "


def test_integer():
    validator = Integer()
    value, error = validator.validate_or_error(123)
    assert value == 123

    validator = Integer()
    value, error = validator.validate_or_error("123")
    assert value == 123

    validator = Integer()
    value, error = validator.validate_or_error(123.0)
    assert value == 123

    validator = Integer()
    value, error = validator.validate_or_error("123.0")
    assert value == 123

    validator = Integer()
    value, error = validator.validate_or_error(None)
    assert error == ValidationError(text="May not be null.", code="null")

    validator = Integer()
    value, error = validator.validate_or_error("abc")
    assert error == ValidationError(text="Must be a number.", code="type")

    validator = Integer()
    value, error = validator.validate_or_error(True)
    assert error == ValidationError(text="Must be a number.", code="type")

    validator = Integer()
    value, error = validator.validate_or_error(123.1)
    assert error == ValidationError(text="Must be an integer.", code="integer")

    validator = Integer()
    value, error = validator.validate_or_error(float("inf"))
    assert error == ValidationError(text="Must be an integer.", code="integer")

    validator = Integer()
    value, error = validator.validate_or_error(float("nan"))
    assert error == ValidationError(text="Must be an integer.", code="integer")

    validator = Integer()
    value, error = validator.validate_or_error("123", strict=True)
    assert error == ValidationError(text="Must be a number.", code="type")

    validator = Integer(allow_null=True)
    value, error = validator.validate_or_error(None)
    assert value is None
    assert error is None

    validator = Integer(allow_null=True)
    value, error = validator.validate_or_error("")
    assert value is None
    assert error is None

    validator = Integer(allow_null=True)
    value, error = validator.validate_or_error("", strict=True)
    assert error == ValidationError(text="Must be a number.", code="type")

    validator = Integer(maximum=10)
    value, error = validator.validate_or_error(100)
    assert error == ValidationError(
        text="Must be less than or equal to 10.", code="maximum"
    )

    validator = Integer(maximum=10)
    value, error = validator.validate_or_error(10)
    assert value == 10

    validator = Integer(minimum=3)
    value, error = validator.validate_or_error(1)
    assert error == ValidationError(
        text="Must be greater than or equal to 3.", code="minimum"
    )

    validator = Integer(minimum=3)
    value, error = validator.validate_or_error(3)
    assert value == 3

    validator = Integer(exclusive_maximum=10)
    value, error = validator.validate_or_error(10)
    assert error == ValidationError(
        text="Must be less than 10.", code="exclusive_maximum"
    )

    validator = Integer(exclusive_minimum=3)
    value, error = validator.validate_or_error(3)
    assert error == ValidationError(
        text="Must be greater than 3.", code="exclusive_minimum"
    )

    validator = Integer(multiple_of=10)
    value, error = validator.validate_or_error(5)
    assert error == ValidationError(
        text="Must be a multiple of 10.", code="multiple_of"
    )


def test_float():
    validator = Float()
    value, error = validator.validate_or_error(123.1)
    assert value == 123.1

    validator = Float()
    value, error = validator.validate_or_error(123)
    assert value == 123.0

    validator = Float()
    value, error = validator.validate_or_error("123.1")
    assert value == 123.1

    validator = Float()
    value, error = validator.validate_or_error(None)
    assert error == ValidationError(text="May not be null.", code="null")

    validator = Float()
    value, error = validator.validate_or_error("abc")
    assert error == ValidationError(text="Must be a number.", code="type")

    validator = Float()
    value, error = validator.validate_or_error(True)
    assert error == ValidationError(text="Must be a number.", code="type")

    validator = Float()
    value, error = validator.validate_or_error(float("inf"))
    assert error == ValidationError(text="Must be finite.", code="finite")

    validator = Float()
    value, error = validator.validate_or_error(float("nan"))
    assert error == ValidationError(text="Must be finite.", code="finite")

    validator = Float()
    value, error = validator.validate_or_error("123", strict=True)
    assert error == ValidationError(text="Must be a number.", code="type")

    validator = Float(allow_null=True)
    value, error = validator.validate_or_error(None)
    assert value is None
    assert error is None

    validator = Float(maximum=10.0)
    value, error = validator.validate_or_error(100.0)
    assert error == ValidationError(
        text="Must be less than or equal to 10.0.", code="maximum"
    )

    validator = Float(maximum=10.0)
    value, error = validator.validate_or_error(10.0)
    assert value == 10.0

    validator = Float(minimum=3.0)
    value, error = validator.validate_or_error(1.0)
    assert error == ValidationError(
        text="Must be greater than or equal to 3.0.", code="minimum"
    )

    validator = Float(minimum=3.0)
    value, error = validator.validate_or_error(3.0)
    assert value == 3.0

    validator = Float(exclusive_maximum=10.0)
    value, error = validator.validate_or_error(10.0)
    assert error == ValidationError(
        text="Must be less than 10.0.", code="exclusive_maximum"
    )

    validator = Float(exclusive_minimum=3.0)
    value, error = validator.validate_or_error(3.0)
    assert error == ValidationError(
        text="Must be greater than 3.0.", code="exclusive_minimum"
    )

    validator = Float(precision="0.01")
    value, error = validator.validate_or_error("123.456")
    assert value == 123.46

    validator = Float(multiple_of=0.05, precision="0.01")
    value, error = validator.validate_or_error("123.05")
    assert value == 123.05

    validator = Float(multiple_of=0.05, precision="0.01")
    value, error = validator.validate_or_error("123.06")
    assert error == ValidationError(
        text="Must be a multiple of 0.05.", code="multiple_of"
    )


def test_decimal():
    validator = Decimal(precision="0.01")
    value, error = validator.validate_or_error(123.01)
    assert value == decimal.Decimal("123.01")


def test_number():
    validator = Number()
    value, error = validator.validate_or_error(123.0)
    assert value == 123.0

    validator = Number()
    value, error = validator.validate_or_error(123)
    assert value == 123

    validator = Number(precision="0.1")
    value, error = validator.validate_or_error(123)
    assert value == 123

    validator = Number(precision="0.1")
    value, error = validator.validate_or_error(123.123)
    assert value == 123.1


def test_boolean():
    validator = Boolean()
    value, error = validator.validate_or_error(True)
    assert value is True

    validator = Boolean()
    value, error = validator.validate_or_error(False)
    assert value is False

    validator = Boolean()
    value, error = validator.validate_or_error("True")
    assert value is True

    validator = Boolean()
    value, error = validator.validate_or_error(1)
    assert value is True

    validator = Boolean()
    value, error = validator.validate_or_error(None)
    assert error == ValidationError(text="May not be null.", code="null")

    validator = Boolean()
    value, error = validator.validate_or_error(2)
    assert error == ValidationError(text="Must be a boolean.", code="type")

    validator = Boolean()
    value, error = validator.validate_or_error([])
    assert error == ValidationError(text="Must be a boolean.", code="type")

    validator = Boolean(allow_null=True)
    value, error = validator.validate_or_error(None)
    assert value is None
    assert error is None

    validator = Boolean(allow_null=True)
    value, error = validator.validate_or_error("")
    assert value is None
    assert error is None

    validator = Boolean()
    value, error = validator.validate_or_error("True", strict=True)
    assert error == ValidationError(text="Must be a boolean.", code="type")


def test_choice():
    validator = Choice(choices=[("R", "red"), ("B", "blue"), ("G", "green")])
    value, error = validator.validate_or_error(None)
    assert error == ValidationError(text="May not be null.", code="null")

    validator = Choice(
        choices=[("R", "red"), ("B", "blue"), ("G", "green")], allow_null=True
    )
    value, error = validator.validate_or_error(None)
    assert value is None
    assert error is None

    validator = Choice(choices=[("R", "red"), ("B", "blue"), ("G", "green")])
    value, error = validator.validate_or_error("")
    assert error == ValidationError(text="This field is required.", code="required")

    validator = Choice(
        choices=[("R", "red"), ("B", "blue"), ("G", "green")], allow_null=True
    )
    value, error = validator.validate_or_error("")
    assert value is None
    assert error is None

    validator = Choice(choices=[("R", "red"), ("B", "blue"), ("G", "green")])
    value, error = validator.validate_or_error("Z")
    assert error == ValidationError(text="Not a valid choice.", code="choice")

    validator = Choice(choices=[("R", "red"), ("B", "blue"), ("G", "green")])
    value, error = validator.validate_or_error("R")
    assert value == "R"

    validator = Choice(
        choices=[("", "empty"), ("R", "red"), ("B", "blue"), ("G", "green")],
        allow_null=True,
    )
    value, error = validator.validate_or_error("")
    assert value == ""

    validator = Choice(
        choices=[("", "empty"), ("R", "red"), ("B", "blue"), ("G", "green")],
        allow_null=True,
    )
    value, error = validator.validate_or_error(None)
    assert value is None

    validator = Choice(choices=["red", "green", "blue"])
    value, error = validator.validate_or_error("red")
    assert value is "red"


def test_object():
    validator = Object()
    value, error = validator.validate_or_error({})
    assert value == {}

    validator = Object()
    value, error = validator.validate_or_error(None)
    assert dict(error) == {"": "May not be null."}

    validator = Object()
    value, error = validator.validate_or_error(123)
    assert dict(error) == {"": "Must be an object."}

    validator = Object()
    value, error = validator.validate_or_error({1: 123})
    assert dict(error) == {1: "All object keys must be strings."}

    validator = Object(property_names=String(min_length=3))
    value, error = validator.validate_or_error({"a": 123})
    assert dict(error) == {"a": "Invalid property name."}

    validator = Object(allow_null=True)
    value, error = validator.validate_or_error(None)
    assert value is None
    assert error is None

    validator = Object(min_properties=1)
    value, error = validator.validate_or_error({})
    assert dict(error) == {"": "Must not be empty."}

    validator = Object(min_properties=1)
    value, error = validator.validate_or_error({"a": 1})
    assert value == {"a": 1}

    validator = Object(min_properties=2)
    value, error = validator.validate_or_error({})
    assert dict(error) == {"": "Must have at least 2 properties."}

    validator = Object(min_properties=2)
    value, error = validator.validate_or_error({"a": 1, "b": 2})
    assert value == {"a": 1, "b": 2}

    validator = Object(max_properties=2)
    value, error = validator.validate_or_error({})
    assert value == {}

    validator = Object(max_properties=2)
    value, error = validator.validate_or_error({"a": 1, "b": 2, "c": 3})
    assert dict(error) == {"": "Must have no more than 2 properties."}

    validator = Object(required=["example"])
    value, error = validator.validate_or_error({"example": 123})
    assert value == {"example": 123}

    validator = Object(required=["example"])
    value, error = validator.validate_or_error({})
    assert dict(error) == {"example": "This field is required."}

    validator = Object(properties={"example": Integer()})
    value, error = validator.validate_or_error({"example": "123"})
    assert value == {"example": 123}

    validator = Object(properties={"example": Integer()})
    value, error = validator.validate_or_error({"example": "abc"})
    assert dict(error) == {"example": "Must be a number."}

    validator = Object(pattern_properties={"^x-.*$": Integer()})
    value, error = validator.validate_or_error({"x-example": "123"})
    assert value == {"x-example": 123}

    validator = Object(pattern_properties={"^x-.*$": Integer()})
    value, error = validator.validate_or_error({"x-example": "abc"})
    assert dict(error) == {"x-example": "Must be a number."}

    validator = Object(properties={"example": Integer(default=0)})
    value, error = validator.validate_or_error({"example": "123"})
    assert value == {"example": 123}

    validator = Object(properties={"example": Integer(default=0)})
    value, error = validator.validate_or_error({})
    assert value == {"example": 0}

    validator = Object(additional_properties=False)
    value, error = validator.validate_or_error({"example": "123"})
    assert dict(error) == {"example": "Invalid property name."}

    validator = Object(additional_properties=True)
    value, error = validator.validate_or_error({"example": "abc"})
    assert value == {"example": "abc"}

    validator = Object(additional_properties=None)
    value, error = validator.validate_or_error({"example": "abc"})
    assert value == {}

    validator = Object(properties=Integer())
    value, error = validator.validate_or_error({"example": "123"})
    assert value == {"example": 123}

    validator = Object(properties=Integer())
    value, error = validator.validate_or_error({"example": "abc"})
    assert dict(error) == {"example": "Must be a number."}

    validator = Object(properties={"example": Integer()})
    value, error = validator.validate_or_error({"example": "123"})
    assert value == {"example": 123}

    validator = Object(properties={"example": Integer()})
    value, error = validator.validate_or_error({"example": "abc"})
    assert dict(error) == {"example": "Must be a number."}

    validator = Object(additional_properties=Object(additional_properties=Integer()))
    value, error = validator.validate_or_error({"example": {"nested": "123"}})
    assert value == {"example": {"nested": 123}}

    validator = Object(additional_properties=Object(additional_properties=Integer()))
    value, error = validator.validate_or_error({"example": {"nested": "abc"}})
    assert dict(error) == {"example": {"nested": "Must be a number."}}


def test_array():
    validator = Array()
    value, error = validator.validate_or_error([])
    assert value == []

    validator = Array()
    value, error = validator.validate_or_error(None)
    assert error == ValidationError(text="May not be null.", code="null")

    validator = Array()
    value, error = validator.validate_or_error(123)
    assert error == ValidationError(text="Must be an array.", code="type")

    validator = Array(allow_null=True)
    value, error = validator.validate_or_error(None)
    assert value is None
    assert error is None

    validator = Array(min_items=1)
    value, error = validator.validate_or_error([])
    assert error == ValidationError(text="Must not be empty.", code="empty")

    validator = Array(min_items=1)
    value, error = validator.validate_or_error([1])
    assert value == [1]

    validator = Array(min_items=2)
    value, error = validator.validate_or_error([])
    assert error == ValidationError(
        text="Must have at least 2 items.", code="min_items"
    )

    validator = Array(min_items=2)
    value, error = validator.validate_or_error([1, 2])
    assert value == [1, 2]

    validator = Array(max_items=2)
    value, error = validator.validate_or_error([])
    assert value == []

    validator = Array(max_items=2)
    value, error = validator.validate_or_error([1, 2, 3])
    assert error == ValidationError(
        text="Must have no more than 2 items.", code="max_items"
    )

    validator = Array(exact_items=2)
    value, error = validator.validate_or_error([1, 2])
    assert value == [1, 2]

    validator = Array(exact_items=2)
    value, error = validator.validate_or_error([1, 2, 3])
    assert error == ValidationError(text="Must have 2 items.", code="exact_items")

    validator = Array(items=Integer())
    value, error = validator.validate_or_error(["1", 2, "3"])
    assert value == [1, 2, 3]

    validator = Array(items=Integer())
    value, error = validator.validate_or_error(["a", 2, "c"])
    assert dict(error) == {0: "Must be a number.", 2: "Must be a number."}

    validator = Array(items=[String(), Integer()])
    value, error = validator.validate_or_error(["a", "b", "c"])
    assert error == ValidationError(text="Must have 2 items.", code="exact_items")

    validator = Array(items=[String(), Integer()])
    value, error = validator.validate_or_error(["a", "123"])
    assert value == ["a", 123]

    validator = Array(items=[String(), Integer()], additional_items=Integer())
    value, error = validator.validate_or_error(["a", "123", "456"])
    assert value == ["a", 123, 456]

    validator = Array(items=String(), unique_items=True)
    value, error = validator.validate_or_error(["a", "b"])
    assert value == ["a", "b"]

    validator = Array(items=String(), unique_items=True)
    value, error = validator.validate_or_error(["a", "a"])
    assert dict(error) == {1: "Items must be unique."}

    validator = Array(items=[String(), Integer(), Boolean()], min_items=1)
    value, error = validator.validate_or_error(["a"])
    assert value == ["a"]

    validator = Array(items=[String(), Integer(), Boolean()], min_items=1)
    value, error = validator.validate_or_error(["a", "123"])
    assert value == ["a", 123]

    validator = Array(items=[String(), Integer(), Boolean()], min_items=1)
    value, error = validator.validate_or_error([])
    assert error == ValidationError(text="Must not be empty.", code="empty")

    validator = Array(items=[String(), Integer(), Boolean()], min_items=2)
    value, error = validator.validate_or_error([])
    assert error == ValidationError(
        text="Must have at least 2 items.", code="min_items"
    )


def test_date():
    validator = Date()
    value, error = validator.validate_or_error("2049-01-01")
    assert value == datetime.date(2049, 1, 1)

    validator = Date()
    value, error = validator.validate_or_error(datetime.date(2049, 1, 1))
    assert value == datetime.date(2049, 1, 1)

    validator = Date()
    value, error = validator.validate_or_error("20490101")
    assert error == ValidationError(text="Must be a valid date format.", code="format")

    validator = Date()
    value, error = validator.validate_or_error("2049-01-32")
    assert error == ValidationError(text="Must be a real date.", code="invalid")


def test_time():
    validator = Time()
    value, error = validator.validate_or_error("12:00:01")
    assert value == datetime.time(12, 0, 1)

    validator = Time()
    value, error = validator.validate_or_error("12:00:01.001")
    assert value == datetime.time(12, 0, 1, 1000)

    validator = Time()
    value, error = validator.validate_or_error("12:00:01.000001")
    assert value == datetime.time(12, 0, 1, 1)

    validator = Time()
    value, error = validator.validate_or_error(datetime.time(12, 0, 1))
    assert value == datetime.time(12, 0, 1)

    validator = Time()
    value, error = validator.validate_or_error("12.00.01")
    assert error == ValidationError(text="Must be a valid time format.", code="format")

    validator = Time()
    value, error = validator.validate_or_error("12:00:60")
    assert error == ValidationError(text="Must be a real time.", code="invalid")


def test_datetime():
    validator = DateTime()
    value, error = validator.validate_or_error("2049-1-1 12:00:00")
    assert value == datetime.datetime(2049, 1, 1, 12, 0, 0)

    validator = DateTime()
    value, error = validator.validate_or_error("2049-1-1 12:00:00.001")
    assert value == datetime.datetime(2049, 1, 1, 12, 0, 0, 1000)

    tzinfo = datetime.timezone.utc
    validator = DateTime()
    value, error = validator.validate_or_error("2049-1-1 12:00:00Z")
    assert value == datetime.datetime(2049, 1, 1, 12, 0, 0, tzinfo=tzinfo)

    tzinfo = datetime.timezone(-datetime.timedelta(hours=2, minutes=30))
    validator = DateTime()
    value, error = validator.validate_or_error("2049-1-1 12:00:00-0230")
    assert value == datetime.datetime(2049, 1, 1, 12, 0, 0, tzinfo=tzinfo)

    validator = DateTime()
    value, error = validator.validate_or_error(datetime.datetime(2049, 1, 1, 12, 0, 0))
    assert value == datetime.datetime(2049, 1, 1, 12, 0, 0)

    validator = DateTime()
    value, error = validator.validate_or_error("2049:01:01 12:00:00")
    assert error == ValidationError(
        text="Must be a valid datetime format.", code="format"
    )

    validator = DateTime()
    value, error = validator.validate_or_error("2049-01-01 12:00:60")
    assert error == ValidationError(text="Must be a real datetime.", code="invalid")


def test_uuid():
    validator = String(format="uuid")
    value, error = validator.validate_or_error("93e19019-c7a6-45fe-8936-f6f4d550f35f")
    assert value == uuid.UUID("93e19019-c7a6-45fe-8936-f6f4d550f35f")

    validator = String(format="uuid")
    value, error = validator.validate_or_error("1245a678-1234-1234-1234-123412341234")
    assert error == ValidationError(text="Must be valid UUID format.", code="format")


def test_union():
    validator = Union(any_of=[Integer(), String()])
    value, error = validator.validate_or_error("abc")
    assert value == "abc"
    assert error is None

    validator = Union(any_of=[Integer(), String()])
    value, error = validator.validate_or_error(123)
    assert value == 123
    assert error is None

    validator = Union(any_of=[Integer(), String()])
    value, error = validator.validate_or_error(None)
    assert value is None
    assert error == ValidationError(text="May not be null.", code="null")

    validator = Union(any_of=[Integer(), String()])
    value, error = validator.validate_or_error(True)
    assert value is None
    assert error == ValidationError(text="Did not match any valid type.", code="union")

    validator = Union(any_of=[Integer(allow_null=True), String()])
    value, error = validator.validate_or_error(None)
    assert error is None
    assert value is None

    validator = Union(any_of=[Integer(), String()], allow_null=True)
    value, error = validator.validate_or_error(None)
    assert error is None
    assert value is None

    validator = Union(any_of=[Integer(maximum=1000), String()])
    value, error = validator.validate_or_error(9999)
    assert value is None
    assert error == ValidationError(
        text="Must be less than or equal to 1000.", code="maximum"
    )

    validator = Integer() | String() | Boolean()
    value, error = validator.validate_or_error(123)
    assert value == 123

    validator = Integer() | (String() | Boolean())
    value, error = validator.validate_or_error(123)
    assert value == 123


def test_const():
    validator = Const(const=None)
    value, error = validator.validate_or_error(None)
    assert value is None
    assert error is None

    validator = Const(const=None)
    value, error = validator.validate_or_error(123)
    assert value is None
    assert error == ValidationError(text="Must be null.", code="only_null")

    validator = Const(const="abc")
    value, error = validator.validate_or_error("def")
    assert value is None
    assert error == ValidationError(text="Must be the value 'abc'.", code="const")

    validator = Const(const="abc")
    value, error = validator.validate_or_error("abc")
    assert value == "abc"
    assert error is None


def test_errors_dict_interface():
    """
    `validated.errors` should present a dict-like interface.
    """
    validator = Object(properties={"example": Integer()})
    value, error = validator.validate_or_error({"example": "abc"})
    assert dict(error) == {"example": "Must be a number."}

    validator = Object(properties={"example": Integer()})
    value, error = validator.validate_or_error({"example": "abc"})
    assert error["example"] == "Must be a number."

    validator = Object(additional_properties=Object(additional_properties=Integer()))
    value, error = validator.validate_or_error({"example": {"nested": "abc"}})
    assert dict(error) == {"example": {"nested": "Must be a number."}}

    validator = Integer()
    value, error = validator.validate_or_error("abc")
    assert error[""] == "Must be a number."

    validator = Integer()
    value, error = validator.validate_or_error("abc")
    assert dict(error) == {"": "Must be a number."}


def test_error_messages_interface():
    """
    `errors.messages()` should return a list of Message instances.
    """
    validator = Integer()
    value, error = validator.validate_or_error("abc")
    assert error.messages() == [Message(text="Must be a number.", code="type")]


def test_validation_error_is_hashable():
    validator = Integer()
    _, error = validator.validate_or_error("abc")
    hash(error)
