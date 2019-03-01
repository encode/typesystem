import typing
from collections.abc import Mapping


class Message:
    def __init__(self, *, text: str, code: str, index: list = None):
        self.text = text
        self.code = code
        self.index = [] if index is None else index

    def __eq__(self, other: typing.Any) -> bool:
        return isinstance(other, Message) and (
            self.text == other.text
            and self.code == other.code
            and self.index == other.index
        )

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        if self.index:
            return f"{class_name}(text={self.text!r}, code={self.code!r}, index={self.index!r})"
        return f"{class_name}(text={self.text!r}, code={self.code!r})"


class ValidationError(Mapping, Exception):
    def __init__(
        self,
        messages: typing.List[Message] = None,
        *,
        text: str = None,
        code: str = None,
    ):
        if messages is None:
            # Instantiated as a ValidationError with a single error message.
            assert text is not None
            assert code is not None
            messages = [Message(text=text, code=code)]
        else:
            # Instantiated as a ValidationError with multiple error messages.
            assert text is None
            assert code is None

        self._messages = messages
        self._message_dict = (
            {}
        )  # type: typing.Dict[typing.Any, typing.Union[str, dict]]

        # Populate 'self._message_dict'
        for message in messages:
            insert_into = self._message_dict
            for key in message.index[:-1]:
                insert_into = insert_into.setdefault(key, {})  # type: ignore
            insert_key = message.index[-1] if message.index else ""
            insert_into[insert_key] = message.text

    def messages(
        self, *, add_prefix: typing.Union[str, int] = None
    ) -> typing.List[Message]:
        if add_prefix is not None:
            return [
                Message(
                    text=message.text,
                    code=message.code,
                    index=[add_prefix] + message.index,
                )
                for message in self._messages
            ]
        return list(self._messages)

    def __iter__(self) -> typing.Iterator:
        return iter(self._message_dict)

    def __len__(self) -> int:
        return len(self._message_dict)

    def __getitem__(self, key: typing.Any) -> typing.Union[str, dict]:
        return self._message_dict[key]

    def __eq__(self, other: typing.Any) -> bool:
        return isinstance(other, ValidationError) and self._messages == other._messages

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        if len(self._messages) == 1 and not self._messages[0].index:
            message = self._messages[0]
            return f"{class_name}(text={message.text!r}, code={message.code!r})"
        return f"{class_name}({self._messages!r})"


class ValidationResult:
    def __init__(
        self, *, value: typing.Any = None, error: ValidationError = None
    ) -> None:
        self.value = value
        self.error = error

    def __iter__(self) -> typing.Iterator:
        yield self.value
        yield self.error

    def __bool__(self) -> bool:
        return self.error is None

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        if self.error is not None:
            return f"{class_name}(error={self.error!r})"
        return f"{class_name}(value={self.value!r})"
