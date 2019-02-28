try:
    import jinja2
except ImportError:  # pragma: no cover
    jinja2 = None  # type: ignore

import typing

from typesystem.base import ValidationError
from typesystem.fields import Boolean, Choice, Field, Object, String
from typesystem.schemas import Schema


class Form:
    def __init__(
        self,
        env: "jinja2.Environment",
        schema: typing.Type[Schema],
        values: dict = None,
        errors: ValidationError = None,
    ) -> None:
        self.env = env
        self.schema = schema
        self.values = values
        self.errors = errors

    def render_fields(self) -> str:
        html = ""
        for field_name, field in self.schema.fields.items():
            value = None if self.values is None else self.values.get(field_name)
            error = None if self.errors is None else self.errors.get(field_name)
            html += self.render_field(field_name, field, value, error)
        return html

    def render_field(
        self, field_name: str, field: Field, value: typing.Any = None, error: str = None
    ) -> str:
        field_id = (
            "form-" + self.schema.__name__.lower() + "-" + field_name.replace("_", "-")
        )
        label = field.title or field_name
        allow_empty = field.allow_null or getattr(field, "allow_blank", False)
        required = not field.has_default() and not allow_empty
        template_name = self.template_for_field(field)
        template = self.env.get_template(template_name)
        return template.render(
            {
                "field_id": field_id,
                "field_name": field_name,
                "field": field,
                "label": label,
                "required": required,
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

    def __str__(self) -> str:
        return self.render_fields()

    def __html__(self) -> "jinja2.Markup":
        return jinja2.Markup(self.render_fields())


class Jinja2Forms:
    def __init__(self, directory: str = None, package: str = None) -> None:
        assert jinja2 is not None, "jinja2 must be installed to use Jinja2Forms."
        assert (
            directory is not None or package is not None
        ), "Either 'directory' or 'package' must be specified."
        self.env = self.load_template_env(directory, package)

    def load_template_env(
        self, directory: str = None, package: str = None
    ) -> "jinja2.Environment":
        if directory is not None and package is None:
            loader = jinja2.FileSystemLoader(directory)  # type: jinja2.BaseLoader
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

    def Form(
        self,
        schema: typing.Type[Schema],
        values: dict = None,
        errors: ValidationError = None,
    ) -> Form:  # type: ignore
        return Form(env=self.env, schema=schema, values=values, errors=errors)
