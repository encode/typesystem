import datetime

import pytest

from typesystem.schemas import Schema
from typesystem.validators import Date, Integer, String, Text


class Person(Schema):
    name = String(max_length=100, allow_blank=False)
    age = Integer()


class Product(Schema):
    name = String(max_length=100, allow_blank=False)
    rating = Integer(default=None)


def test_schema_validation():
    validated = Person.validate({"name": "Tom", "age": "123"})
    assert validated.value == Person(name="Tom", age=123)

    validated = Person.validate({"name": "Tom", "age": "123"})
    assert validated.value == Person(name="Tom", age=123)

    validated = Person.validate({"name": "Tom", "age": "abc"})
    assert dict(validated.errors) == {"age": "Must be a number."}

    validated = Person.validate({"name": "Tom"})
    assert dict(validated.errors) == {"age": "This field is required."}


def test_schema_eq():
    tom = Person(name="Tom", age=123)
    lucy = Person(name="Lucy", age=123)
    assert tom != lucy

    tom = Person(name="Tom", age=123)
    tshirt = Product(name="T-Shirt")
    assert tom != tshirt


def test_schema_instantiation():
    tshirt = Product(name="T-Shirt")
    assert tshirt.name == "T-Shirt"
    assert tshirt.rating == None

    empty = Product()
    assert not hasattr(empty, "name")

    with pytest.raises(TypeError):
        Product(name="T-Shirt", other="Invalid")


def test_schema_subclass():
    class DetailedProduct(Product):
        info = Text()

    assert set(DetailedProduct.fields.keys()) == {"name", "rating", "info"}


def test_schema_serialization():
    tshirt = Product(name="T-Shirt")

    data = dict(tshirt)

    assert data == {"name": "T-Shirt", "rating": None}


def test_schema_len():
    tshirt = Product(name="T-Shirt")

    count = len(tshirt)

    assert count == 2


def test_schema_getattr():
    tshirt = Product(name="T-Shirt")
    assert tshirt["name"] == "T-Shirt"


def test_schema_missing_getattr():
    tshirt = Product(name="T-Shirt")

    with pytest.raises(KeyError):
        assert tshirt["missing"]


def test_schema_format_serialization():
    class BlogPost(Schema):
        text = String()
        created = Date()

    post = BlogPost(text="Hi", created=datetime.date.today())

    data = dict(post)

    assert data["text"] == "Hi"
    assert data["created"] == datetime.date.today().isoformat()
