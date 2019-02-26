from typesystem.forms import Jinja2Forms
from typesystem.schemas import Schema
from typesystem.validators import Boolean, String, Text


class Contact(Schema):
    a = Boolean()
    b = String(max_length=10)
    c = Text()
    d = Text(enum=["abc", "def", "ghi"])


forms = Jinja2Forms()


def test_forms():
    class ContactForm(forms.Form):
        schema = Contact

    html = str(ContactForm())

    assert html
