from typesystem.forms import Jinja2Forms
from typesystem.types import Type
from typesystem.validators import Boolean, String, Text


class Contact(Type):
    a = Boolean()
    b = String(max_length=10)
    c = Text()
    d = Text(enum=["abc", "def", "ghi"])


def test_forms():
    forms = Jinja2Forms()

    html = forms.render_form(Contact)

    assert html
