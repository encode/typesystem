from typesystem.base import Message, ValidationError
from typesystem.composites import AllOf, NeverMatch, Not, OneOf
from typesystem.fields import Integer, String


def test_never_match():
    validator = NeverMatch()
    value, error = validator.validate_or_error(123)
    assert value is None
    assert error == ValidationError(text="This never validates.", code="never")


def test_one_of():
    validator = OneOf([String(), Integer()])
    value, error = validator.validate_or_error(123)
    assert value is 123
    assert error is None

    validator = OneOf([String(allow_null=True), Integer()])
    value, error = validator.validate_or_error(None)
    assert value is None
    assert error is None

    validator = OneOf([String(allow_null=True), Integer(allow_null=True)])
    value, error = validator.validate_or_error(None)
    assert value is None
    assert error == ValidationError(
        text="Matched more than one type.", code="multiple_matches"
    )

    validator = OneOf([String(), Integer()])
    value, error = validator.validate_or_error(None)
    assert value is None
    assert error == ValidationError(
        text="Did not match any valid type.", code="no_match"
    )


def test_all_of():
    validator = AllOf([Integer(multiple_of=5), Integer(multiple_of=3)])
    value, error = validator.validate_or_error(3)
    assert value is None
    assert error == ValidationError(text="Must be a multiple of 5.", code="multiple_of")

    validator = AllOf([Integer(multiple_of=5), Integer(multiple_of=3)])
    value, error = validator.validate_or_error(5)
    assert value is None
    assert error == ValidationError(text="Must be a multiple of 3.", code="multiple_of")

    validator = AllOf([Integer(multiple_of=5), Integer(multiple_of=3)])
    value, error = validator.validate_or_error(15)
    assert value == 15
    assert error is None


def test_not():
    validator = Not(Integer())
    value, error = validator.validate_or_error("abc")
    assert value == "abc"
    assert error is None

    validator = Not(Integer())
    value, error = validator.validate_or_error(5)
    assert value is None
    assert error == ValidationError(text="Must not match.", code="negated")
