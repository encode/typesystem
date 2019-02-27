import typing
from collections.abc import Mapping


class ErrorMessage:
    def __init__(
        self, *, text: str, code: str, index: typing.List[typing.Union[str, int]] = None
    ):
        self.text = text
        self.code = code
        self.index = [] if index is None else index

    def __eq__(self, other):
        if isinstance(other, str):
            return self.code == other

        return isinstance(other, ErrorMessage) and (
            self.text == other.text
            and self.code == other.code
            and self.index == other.index
        )

    def with_index_prefix(self, *, prefix: typing.Union[str, int]):
        index = [prefix] + self.index
        return ErrorMessage(text=self.text, code=self.code, index=index)


class ErrorMessages(Mapping):
    def __init__(self, messages: typing.List[ErrorMessage] = None):
        self._messages = [] if messages is None else messages

    def __iter__(self):
        return iter(self._messages)

    def __bool__(self):
        return bool(self._messages)

    def __len__(self):
        return len(self._messages)

    def __eq__(self, other):
        return list(self) == list(other)

    def __getitem__(self, key):
        if not hasattr(self, "_message_dict"):
            self._message_dict = self.to_dict(style="text")
        return self._message_dict[key]

    def keys(self):
        if not hasattr(self, "_message_dict"):
            self._message_dict = self.to_dict(style="text")
        return self._message_dict.keys()

    def to_dict(self, *, style: str):
        assert style in ("code", "text", "full")

        get_value = {
            "code": lambda message: message.code,
            "text": lambda message: message.text,
            "full": lambda message: message,
        }[style]

        result = {}
        for message in self._messages:
            insert_into = result
            for key in message.index[:-1]:
                insert_into = insert_into.setdefault(key, {})
            insert_key = message.index[-1] if message.index else ""
            insert_into[insert_key] = get_value(message)
        return result


class ValidationResult:
    def __init__(self, value, errors: ErrorMessages = None):
        self.value = value
        self.errors = ErrorMessages() if errors is None else errors

    def __iter__(self):
        yield self.value
        yield self.errors

    def __bool__(self):
        return not self.errors

    @property
    def is_valid(self):
        return not self.errors
