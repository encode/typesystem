import typing

from typesystem.base import Message, ValidationError
from typesystem.fields import Field
from typesystem.schemas import Schema
from typesystem.tokenize.tokens import Token


def validate_with_positions(
    *, token: Token, validator: typing.Union[Field, typing.Type[Schema]]
) -> typing.Any:
    try:
        return validator.validate(token.value)
    except ValidationError as error:
        messages = []
        for message in error.messages():
            if message.code == "required":
                field = message.index[-1]
                token = token.lookup(message.index[:-1])
                text = f"The field {field!r} is required."
            else:
                token = token.lookup(message.index)
                text = message.text

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
        raise ValidationError(messages=messages)
