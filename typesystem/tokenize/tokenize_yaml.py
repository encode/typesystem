try:
    import yaml
    from yaml.loader import SafeLoader
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore
    SafeLoader = None  # type: ignore

import typing

from typesystem.base import Message, ParseError, Position, ValidationError
from typesystem.fields import Field
from typesystem.schemas import Schema
from typesystem.tokenize.positional_validation import validate_with_positions
from typesystem.tokenize.tokens import DictToken, ListToken, ScalarToken, Token


def _get_position(content: str, index: int) -> Position:
    return Position(
        line_no=content.count("\n", 0, index) + 1,
        column_no=index - content.rfind("\n", 0, index),
        char_index=index,
    )


def tokenize_yaml(content: typing.Union[str, bytes]) -> Token:
    assert yaml is not None, "'pyyaml' must be installed."

    if isinstance(content, bytes):
        str_content = content.decode("utf-8", "ignore")
    else:
        str_content = content

    if not str_content.strip():
        # Handle the empty string case explicitly for clear error messaging.
        position = Position(column_no=1, line_no=1, char_index=0)
        raise ParseError(text="No content.", code="no_content", position=position)

    class CustomSafeLoader(SafeLoader):
        pass

    def construct_mapping(loader: "yaml.Loader", node: "yaml.Node") -> DictToken:
        start = node.start_mark.index
        end = node.end_mark.index
        mapping = loader.construct_mapping(node)
        return DictToken(mapping, start, end - 1, content=str_content)

    def construct_sequence(loader: "yaml.Loader", node: "yaml.Node") -> ListToken:
        start = node.start_mark.index
        end = node.end_mark.index
        value = loader.construct_sequence(node)
        return ListToken(value, start, end - 1, content=str_content)

    def construct_scalar(loader: "yaml.Loader", node: "yaml.Node") -> ScalarToken:
        start = node.start_mark.index
        end = node.end_mark.index
        value = loader.construct_scalar(node)
        return ScalarToken(value, start, end - 1, content=str_content)

    def construct_int(loader: "yaml.Loader", node: "yaml.Node") -> ScalarToken:
        start = node.start_mark.index
        end = node.end_mark.index
        value = loader.construct_yaml_int(node)
        return ScalarToken(value, start, end - 1, content=str_content)

    def construct_float(loader: "yaml.Loader", node: "yaml.Node") -> ScalarToken:
        start = node.start_mark.index
        end = node.end_mark.index
        value = loader.construct_yaml_float(node)
        return ScalarToken(value, start, end - 1, content=str_content)

    def construct_bool(loader: "yaml.Loader", node: "yaml.Node") -> ScalarToken:
        start = node.start_mark.index
        end = node.end_mark.index
        value = loader.construct_yaml_bool(node)
        return ScalarToken(value, start, end - 1, content=str_content)

    def construct_null(loader: "yaml.Loader", node: "yaml.Node") -> ScalarToken:
        start = node.start_mark.index
        end = node.end_mark.index
        value = loader.construct_yaml_null(node)
        return ScalarToken(value, start, end - 1, content=str_content)

    CustomSafeLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping
    )

    CustomSafeLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_SEQUENCE_TAG, construct_sequence
    )

    CustomSafeLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_SCALAR_TAG, construct_scalar
    )

    CustomSafeLoader.add_constructor("tag:yaml.org,2002:int", construct_int)

    CustomSafeLoader.add_constructor("tag:yaml.org,2002:float", construct_float)

    CustomSafeLoader.add_constructor("tag:yaml.org,2002:bool", construct_bool)

    CustomSafeLoader.add_constructor("tag:yaml.org,2002:null", construct_null)

    try:
        return yaml.load(str_content, CustomSafeLoader)
    except (yaml.scanner.ScannerError, yaml.parser.ParserError) as exc:  # type: ignore
        # Handle cases that result in a YAML parse error.
        text = exc.problem + "."
        position = _get_position(str_content, index=exc.problem_mark.index)
        raise ParseError(text=text, code="parse_error", position=position)


def validate_yaml(
    content: typing.Union[str, bytes],
    validator: typing.Union[Field, typing.Type[Schema]],
) -> typing.Any:
    """
    Parse and validate a YAML string, returning positionally marked error
    messages on parse or validation failures.

    content - A YAML string or bytestring.
    validator - A Field instance or Schema class to validate against.

    Returns a two-tuple of (value, error_messages)
    """
    assert yaml is not None, "'pyyaml' must be installed."

    token = tokenize_yaml(content)
    return validate_with_positions(token=token, validator=validator)
