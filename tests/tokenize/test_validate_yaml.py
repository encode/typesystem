import pytest

from typesystem import Integer, Object, Schema, ValidationError, validate_yaml
from typesystem.base import Message, Position


def test_validate_yaml():
    validator = Object(properties=Integer())
    text = "a: 123\nb: 456\n"
    value = validate_yaml(text, validator=validator)
    assert value == {"a": 123, "b": 456}

    validator = Object(properties=Integer())
    text = "a: 123\nb: abc\n"

    with pytest.raises(ValidationError) as exc_info:
        validate_yaml(text, validator=validator)

    exc = exc_info.value
    assert exc.messages() == [
        Message(
            text="Must be a number.",
            code="type",
            index=["b"],
            start_position=Position(line_no=2, column_no=4, char_index=10),
            end_position=Position(line_no=2, column_no=6, char_index=12),
        )
    ]

    class Validator(Schema):
        a = Integer()
        b = Integer()

    text = "a: 123\nb: abc\n"

    with pytest.raises(ValidationError) as exc_info:
        validate_yaml(text, validator=Validator)

    exc = exc_info.value
    assert exc.messages() == [
        Message(
            text="Must be a number.",
            code="type",
            index=["b"],
            start_position=Position(line_no=2, column_no=4, char_index=10),
            end_position=Position(line_no=2, column_no=6, char_index=12),
        )
    ]

    text = "a: 123"
    with pytest.raises(ValidationError) as exc_info:
        validate_yaml(text, validator=Validator)
    exc = exc_info.value
    assert exc.messages() == [
        Message(
            text="The field 'b' is required.",
            code="required",
            index=["b"],
            start_position=Position(line_no=1, column_no=1, char_index=0),
            end_position=Position(line_no=1, column_no=6, char_index=5),
        )
    ]
