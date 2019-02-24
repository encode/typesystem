try:
    import jinja2
except ImportError:  # pragma: no cover
    jinja2 = None  # type: ignore

from typesystem import validators


class Jinja2Forms:
    def __init__(self):
        assert jinja2 is not None, "jinja2 must be installed to use Jinja2Forms"
        self.env = self.get_env()

    def get_env(self) -> "jinja2.Environment":
        loader = jinja2.PackageLoader("typesystem", "templates")
        env = jinja2.Environment(loader=loader, autoescape=True)
        return env

    def render_form(self, type):
        template = self.env.get_template("form.html")
        return template.render({"type": type, "render_field": self.render_field})

    def render_field(self, key, validator):
        label = validator.title or key
        required = not validator.has_default()
        template_name = self.template_for_field(validator)
        template = self.env.get_template(template_name)
        return template.render(
            {"key": key, "validator": validator, "label": label, "required": required}
        )

    def template_for_field(self, validator):
        if getattr(validator, "enum", None):
            return "inputs/select.html"
        elif isinstance(validator, validators.Boolean):
            return "inputs/checkbox.html"
        if isinstance(validator, validators.String) and validator.format == "textarea":
            return "inputs/textarea.html"
        return "inputs/input.html"
