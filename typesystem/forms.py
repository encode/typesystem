try:
    import jinja2
except ImportError:  # pragma: no cover
    jinja2 = None  # type: ignore

from typesystem import validators


class Form:
    def __init__(self, env, schema, values=None, errors=None):
        self.env = env
        self.schema = schema
        self.values = values or {}
        self.errors = errors or {}

    def render_fields(self):
        html = ""
        for field_name, field in self.schema.fields.items():
            value = self.values.get(field_name)
            error = self.errors.get(field_name)
            html += self.render_field(field_name, field, value, error)
        return html

    def render_field(self, field_name, field, value, error):
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

    def template_for_field(self, field):
        if isinstance(field, validators.Choice):
            return "forms/select.html"
        elif isinstance(field, validators.Boolean):
            return "forms/checkbox.html"
        if isinstance(field, validators.String) and field.format == "text":
            return "forms/textarea.html"
        return "forms/input.html"

    def __str__(self):
        return self.render_fields()

    def __html__(self):
        return jinja2.Markup(self.render_fields())


class Jinja2Forms:
    form_class = Form

    def __init__(self, package="typesystem"):
        assert jinja2 is not None, "jinja2 must be installed to use Jinja2Forms"
        self.env = self.load_template_env(package)

    def load_template_env(self, package) -> "jinja2.Environment":
        loader = jinja2.PackageLoader(package, "templates")
        return jinja2.Environment(loader=loader, autoescape=True)

    def Form(self, schema, values=None, errors=None):
        return self.form_class(
            env=self.env, schema=schema, values=values, errors=errors
        )
