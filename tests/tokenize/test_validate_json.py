import pytest

from typesystem import Integer, Object, Schema, ValidationError
from typesystem.base import Message, Position
from typesystem.tokenize.tokenize_json import validate_json


def test_validate_json():
    validator = Object(properties=Integer())
    text = '{\n    "a": "123",\n    "b": "456"}'
    value = validate_json(text, validator=validator)
    assert value == {"a": 123, "b": 456}

    validator = Object(properties=Integer())
    text = '{\n    "a": "123",\n    "b": "abc"}'

    with pytest.raises(ValidationError) as exc_info:
        validate_json(text, validator=validator)
    exc = exc_info.value

    assert exc.messages() == [
        Message(
            text="Must be a number.",
            code="type",
            index=["b"],
            start_position=Position(line_no=3, column_no=10, char_index=27),
            end_position=Position(line_no=3, column_no=14, char_index=31),
        )
    ]
    assert (
        repr(exc.messages()[0])
        == "Message(text='Must be a number.', code='type', index=['b'], start_position=Position(line_no=3, column_no=10, char_index=27), end_position=Position(line_no=3, column_no=14, char_index=31))"
    )

    class Validator(Schema):
        a = Integer()
        b = Integer()

    text = '{\n    "a": "123",\n    "b": "abc"}'
    with pytest.raises(ValidationError) as exc_info:
        validate_json(text, validator=Validator)
    exc = exc_info.value
    assert exc.messages() == [
        Message(
            text="Must be a number.",
            code="type",
            index=["b"],
            start_position=Position(line_no=3, column_no=10, char_index=27),
            end_position=Position(line_no=3, column_no=14, char_index=31),
        )
    ]

    text = '{"a": "123"}'
    with pytest.raises(ValidationError) as exc_info:
        validate_json(text, validator=Validator)
    exc = exc_info.value
    assert exc.messages() == [
        Message(
            text="The field 'b' is required.",
            code="required",
            index=["b"],
            start_position=Position(line_no=1, column_no=1, char_index=0),
            end_position=Position(line_no=1, column_no=12, char_index=11),
        )
    ]
