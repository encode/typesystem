import jinja2

from typesystem.forms import Jinja2Forms
from typesystem.schemas import Schema
from typesystem.validators import Boolean, Choice, String, Text


class Contact(Schema):
    a = Boolean()
    b = String(max_length=10)
    c = Text()
    d = Choice(choices=["abc", "def", "ghi"])


forms = Jinja2Forms()


def test_form_rendering():
    form = forms.Form(Contact)

    html = str(form)

    assert html.count('<input type="checkbox" ') == 1
    assert html.count('<input type="text" ') == 1
    assert html.count("<textarea ") == 1
    assert html.count("<select ") == 1


def test_form_html():
    form = forms.Form(Contact)

    markup = form.__html__()

    assert isinstance(markup, jinja2.Markup)
    assert str(markup) == str(form)
