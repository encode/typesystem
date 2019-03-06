from typesystem import Integer, Object, Schema
from typesystem.base import Message, Position
from typesystem.tokenize.tokenize_yaml import validate_yaml


def test_validate_yaml():
    value, messages = validate_yaml("")
    assert value is None
    assert messages == [
        Message(
            text="No content.",
            code="no_content",
            position=Position(line_no=1, column_no=1, char_index=0),
        )
    ]

    value, messages = validate_yaml("a: 123")
    assert value == {"a": 123}
    assert messages == []

    value, messages = validate_yaml(b"a: 123")
    assert value == {"a": 123}
    assert messages == []

    value, messages = validate_yaml('{"a" 1}')
    assert value is None
    assert messages == [
        Message(
            text="expected ',' or '}', but got '<scalar>'.",
            code="parse_error",
            position=Position(line_no=1, column_no=6, char_index=5),
        )
    ]

    validator = Object(properties=Integer())
    text = "a: 123\nb: abc\n"
    value, messages = validate_yaml(text, validator=validator)
    assert value is None
    assert messages == [
        Message(
            text="Must be a number.",
            code="type",
            index=["b"],
            start_position=Position(line_no=2, column_no=4, char_index=10),
            end_position=Position(line_no=2, column_no=6, char_index=12),
        )
    ]

    validator = Object(properties=Integer())
    text = "a: 123\nb: 456\n"
    value, messages = validate_yaml(text, validator=validator)
    assert value == {"a": 123, "b": 456}
    assert messages == []

    class Validator(Schema):
        a = Integer()
        b = Integer()

    text = "a: 123\nb: abc\n"
    value, messages = validate_yaml(text, validator=Validator)
    assert value is None
    assert messages == [
        Message(
            text="Must be a number.",
            code="type",
            index=["b"],
            start_position=Position(line_no=2, column_no=4, char_index=10),
            end_position=Position(line_no=2, column_no=6, char_index=12),
        )
    ]

    text = "a: 123"
    value, messages = validate_yaml(text, validator=Validator)
    assert value is None
    assert messages == [
        Message(
            text="The field 'b' is required.",
            code="required",
            index=["b"],
            start_position=Position(line_no=1, column_no=1, char_index=0),
            end_position=Position(line_no=1, column_no=6, char_index=5),
        )
    ]
