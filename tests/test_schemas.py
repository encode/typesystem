import datetime
import decimal

import pytest

import typesystem


class Person(typesystem.Schema):
    name = typesystem.String(max_length=100, allow_blank=False)
    age = typesystem.Integer()


class Product(typesystem.Schema):
    name = typesystem.String(max_length=100, allow_blank=False)
    rating = typesystem.Integer(default=None)


def test_schema_validation():
    value, error = Person.validate({"name": "Tom", "age": "123"})
    assert not error
    assert value == Person(name="Tom", age=123)

    value, error = Person.validate({"name": "Tom", "age": "123"})
    assert not error
    assert value == Person(name="Tom", age=123)

    value, error = Person.validate({"name": "Tom", "age": "abc"})
    assert dict(error) == {"age": "Must be a number."}

    value, error = Person.validate({"name": "Tom"})
    assert dict(error) == {"age": "This field is required."}


def test_schema_eq():
    tom = Person(name="Tom", age=123)
    lucy = Person(name="Lucy", age=123)
    assert tom != lucy

    tom = Person(name="Tom", age=123)
    tshirt = Product(name="T-Shirt")
    assert tom != tshirt


def test_schema_repr():
    tom = Person(name="Tom", age=123)
    assert repr(tom) == "Person(name='Tom', age=123)"

    tom = Person(name="Tom")
    assert repr(tom) == "Person(name='Tom') [sparse]"


def test_schema_instantiation():
    tshirt = Product(name="T-Shirt")
    assert tshirt.name == "T-Shirt"
    assert tshirt.rating == None

    empty = Product()
    assert not hasattr(empty, "name")

    with pytest.raises(TypeError):
        Product(name="T-Shirt", other="Invalid")

    with pytest.raises(TypeError):
        Product(name="x" * 1000)

    tshirt = Product(name="T-Shirt")
    assert Product(tshirt) == tshirt


def test_schema_subclass():
    class DetailedProduct(Product):
        info = typesystem.Text()

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
    class BlogPost(typesystem.Schema):
        text = typesystem.String()
        created = typesystem.Date()

    post = BlogPost(text="Hi", created=datetime.date.today())

    data = dict(post)

    assert data["text"] == "Hi"
    assert data["created"] == datetime.date.today().isoformat()


def test_schema_decimal_serialization():
    class InventoryItem(typesystem.Schema):
        name = typesystem.String()
        price = typesystem.Decimal(precision="0.01")

    item = InventoryItem(name="Example", price=123.45)

    assert item.price == decimal.Decimal("123.45")
    assert item["price"] == 123.45
