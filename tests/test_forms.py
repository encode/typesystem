import jinja2

import typesystem


class Contact(typesystem.Schema):
    a = typesystem.Boolean()
    b = typesystem.String(max_length=10)
    c = typesystem.Text()
    d = typesystem.Choice(choices=[("abc", "Abc"), ("def", "Def"), ("ghi", "Ghi")])


forms = typesystem.Jinja2Forms(package="typesystem")


def test_form_rendering():
    form = forms.Form(Contact)

    html = str(form)

    assert html.count('<input type="checkbox" ') == 1
    assert html.count('<input type="text" ') == 1
    assert html.count("<textarea ") == 1
    assert html.count("<select ") == 1


def test_password_rendering():
    class PasswordForm(typesystem.Schema):
        password = typesystem.String(format="password")

    form = forms.Form(PasswordForm, values={"password": "secret"})
    html = str(form)
    assert "secret" not in html


def test_form_html():
    form = forms.Form(Contact)

    markup = form.__html__()

    assert isinstance(markup, jinja2.Markup)
    assert str(markup) == str(form)


def test_forms_from_directory(tmpdir):
    forms = typesystem.Jinja2Forms(directory=str(tmpdir))
    assert isinstance(forms.env.loader, jinja2.FileSystemLoader)


def test_forms_with_directory_override(tmpdir):
    forms = typesystem.Jinja2Forms(directory=str(tmpdir), package="typesystem")
    assert isinstance(forms.env.loader, jinja2.ChoiceLoader)
