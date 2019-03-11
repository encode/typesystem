import typing
from collections.abc import MutableMapping

from typesystem.fields import Array, Field, Object, Reference


class SchemaDefinitions(MutableMapping):
    def __init__(self) -> None:
        self._definitions = {}  # type: dict

    def __getitem__(self, key: typing.Any) -> typing.Any:
        return self._definitions[key]

    def __iter__(self) -> typing.Iterator[typing.Any]:
        return iter(self._definitions)

    def __len__(self) -> int:
        return len(self._definitions)

    def __setitem__(self, key: typing.Any, value: typing.Any) -> None:
        self._definitions[key] = value

    def __delitem__(self, key: typing.Any) -> None:
        del self._definitions[key]


def set_definitions(field: Field, definitions: SchemaDefinitions) -> None:
    """
    Recursively set the definitions that string-referenced `Reference` fields
    should use.
    """
    if (
        isinstance(field, Reference)
        and isinstance(field.to, str)
        and field.definitions is None
    ):
        field.definitions = definitions
    elif isinstance(field, Array):
        if field.items is not None:
            if isinstance(field.items, (tuple, list)):
                for child in field.items:
                    set_definitions(child, definitions)
            else:
                set_definitions(field.items, definitions)
    elif isinstance(field, Object):
        for child in field.properties.values():
            set_definitions(child, definitions)
