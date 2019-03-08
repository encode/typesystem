import typing
from collections.abc import MutableMapping

from typesystem.fields import Array, Field, Nested, Object


class SchemaNamespace(MutableMapping):
    def __init__(self) -> None:
        self._namespace = {}  # type: dict

    def __getitem__(self, key: typing.Any) -> typing.Any:
        return self._namespace[key]

    def __iter__(self) -> typing.Iterator[typing.Any]:
        return iter(self._namespace)

    def __len__(self) -> int:
        return len(self._namespace)

    def __setitem__(self, key: typing.Any, value: typing.Any) -> None:
        self._namespace[key] = value

    def __delitem__(self, key: typing.Any) -> None:
        del self._namespace[key]


def set_namespace(field: Field, namespace: SchemaNamespace) -> None:
    """
    Recursively set the namespace that string-referenced `Nested` fields
    should use.
    """
    if (
        isinstance(field, Nested)
        and isinstance(field.schema, str)
        and field.namespace is None
    ):
        field.namespace = namespace
    elif isinstance(field, Array):
        if field.items is not None:
            if isinstance(field.items, (tuple, list)):
                for child in field.items:
                    set_namespace(child, namespace)
            else:
                set_namespace(field.items, namespace)
    elif isinstance(field, Object):
        for child in field.properties.values():
            set_namespace(child, namespace)
