try:
    import jinja2
except ImportError:  # pragma: no cover
    jinja2 = None  # type: ignore

from typesystem import validators


class FormBase:
    renderer = None
    schema = None

    def __init__(self, values=None, errors=None):
        self.values = values or {}
        self.errors = errors or {}

    def __str__(self):
        return self.__html__()

    def __html__(self):
        assert self.schema is not None
        return self.renderer.render_form(
            self.schema, values=self.values, errors=self.errors
        )


class Jinja2Forms:
    def __init__(self, package="typesystem"):
        assert jinja2 is not None, "jinja2 must be installed to use Jinja2Forms"
        self.env = self.get_env(package)
        self.Form = type("Form", (FormBase,), {"renderer": self})

    def get_env(self, package) -> "jinja2.Environment":
        loader = jinja2.PackageLoader(package, "templates")
        env = jinja2.Environment(loader=loader, autoescape=True)
        return env

    def render_form(self, type, values, errors):
        template = self.env.get_template("form.html")
        html = template.render(
            {
                "type": type,
                "render_field": self.render_field,
                "values": values,
                "errors": errors,
            }
        )
        return jinja2.Markup(html)

    def render_field(self, key, validator):
        label = validator.title or key
        required = not validator.has_default()
        template_name = self.template_for_field(validator)
        template = self.env.get_template(template_name)
        html = template.render(
            {"key": key, "validator": validator, "label": label, "required": required}
        )
        return jinja2.Markup(html)

    def template_for_field(self, validator):
        if getattr(validator, "enum", None):
            return "inputs/select.html"
        elif isinstance(validator, validators.Boolean):
            return "inputs/checkbox.html"
        if isinstance(validator, validators.String) and validator.format == "text":
            return "inputs/textarea.html"
        return "inputs/input.html"
