import pytest

from typesystem import ParseError, tokenize_json
from typesystem.tokenize.tokens import DictToken, ListToken, ScalarToken


def test_tokenize_object():
    token = tokenize_json('{"a": [1, 2, 3], "b": "test"}')
    expected = DictToken(
        {
            ScalarToken("a", 1, 3): ListToken(
                [ScalarToken(1, 7, 7), ScalarToken(2, 10, 10), ScalarToken(3, 13, 13)],
                6,
                14,
            ),
            ScalarToken("b", 17, 19): ScalarToken("test", 22, 27),
        },
        0,
        28,
    )
    assert repr(token) == 'DictToken(\'{"a": [1, 2, 3], "b": "test"}\')'
    assert token == expected
    assert token.value == {"a": [1, 2, 3], "b": "test"}
    assert token.lookup(["a"]).value == [1, 2, 3]
    assert token.lookup(["a"]).string == "[1, 2, 3]"
    assert token.lookup(["a"]).start.line_no == 1
    assert token.lookup(["a"]).start.column_no == 7
    assert token.lookup_key(["a"]).value == "a"
    assert token.lookup_key(["a"]).string == '"a"'
    assert token.lookup_key(["a"]).start.char_index == 1
    assert token.lookup_key(["a"]).end.char_index == 3


def test_tokenize_list():
    token = tokenize_json("[true, false, null]")
    expected = ListToken(
        [ScalarToken(True, 1, 4), ScalarToken(False, 7, 11), ScalarToken(None, 14, 17)],
        0,
        18,
    )
    assert token == expected
    assert token.value == [True, False, None]
    assert token.lookup([0]).value is True
    assert token.lookup([0]).string == "true"
    assert token.lookup([0]).start.char_index == 1
    assert token.lookup([0]).end.char_index == 4


def test_tokenize_floats():
    token = tokenize_json("[100.0, 1.0E+2, 1E+2]")
    expected = ListToken(
        [
            ScalarToken(100.0, 1, 5),
            ScalarToken(100.0, 8, 13),
            ScalarToken(100.0, 16, 19),
        ],
        0,
        20,
    )
    assert token == expected
    assert token.value == [100.0, 1.0e2, 1e2]
    assert token.lookup([0]).value == 100.0
    assert token.lookup([0]).string == "100.0"
    assert token.lookup([0]).start.char_index == 1
    assert token.lookup([0]).end.char_index == 5


def test_tokenize_whitespace():
    token = tokenize_json("{ }")
    expected = DictToken({}, 0, 2)
    assert token == expected
    assert token.value == {}
    assert token.string == "{ }"

    token = tokenize_json('{ "a" :  1 }')
    expected = DictToken({ScalarToken("a", 2, 4): ScalarToken(1, 9, 9)}, 0, 11)
    assert token == expected
    assert token.value == {"a": 1}
    assert token.lookup(["a"]).value == 1
    assert token.lookup(["a"]).string == "1"
    assert token.lookup(["a"]).start.char_index == 9
    assert token.lookup(["a"]).end.char_index == 9
    assert token.lookup_key(["a"]).value == "a"
    assert token.lookup_key(["a"]).string == '"a"'
    assert token.lookup_key(["a"]).start.char_index == 2
    assert token.lookup_key(["a"]).end.char_index == 4


def test_tokenize_parse_errors():
    with pytest.raises(ParseError) as exc_info:
        tokenize_json(b"")
    exc = exc_info.value
    message = exc.messages()[0]
    assert message.text == "No content."
    assert message.start_position.char_index == 0
    assert (
        repr(message)
        == "Message(text='No content.', code='no_content', position=Position(line_no=1, column_no=1, char_index=0))"
    )

    with pytest.raises(ParseError) as exc_info:
        tokenize_json("{")
    exc = exc_info.value
    message = exc.messages()[0]
    assert message.text == "Expecting property name enclosed in double quotes."
    assert message.start_position.char_index == 1

    with pytest.raises(ParseError) as exc_info:
        tokenize_json('{"a"')
    exc = exc_info.value
    message = exc.messages()[0]
    assert message.text == "Expecting ':' delimiter."
    assert message.start_position.char_index == 4

    with pytest.raises(ParseError) as exc_info:
        tokenize_json('{"a":')
    exc = exc_info.value
    message = exc.messages()[0]
    assert message.text == "Expecting value."
    assert message.start_position.char_index == 5

    with pytest.raises(ParseError) as exc_info:
        tokenize_json('{"a":1')
    exc = exc_info.value
    message = exc.messages()[0]
    assert message.text == "Expecting ',' delimiter."
    assert message.start_position.char_index == 6

    with pytest.raises(ParseError) as exc_info:
        tokenize_json('{"a":1,1')
    exc = exc_info.value
    message = exc.messages()[0]
    assert message.text == "Expecting property name enclosed in double quotes."
    assert message.start_position.char_index == 7

    with pytest.raises(ParseError) as exc_info:
        tokenize_json('{"a":1 "b"')
    exc = exc_info.value
    message = exc.messages()[0]
    assert message.text == "Expecting ',' delimiter."
    assert message.start_position.char_index == 7

    with pytest.raises(ParseError) as exc_info:
        tokenize_json('{"a" 123}')
    exc = exc_info.value
    message = exc.messages()[0]
    assert message.text == "Expecting ':' delimiter."
    assert message.start_position.char_index == 5
