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
        return isinstance(other, ErrorMessage) and (
            self.text == other.text
            and self.code == other.code
            and self.index == other.index
        )

    def with_index_prefix(self, *, prefix: typing.Union[str, int]):
        index = [prefix] + self.index
        return ErrorMessage(text=self.text, code=self.code, index=index)


class ValidationError(Mapping):
    def __init__(
        self,
        *,
        text: str = None,
        code: str = None,
        messages: typing.List[ErrorMessage] = None
    ):
        if messages is None:
            # Instantiated as a ValidationError with a single error message.
            assert text is not None
            assert code is not None
            messages = [ErrorMessage(text=text, code=code)]
        else:
            # Instantiated as a ValidationError with multiple error messages.
            assert text is None
            assert code is None

        self._messages = messages
        self._message_dict = {}

        # Populate 'self._message_dict'
        for message in messages:
            insert_into = self._message_dict
            for key in message.index[:-1]:
                insert_into = insert_into.setdefault(key, {})
            insert_key = message.index[-1] if message.index else ""
            insert_into[insert_key] = message.text

    def messages(self):
        return list(self._messages)

    def __iter__(self):
        return iter(self._message_dict)

    def __len__(self):
        return len(self._message_dict)

    def __getitem__(self, key):
        return self._message_dict[key]

    def __eq__(self, other):
        return isinstance(other, ValidationError) and self._messages == other._messages


class ValidationResult:
    def __init__(self, value, errors: ValidationError):
        self.value = value
        self.errors = errors

    @property
    def error(self):
        return self.errors

    def __iter__(self):
        yield self.value
        yield self.errors

    def __bool__(self):
        return not self.errors

    @property
    def is_valid(self):
        return not self.errors
