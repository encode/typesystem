# The following fields are required for complete JSON schema support,
# but are undocumented as we don't recommend using them directly.
import typing

from typesystem.fields import Any, Field


class NeverMatch(Field):
    """
    Doesn't ever match.
    """

    errors = {"never": "This never validates."}

    def __init__(self, **kwargs: typing.Any) -> None:
        assert "allow_null" not in kwargs
        super().__init__(**kwargs)

    def validate(self, value: typing.Any, strict: bool = False) -> typing.Any:
        raise self.validation_error("never")


class OneOf(Field):
    """
    Must match exactly one of the sub-items.

    You'll almost always want to just use `Union` instead of this, which is an
    "anyOf" test.
    """

    errors = {
        "no_match": "Did not match any valid type.",
        "multiple_matches": "Matched more than one type.",
    }

    def __init__(self, one_of: typing.List[Field], **kwargs: typing.Any) -> None:
        assert "allow_null" not in kwargs
        super().__init__(**kwargs)
        self.one_of = one_of

    def validate(self, value: typing.Any, strict: bool = False) -> typing.Any:
        candidate = None
        match_count = 0
        for child in self.one_of:
            validated, error = child.validate_or_error(value, strict=strict)
            if error is None:
                match_count += 1
                candidate = validated

        if match_count == 1:
            return candidate
        elif match_count > 1:
            raise self.validation_error("multiple_matches")
        raise self.validation_error("no_match")


class AllOf(Field):
    """
    Must match all of the sub-items.

    You should instead consolidate into a single type, or use
    schema inheritence instead of this.
    """

    def __init__(self, all_of: typing.List[Field], **kwargs: typing.Any) -> None:
        assert "allow_null" not in kwargs
        super().__init__(**kwargs)
        self.all_of = all_of

    def validate(self, value: typing.Any, strict: bool = False) -> typing.Any:
        for child in self.all_of:
            child.validate(value, strict=strict)
        return value


class Not(Field):
    """
    Must match all of the sub-items.

    You should use custom validation instead.
    """

    errors = {"negated": "Must not match."}

    def __init__(self, negated: Field, **kwargs: typing.Any) -> None:
        assert "allow_null" not in kwargs
        super().__init__(**kwargs)
        self.negated = negated

    def validate(self, value: typing.Any, strict: bool = False) -> typing.Any:
        _, error = self.negated.validate_or_error(value, strict=strict)
        if error:
            return value
        raise self.validation_error("negated")


class IfThenElse(Field):
    """
    Conditional sub-item matching.

    You should use custom validation instead.
    """

    def __init__(
        self,
        if_clause: Field,
        then_clause: Field = None,
        else_clause: Field = None,
        **kwargs: typing.Any
    ) -> None:
        assert "allow_null" not in kwargs
        super().__init__(**kwargs)
        self.if_clause = if_clause
        self.then_clause = Any() if then_clause is None else then_clause
        self.else_clause = Any() if else_clause is None else else_clause

    def validate(self, value: typing.Any, strict: bool = False) -> typing.Any:
        _, error = self.if_clause.validate_or_error(value, strict=strict)
        if error is None:
            return self.then_clause.validate(value, strict=strict)
        else:
            return self.else_clause.validate(value, strict=strict)
