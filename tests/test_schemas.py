import datetime
import decimal
import uuid

import pytest

import typesystem
import typesystem.formats


class Person(typesystem.Schema):
    name = typesystem.String(max_length=100, allow_blank=False)
    age = typesystem.Integer()


class Product(typesystem.Schema):
    name = typesystem.String(max_length=100, allow_blank=False)
    rating = typesystem.Integer(default=None)


def test_required():
    class Example(typesystem.Schema):
        field = typesystem.Integer()

    value, error = Example.validate_or_error({})
    assert dict(error) == {"field": "This field is required."}

    class Example(typesystem.Schema):
        field = typesystem.Integer(allow_null=True)

    value, error = Example.validate_or_error({})
    assert dict(value) == {"field": None}

    class Example(typesystem.Schema):
        field = typesystem.Integer(default=0)

    value, error = Example.validate_or_error({})
    assert dict(value) == {"field": 0}

    class Example(typesystem.Schema):
        field = typesystem.Integer(allow_null=True, default=0)

    value, error = Example.validate_or_error({})
    assert dict(value) == {"field": 0}

    class Example(typesystem.Schema):
        field = typesystem.String()

    value, error = Example.validate_or_error({})
    assert dict(error) == {"field": "This field is required."}

    class Example(typesystem.Schema):
        field = typesystem.String(allow_blank=True)

    value, error = Example.validate_or_error({})
    assert dict(value) == {"field": ""}

    class Example(typesystem.Schema):
        field = typesystem.String(allow_null=True, allow_blank=True)

    value, error = Example.validate_or_error({})
    assert dict(value) == {"field": None}


def test_schema_validation():
    value, error = Person.validate_or_error({"name": "Tom", "age": "123"})
    assert not error
    assert value == Person(name="Tom", age=123)

    value, error = Person.validate_or_error({"name": "Tom", "age": "123"})
    assert not error
    assert value == Person(name="Tom", age=123)

    value, error = Person.validate_or_error({"name": "Tom", "age": "abc"})
    assert dict(error) == {"age": "Must be a number."}

    value, error = Person.validate_or_error({"name": "Tom"})
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


def test_schema_null_items_array_serialization():
    class Product(typesystem.Schema):
        names = typesystem.Array()

    tshirt = Product(names=[1, "2", {"nested": 3}])

    data = dict(tshirt)

    assert data == {"names": [1, "2", {"nested": 3}]}


def test_schema_string_array_serialization():
    class Product(typesystem.Schema):
        names = typesystem.Array(typesystem.String())

    tshirt = Product(names=["T-Shirt"])

    data = dict(tshirt)

    assert data == {"names": ["T-Shirt"]}


def test_schema_dates_array_serialization():
    class BlogPost(typesystem.Schema):
        text = typesystem.String()
        modified = typesystem.Array(typesystem.Date())

    post = BlogPost(text="Hi", modified=[datetime.date.today()])

    data = dict(post)

    assert data["text"] == "Hi"
    assert data["modified"] == [datetime.date.today().isoformat()]


def test_schema_positional_array_serialization():
    class NumberName(typesystem.Schema):
        pair = typesystem.Array([typesystem.Integer(), typesystem.String()])

    name = NumberName(pair=[1, "one"])

    data = dict(name)

    assert data == {"pair": [1, "one"]}


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


def test_schema_date_serialization():
    class BlogPost(typesystem.Schema):
        text = typesystem.String()
        created = typesystem.Date()
        modified = typesystem.Date(allow_null=True)

    post = BlogPost(text="Hi", created=datetime.date.today())

    data = dict(post)

    assert data["text"] == "Hi"
    assert data["created"] == datetime.date.today().isoformat()
    assert data["modified"] is None


def test_schema_time_serialization():
    class MealSchedule(typesystem.Schema):
        guest_id = typesystem.Integer()
        breakfast_at = typesystem.Time()
        dinner_at = typesystem.Time(allow_null=True)

    guest_id = 123
    breakfast_at = datetime.time(hour=10, minute=30)
    schedule = MealSchedule(guest_id=guest_id, breakfast_at=breakfast_at)

    assert typesystem.formats.TIME_REGEX.match(schedule["breakfast_at"])
    assert schedule["guest_id"] == guest_id
    assert schedule["breakfast_at"] == breakfast_at.isoformat()
    assert schedule["dinner_at"] is None


def test_schema_datetime_serialization():
    class Guest(typesystem.Schema):
        id = typesystem.Integer()
        name = typesystem.String()
        check_in = typesystem.DateTime()
        check_out = typesystem.DateTime(allow_null=True)

    guest_id = 123
    guest_name = "Bob"
    check_in = datetime.datetime.now(tz=datetime.timezone.utc)
    guest = Guest(id=guest_id, name=guest_name, check_in=check_in)

    assert typesystem.formats.DATETIME_REGEX.match(guest["check_in"])
    assert guest["id"] == guest_id
    assert guest["name"] == guest_name
    assert guest["check_in"] == check_in.isoformat()[:-6] + "Z"
    assert guest["check_out"] is None


def test_schema_decimal_serialization():
    class InventoryItem(typesystem.Schema):
        name = typesystem.String()
        price = typesystem.Decimal(precision="0.01", allow_null=True)

    item = InventoryItem(name="Example", price=123.45)

    assert item.price == decimal.Decimal("123.45")
    assert item["price"] == 123.45

    item = InventoryItem(name="test")
    assert dict(item) == {"name": "test", "price": None}
    item = InventoryItem(name="test", price=0)
    assert dict(item) == {"name": "test", "price": 0}


def test_schema_uuid_serialization():
    class User(typesystem.Schema):
        id = typesystem.String(format="uuid")
        username = typesystem.String()

    item = User(id="b769df4a-18ec-480f-89ef-8ea961a82269", username="tom")

    assert item.id == uuid.UUID("b769df4a-18ec-480f-89ef-8ea961a82269")
    assert item["id"] == "b769df4a-18ec-480f-89ef-8ea961a82269"


def test_schema_with_callable_default():
    class Example(typesystem.Schema):
        created = typesystem.Date(default=datetime.date.today)

    value, error = Example.validate_or_error({})
    assert value.created == datetime.date.today()


def test_nested_schema():
    class Artist(typesystem.Schema):
        name = typesystem.String(max_length=100)

    class Album(typesystem.Schema):
        title = typesystem.String(max_length=100)
        release_year = typesystem.Integer()
        artist = typesystem.Reference(Artist)

    value = Album.validate(
        {"title": "Double Negative", "release_year": "2018", "artist": {"name": "Low"}}
    )
    assert dict(value) == {
        "title": "Double Negative",
        "release_year": 2018,
        "artist": {"name": "Low"},
    }
    assert value == Album(
        title="Double Negative", release_year=2018, artist=Artist(name="Low")
    )

    value, error = Album.validate_or_error(
        {"title": "Double Negative", "release_year": "2018", "artist": None}
    )
    assert dict(error) == {"artist": "May not be null."}

    value, error = Album.validate_or_error(
        {"title": "Double Negative", "release_year": "2018", "artist": "Low"}
    )
    assert dict(error) == {"artist": "Must be an object."}

    class Album(typesystem.Schema):
        title = typesystem.String(max_length=100)
        release_year = typesystem.Integer()
        artist = typesystem.Reference(Artist, allow_null=True)

    value = Album.validate(
        {"title": "Double Negative", "release_year": "2018", "artist": None}
    )
    assert dict(value) == {
        "title": "Double Negative",
        "release_year": 2018,
        "artist": None,
    }


def test_nested_schema_array():
    class Artist(typesystem.Schema):
        name = typesystem.String(max_length=100)

    class Album(typesystem.Schema):
        title = typesystem.String(max_length=100)
        release_year = typesystem.Integer()
        artists = typesystem.Array(items=typesystem.Reference(Artist))

    value = Album.validate(
        {
            "title": "Double Negative",
            "release_year": "2018",
            "artists": [{"name": "Low"}],
        }
    )
    assert dict(value) == {
        "title": "Double Negative",
        "release_year": 2018,
        "artists": [{"name": "Low"}],
    }
    assert value == Album(
        title="Double Negative", release_year=2018, artists=[Artist(name="Low")]
    )

    value, error = Album.validate_or_error(
        {"title": "Double Negative", "release_year": "2018", "artists": None}
    )
    assert dict(error) == {"artists": "May not be null."}

    value, error = Album.validate_or_error(
        {"title": "Double Negative", "release_year": "2018", "artists": "Low"}
    )
    assert dict(error) == {"artists": "Must be an array."}

    class Album(typesystem.Schema):
        title = typesystem.String(max_length=100)
        release_year = typesystem.Integer()
        artists = typesystem.Array(items=typesystem.Reference(Artist), allow_null=True)

    value = Album.validate(
        {"title": "Double Negative", "release_year": "2018", "artists": None}
    )
    assert dict(value) == {
        "title": "Double Negative",
        "release_year": 2018,
        "artists": None,
    }


def test_nested_schema_to_json_schema():
    class Artist(typesystem.Schema):
        name = typesystem.String(max_length=100)

    class Album(typesystem.Schema):
        title = typesystem.String(max_length=100)
        release_date = typesystem.Date()
        artist = typesystem.Reference(Artist)

    schema = typesystem.to_json_schema(Album)

    assert schema == {
        "type": "object",
        "properties": {
            "title": {"type": "string", "minLength": 1, "maxLength": 100},
            "release_date": {"type": "string", "minLength": 1, "format": "date"},
            "artist": {"$ref": "#/definitions/Artist"},
        },
        "required": ["title", "release_date", "artist"],
        "definitions": {
            "Artist": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "minLength": 1, "maxLength": 100}
                },
                "required": ["name"],
            }
        },
    }


def test_definitions_to_json_schema():
    definitions = typesystem.SchemaDefinitions()

    class Artist(typesystem.Schema, definitions=definitions):
        name = typesystem.String(max_length=100)

    class Album(typesystem.Schema, definitions=definitions):
        title = typesystem.String(max_length=100)
        release_date = typesystem.Date()
        artist = typesystem.Reference("Artist")

    schema = typesystem.to_json_schema(definitions)

    assert schema == {
        "definitions": {
            "Artist": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "minLength": 1, "maxLength": 100}
                },
                "required": ["name"],
            },
            "Album": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "minLength": 1, "maxLength": 100},
                    "release_date": {
                        "type": "string",
                        "minLength": 1,
                        "format": "date",
                    },
                    "artist": {"$ref": "#/definitions/Artist"},
                },
                "required": ["title", "release_date", "artist"],
            },
        }
    }
