from typesystem.validators import String, Integer


def test_string():
    validator = String()
    assert validator.validate("abc").value == "abc"
    assert validator.validate(None).errors == ["null"]
    assert validator.validate(123).errors == ["type"]

    validator = String(max_length=10)
    assert validator.validate("abc" * 10).errors == ["max_length"]

    validator = String(min_length=3)
    assert validator.validate("a").errors == ["min_length"]

    validator = String(allow_blank=False)
    assert validator.validate("").errors == ["blank"]

    validator = String(allow_null=True)
    assert validator.validate(None).value is None

    validator = String(exact="example")
    assert validator.validate("foo").errors == ["exact"]
    assert validator.validate("example")

    validator = String(enum=["red", "blue", "green"])
    assert validator.validate("foo").errors == ["enum"]
    assert validator.validate("red")

    validator = String(pattern="^[abc]*$")
    assert validator.validate("cba").value == "cba"
    assert validator.validate("cbxa").errors == ["pattern"]


def test_integer():
    validator = Integer()
    assert validator.validate(123).value == 123
    assert validator.validate("123").value == 123
    assert validator.validate(123.0).value == 123
    assert validator.validate(None).errors == ["null"]
    assert validator.validate("abc").errors == ["type"]
    assert validator.validate(True).errors == ["type"]
    assert validator.validate(123.1).errors == ["integer"]
    assert validator.validate(float('inf')).errors == ["integer"]
    assert validator.validate(float('nan')).errors == ["integer"]
    assert validator.validate("123", strict=True).errors == ["type"]

    validator = Integer(allow_null=True)
    assert validator.validate(None).value is None

    validator = Integer(maximum=10)
    assert validator.validate(100).errors == ["maximum"]
    assert validator.validate(10).value == 10

    validator = Integer(minimum=3)
    assert validator.validate(1).errors == ["minimum"]
    assert validator.validate(3).value == 3

    validator = Integer(exclusive_maximum=10)
    assert validator.validate(10).errors == ["exclusive_maximum"]

    validator = Integer(exclusive_minimum=3)
    assert validator.validate(3).errors == ["exclusive_minimum"]

    validator = Integer(enum=[1,2,3])
    assert validator.validate(5).errors == ["enum"]

    validator = Integer(enum=[123])
    assert validator.validate(5).errors == ["exact"]

    validator = Integer(exact=123)
    assert validator.validate(5).errors == ["exact"]

    validator = Integer(multiple_of=10)
    assert validator.validate(5).errors == ["multiple_of"]
