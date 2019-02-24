import pytest

from typesystem.types import Type
from typesystem.validators import Integer, String


class Person(Type):
    name = String(max_length=100, allow_blank=False)
    age = Integer()


class Product(Type):
    name = String(max_length=100, allow_blank=False)
    rating = Integer(default=None)


def test_type_validation():
    validated = Person.validate({"name": "Tom", "age": "123"})
    assert validated.value == Person(name="Tom", age=123)

    validated = Person.validate({"name": "Tom", "age": "123"})
    assert validated.value == Person(name="Tom", age=123)

    validated = Person.validate({"name": "Tom", "age": "abc"})
    assert dict(validated.errors) == {"age": "Must be a number."}

    validated = Person.validate({"name": "Tom"})
    assert dict(validated.errors) == {"age": 'The "age" field is required.'}


def test_type_eq():
    tom = Person(name="Tom", age=123)
    lucy = Person(name="Lucy", age=123)
    assert tom != lucy

    tom = Person(name="Tom", age=123)
    tshirt = Product(name="T-Shirt")
    assert tom != tshirt


def test_type_instantiation():
    tshirt = Product(name="T-Shirt")
    assert tshirt.name == "T-Shirt"
    assert tshirt.rating == None

    with pytest.raises(TypeError):
        Product()

    with pytest.raises(TypeError):
        Product(name="T-Shirt", other="Invalid")
