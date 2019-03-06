from typesystem import Integer, Object, Schema
from typesystem.base import Message, Position
from typesystem.tokenize.tokenize_json import validate_json


def test_validate_json():
    value, messages = validate_json("")
    assert value is None
    assert messages == [
        Message(
            text="No content.",
            code="no_content",
            position=Position(line_no=1, column_no=1, char_index=0),
        )
    ]
    assert (
        repr(messages[0])
        == "Message(text='No content.', code='no_content', position=Position(line_no=1, column_no=1, char_index=0))"
    )

    value, messages = validate_json('{"a": 123}')
    assert value == {"a": 123}
    assert messages == []

    value, messages = validate_json(b'{"a": 123}')
    assert value == {"a": 123}
    assert messages == []

    value, messages = validate_json('{"a" 123}')
    assert value is None
    assert messages == [
        Message(
            text="Expecting ':' delimiter.",
            code="parse_error",
            position=Position(line_no=1, column_no=6, char_index=5),
        )
    ]

    validator = Object(properties=Integer())
    text = '{\n    "a": "123",\n    "b": "abc"}'
    value, messages = validate_json(text, validator=validator)
    assert value is None
    assert messages == [
        Message(
            text="Must be a number.",
            code="type",
            index=["b"],
            start_position=Position(line_no=3, column_no=10, char_index=27),
            end_position=Position(line_no=3, column_no=14, char_index=31),
        )
    ]
    assert (
        repr(messages[0])
        == "Message(text='Must be a number.', code='type', index=['b'], start_position=Position(line_no=3, column_no=10, char_index=27), end_position=Position(line_no=3, column_no=14, char_index=31))"
    )

    validator = Object(properties=Integer())
    text = '{\n    "a": "123",\n    "b": "456"}'
    value, messages = validate_json(text, validator=validator)
    assert value == {"a": 123, "b": 456}
    assert messages == []

    class Validator(Schema):
        a = Integer()
        b = Integer()

    text = '{\n    "a": "123",\n    "b": "abc"}'
    value, messages = validate_json(text, validator=Validator)
    assert value is None
    assert messages == [
        Message(
            text="Must be a number.",
            code="type",
            index=["b"],
            start_position=Position(line_no=3, column_no=10, char_index=27),
            end_position=Position(line_no=3, column_no=14, char_index=31),
        )
    ]

    text = '{"a": "123"}'
    value, messages = validate_json(text, validator=Validator)
    assert value is None
    assert messages == [
        Message(
            text="The field 'b' is required.",
            code="required",
            index=["b"],
            start_position=Position(line_no=1, column_no=1, char_index=0),
            end_position=Position(line_no=1, column_no=12, char_index=11),
        )
    ]
