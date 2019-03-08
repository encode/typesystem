import typing

from typesystem.base import Position


class Token:
    def __init__(
        self, value: typing.Any, start_index: int, end_index: int, content: str = ""
    ) -> None:
        self._value = value
        self._start_index = start_index
        self._end_index = end_index
        self._content = content

    def _get_value(self) -> typing.Any:
        raise NotImplementedError  # pragma: nocover

    def _get_child_token(self, key: typing.Any) -> "Token":
        raise NotImplementedError  # pragma: nocover

    def _get_key_token(self, key: typing.Any) -> "Token":
        raise NotImplementedError  # pragma: nocover

    @property
    def string(self) -> str:
        return self._content[self._start_index : self._end_index + 1]

    @property
    def value(self) -> typing.Any:
        return self._get_value()

    @property
    def start(self) -> Position:
        return self._get_position(self._start_index)

    @property
    def end(self) -> Position:
        return self._get_position(self._end_index)

    def lookup(self, index: list) -> "Token":
        """
        Given an index, lookup a child token within this structure.
        """
        token = self
        for key in index:
            token = token._get_child_token(key)
        return token

    def lookup_key(self, index: list) -> "Token":
        """
        Given an index, lookup a token for a dictionary key within this structure.
        """
        token = self.lookup(index[:-1])
        return token._get_key_token(index[-1])

    def _get_position(self, index: int) -> Position:
        content = self._content[: index + 1]
        lines = content.splitlines()
        line_no = max(len(lines), 1)
        column_no = 1 if not lines else max(len(lines[-1]), 1)
        return Position(line_no, column_no, index)

    def __repr__(self) -> str:
        return "%s(%s)" % (self.__class__.__name__, repr(self.string))

    def __eq__(self, other: typing.Any) -> bool:
        return isinstance(other, Token) and (
            self._get_value() == other._get_value()
            and self._start_index == other._start_index
            and self._end_index == other._end_index
        )


class ScalarToken(Token):
    def __hash__(self) -> typing.Any:
        return hash(self._value)

    def _get_value(self) -> typing.Any:
        return self._value


class DictToken(Token):
    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self._child_keys = {k._value: k for k in self._value.keys()}
        self._child_tokens = {k._value: v for k, v in self._value.items()}

    def _get_value(self) -> typing.Any:
        return {
            key_token._get_value(): value_token._get_value()
            for key_token, value_token in self._value.items()
        }

    def _get_child_token(self, key: typing.Any) -> Token:
        return self._child_tokens[key]

    def _get_key_token(self, key: typing.Any) -> Token:
        return self._child_keys[key]


class ListToken(Token):
    def _get_value(self) -> typing.Any:
        return [token._get_value() for token in self._value]

    def _get_child_token(self, key: typing.Any) -> Token:
        return self._value[key]
