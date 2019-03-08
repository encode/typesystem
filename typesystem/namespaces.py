import typing
from collections.abc import MutableMapping

from typesystem.schemas import Schema


class SchemaNamespace(MutableMapping):
    def __init__(self) -> None:
        self._namespace = {}  # type: typing.Dict[str, typing.Type[Schema]]

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

    @property
    def Schema(self) -> typing.Type[Schema]:  # type: ignore
        return type("NamespacedSchema", (Schema,), {"namespace": self})
