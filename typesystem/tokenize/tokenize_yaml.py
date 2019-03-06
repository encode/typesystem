try:
    import yaml
    from yaml.loader import SafeLoader
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore
    SafeLoader = None  # type: ignore

import typing

from typesystem.base import Message, Position
from typesystem.fields import Field
from typesystem.schemas import Schema
from typesystem.tokenize.tokens import DictToken, ListToken, ScalarToken, Token


def _get_position(content: str, index: int) -> Position:
    return Position(
        line_no=content.count("\n", 0, index) + 1,
        column_no=index - content.rfind("\n", 0, index),
        char_index=index,
    )


def tokenize_yaml(content: str) -> Token:
    assert yaml is not None, "'pyyaml' must be installed."

    class CustomSafeLoader(SafeLoader):
        pass

    def construct_mapping(loader: "yaml.Loader", node: "yaml.Node") -> DictToken:
        start = node.start_mark.index
        end = node.end_mark.index
        mapping = loader.construct_mapping(node)
        return DictToken(mapping, start, end - 1, content=content)

    def construct_sequence(loader: "yaml.Loader", node: "yaml.Node") -> ListToken:
        start = node.start_mark.index
        end = node.end_mark.index
        value = loader.construct_sequence(node)
        return ListToken(value, start, end - 1, content=content)

    def construct_scalar(loader: "yaml.Loader", node: "yaml.Node") -> ScalarToken:
        start = node.start_mark.index
        end = node.end_mark.index
        value = loader.construct_scalar(node)
        return ScalarToken(value, start, end - 1, content=content)

    def construct_int(loader: "yaml.Loader", node: "yaml.Node") -> ScalarToken:
        start = node.start_mark.index
        end = node.end_mark.index
        value = loader.construct_yaml_int(node)
        return ScalarToken(value, start, end - 1, content=content)

    def construct_float(loader: "yaml.Loader", node: "yaml.Node") -> ScalarToken:
        start = node.start_mark.index
        end = node.end_mark.index
        value = loader.construct_yaml_float(node)
        return ScalarToken(value, start, end - 1, content=content)

    def construct_bool(loader: "yaml.Loader", node: "yaml.Node") -> ScalarToken:
        start = node.start_mark.index
        end = node.end_mark.index
        value = loader.construct_yaml_bool(node)
        return ScalarToken(value, start, end - 1, content=content)

    def construct_null(loader: "yaml.Loader", node: "yaml.Node") -> ScalarToken:
        start = node.start_mark.index
        end = node.end_mark.index
        value = loader.construct_yaml_null(node)
        return ScalarToken(value, start, end - 1, content=content)

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

    return yaml.load(content, CustomSafeLoader)


def validate_yaml(
    content: typing.Union[str, bytes],
    validator: typing.Union[Field, typing.Type[Schema]] = None,
) -> typing.Tuple[typing.Any, typing.List[Message]]:
    """
    Parse and validate a YAML string, returning positionally marked error
    messages on parse or validation failures.

    content - A YAML string or bytestring.
    validator - A Field instance or Schema class to validate against.

    Returns a two-tuple of (value, error_messages)
    """
    assert yaml is not None, "'pyyaml' must be installed."

    if isinstance(content, bytes):
        content = content.decode("utf-8", "ignore")

    if not content.strip():
        # Handle the empty string case explicitly for clear error messaging.
        position = Position(column_no=1, line_no=1, char_index=0)
        message = Message(
            text="No content.", code="no_content", index=None, position=position
        )
        return (None, [message])

    try:
        root_token = tokenize_yaml(content)
    except (yaml.scanner.ScannerError, yaml.parser.ParserError) as exc:  # type: ignore
        # Handle cases that result in a YAML parse error.
        position = _get_position(content, index=exc.problem_mark.index)
        message = Message(
            text=exc.problem + ".", code="parse_error", index=None, position=position
        )
        return (None, [message])

    if validator is None:
        return (root_token.value, [])

    value, error = validator.validate_or_error(root_token.value)
    if error:
        messages = []
        for message in error.messages():
            if message.code == "required":
                token = root_token.lookup(message.index[:-1])
                text = "The field '%s' is required." % message.index[-1]
            else:
                text = message.text
                token = root_token.lookup(message.index)

            positional_message = Message(
                text=text,
                code=message.code,
                index=message.index,
                start_position=token.start,
                end_position=token.end,
            )
            messages.append(positional_message)
        messages = sorted(
            messages, key=lambda m: m.start_position.char_index  # type: ignore
        )
        return (None, messages)
    return (value, [])
