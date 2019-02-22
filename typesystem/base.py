import typing


class ErrorMessage:
    def __init__(self, *, text: str, code: str, index: typing.List[typing.Union[str, int]]=None):
        self.text = text
        self.code = code
        self.index = [] if index is None else index

    def __eq__(self, other):
        if isinstance(other, str):
            return self.code == other

        return isinstance(other, ErrorMessage) and (
            self.text == other.text and
            self.code == other.code and
            self.index == other.index
        )

    def with_index_prefix(self, *, prefix: typing.Union[str, int]):
        index = [prefix] + self.index
        return ErrorMessage(text=self.text, code=self.code, index=index)


class ErrorMessages:
    def __init__(self, messages: typing.List[ErrorMessage] = None):
        self.messages = [] if messages is None else messages

    def __iter__(self):
        return iter(self.messages)

    def __bool__(self):
        return bool(self.messages)

    def __eq__(self, other):
        return list(self) == list(other)

    def to_dict(self):
        result = {}
        for message in self.messages:
            insert_into = result
            for key in message.index[:-1]:
                insert_into = insert_into.setdefault(key, {})
            insert_key = message.index[-1] if message.index else ''
            insert_into[insert_key] = message.code
        return result


class ValidationResult:
    def __init__(self, value, errors: ErrorMessages=None):
        self.value = value
        self.errors = ErrorMessages() if errors is None else errors

    def __bool__(self):
        return not self.errors

    @property
    def is_valid(self):
        return not self.errors
