import pytest

from typesystem import ParseError, tokenize_yaml
from typesystem.tokenize.tokens import DictToken, ListToken, ScalarToken

YAML_OBJECT = """
a:
  - 1
  - 2
  - 3
b: "test"
"""

YAML_LIST = """
- true
- false
- null
"""

YAML_FLOATS = """
- 100.0
- 1.0E+2
"""


def test_tokenize_object():
    token = tokenize_yaml(YAML_OBJECT)
    expected = DictToken(
        {
            ScalarToken("a", 1, 1): ListToken(
                [ScalarToken(1, 8, 8), ScalarToken(2, 14, 14), ScalarToken(3, 20, 20)],
                6,
                21,
            ),
            ScalarToken("b", 22, 22): ScalarToken("test", 25, 30),
        },
        1,
        31,
    )
    assert token == expected


def test_tokenize_list():
    token = tokenize_yaml(YAML_LIST)
    expected = ListToken(
        [
            ScalarToken(True, 3, 6),
            ScalarToken(False, 10, 14),
            ScalarToken(None, 18, 21),
        ],
        1,
        22,
    )
    assert token == expected


def test_tokenize_floats():
    token = tokenize_yaml(YAML_FLOATS)
    expected = ListToken([ScalarToken(100.0, 3, 7), ScalarToken(100.0, 11, 16)], 1, 17)
    assert token == expected


def test_tokenize_parse_errors():
    with pytest.raises(ParseError) as exc_info:
        tokenize_yaml(b"")
    exc = exc_info.value
    message = exc.messages()[0]
    assert message.text == "No content."
    assert message.start_position.char_index == 0

    with pytest.raises(ParseError) as exc_info:
        tokenize_yaml('{"a" 1}')
    exc = exc_info.value
    message = exc.messages()[0]
    assert message.text == "expected ',' or '}', but got '<scalar>'."
    assert message.start_position.char_index == 5
