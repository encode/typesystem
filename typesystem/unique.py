import typing


class Uniqueness:
    """
    A set-like class that tests for uniqueness of primitive types.
    Ensures the `True` and `False` are treated as distinct from `1` and `0`,
    and coerces non-hashable instances that cannot be added to sets,
    into hashable representations that can.
    """

    TRUE = object()
    FALSE = object()

    def __init__(self, items: list = None) -> None:
        self._set: set = set()
        for item in items or []:
            self.add(item)

    def __contains__(self, item: typing.Any) -> bool:
        item = self.make_hashable(item)
        return item in self._set

    def add(self, item: typing.Any) -> None:
        item = self.make_hashable(item)
        self._set.add(item)

    def make_hashable(self, element: typing.Any) -> typing.Any:
        """
        Coerce a primitive into a uniquely hashable type, for uniqueness checks.
        """

        # Only primitive types can be handled.
        assert (element is None) or isinstance(
            element, (bool, int, float, str, list, dict)
        )

        if element is True:
            # Need to make `True` distinct from `1`.
            return self.TRUE
        elif element is False:
            # Need to make `False` distinct from `0`.
            return self.FALSE
        elif isinstance(element, list):
            # Represent lists using a two-tuple of ('list', (item, item, ...))
            return ("list", tuple([self.make_hashable(item) for item in element]))
        elif isinstance(element, dict):
            # Represent dicts using a two-tuple of ('dict', ((key, val), (key, val), ...))
            return (
                "dict",
                tuple(
                    [
                        (self.make_hashable(key), self.make_hashable(value))
                        for key, value in element.items()
                    ]
                ),
            )

        return element
