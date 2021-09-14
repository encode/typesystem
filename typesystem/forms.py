try:
    import jinja2
    import markupsafe
except ImportError:  # pragma: no cover
    jinja2 = None  # type: ignore

import typing

from typesystem.fields import Boolean, Choice, Field, Object, String
from typesystem.schemas import Schema


class Form:
    # Does not include "checkbox", "radio", "file", "image", "reset", "submit", "button"
    FORMAT_TO_INPUTTYPE = {
        "color": "color",
        "datetime": "datetime-local",
        "date": "date",
        "email": "email",
        "hidden": "hidden",
        "month": "month",
        "number": "number",
        "password": "password",
        "range": "range",
        "search": "search",
        "tel": "tel",
        "text": "text",
        "time": "time",
        "url": "url",
        "week": "week",
    }

    def __init__(
        self,
        *,
        env: "jinja2.Environment",
        schema: Schema,
        values: typing.Dict[str, typing.Any] = None,
    ) -> None:
        self.env = env
        self.schema = schema
        self.values = self.schema.serialize(values)
        self.errors: typing.Optional[typing.Dict[str, typing.Any]] = None
        self._validate_called = False

    def validate(self, data: dict = None) -> None:
        assert not self._validate_called, "validate() has already been called."
        self.data = data
        self.values, self.errors = self.schema.validate_or_error(data)
        self._validate_called = True

    @property
    def is_valid(self) -> bool:
        assert self._validate_called, "validate() has not been called."
        return self.errors is None

    @property
    def validated_data(self) -> typing.Any:
        return self.values

    def render_fields(self) -> str:
        values = self.data if self.errors else self.values
        errors = self.errors

        html = ""
        for field_name, field in self.schema.fields.items():
            if field.read_only:
                continue
            value = None if values is None else values.get(field_name)
            error = None if errors is None else errors.get(field_name)
            html += self.render_field(
                field_name=field_name, field=field, value=value, error=error
            )
        return html

    def render_field(
        self,
        *,
        field_name: str,
        field: Field,
        value: typing.Any = None,
        error: str = None,
    ) -> str:
        field_id = field_name.replace("_", "-")
        label = field.title or field_name
        allow_empty = field.allow_null or getattr(field, "allow_blank", False)
        required = not field.has_default() and not allow_empty
        input_type = self.input_type_for_field(field)
        template_name = self.template_for_field(field)
        template = self.env.get_template(template_name)
        value = "" if input_type == "password" else value
        return template.render(
            {
                "field_id": field_id,
                "field_name": field_name,
                "field": field,
                "label": label,
                "required": required,
                "input_type": input_type,
                "value": value,
                "error": error,
            }
        )

    def template_for_field(self, field: Field) -> str:
        assert not isinstance(
            field, Object
        ), "Forms do not support rendering Object fields"

        if isinstance(field, Choice):
            return "forms/select.html"
        elif isinstance(field, Boolean):
            return "forms/checkbox.html"
        if isinstance(field, String) and field.format == "text":
            return "forms/textarea.html"
        return "forms/input.html"

    def input_type_for_field(self, field: Field) -> str:
        format = getattr(field, "format", None)
        if not format:
            return "text"
        return self.FORMAT_TO_INPUTTYPE.get(format, "text")

    def __str__(self) -> str:
        return self.render_fields()

    def __html__(self) -> "markupsafe.Markup":
        return markupsafe.Markup(self.render_fields())


class Jinja2Forms:
    def __init__(self, *, directory: str = None, package: str = None) -> None:
        assert jinja2 is not None, "jinja2 must be installed to use Jinja2Forms."
        assert (
            directory is not None or package is not None
        ), "Either 'directory' or 'package' must be specified."
        self.env = self.load_template_env(directory=directory, package=package)

    def load_template_env(
        self, *, directory: str = None, package: str = None
    ) -> "jinja2.Environment":
        if directory is not None and package is None:
            loader: jinja2.BaseLoader = jinja2.FileSystemLoader(directory)
        elif directory is None and package is not None:
            loader = jinja2.PackageLoader(package, "templates")
        else:
            assert directory is not None
            assert package is not None
            loader = jinja2.ChoiceLoader(
                [
                    jinja2.FileSystemLoader(directory),
                    jinja2.PackageLoader(package, "templates"),
                ]
            )
        return jinja2.Environment(loader=loader, autoescape=True)

    def create_form(
        self, schema: Schema, values: typing.Dict[str, typing.Any] = None
    ) -> Form:
        return Form(env=self.env, schema=schema, values=values)
