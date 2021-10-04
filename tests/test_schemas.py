import datetime

import typesystem
import typesystem.formats


def test_schema():
    validator = typesystem.Schema(fields={})
    value, error = validator.validate_or_error({})
    assert value == {}

    data = validator.serialize(None)
    assert data is None

    validator = typesystem.Schema(fields={"title": typesystem.String()})
    data = validator.serialize({})
    assert data == {}

    validator = typesystem.Schema(fields={})
    value, error = validator.validate_or_error(None)
    assert dict(error) == {"": "May not be null."}

    validator = typesystem.Schema(fields={})
    value, error = validator.validate_or_error(123)
    assert dict(error) == {"": "Must be an object."}

    validator = typesystem.Schema(fields={})
    value, error = validator.validate_or_error({1: 123})
    assert dict(error) == {1: "All object keys must be strings."}

    validator = typesystem.Schema(fields={}, allow_null=True)
    value, error = validator.validate_or_error(None)
    assert value is None
    assert error is None

    validator = typesystem.Schema(fields={"example": typesystem.Integer()})
    value, error = validator.validate_or_error({"example": "123"})
    assert value == {"example": 123}

    validator = typesystem.Schema(fields={"example": typesystem.Integer()})
    value, error = validator.validate_or_error({"example": "abc"})
    assert dict(error) == {"example": "Must be a number."}

    validator = typesystem.Schema(fields={"example": typesystem.Integer(default=0)})
    value, error = validator.validate_or_error({"example": "123"})
    assert value == {"example": 123}

    validator = typesystem.Schema(fields={"example": typesystem.Integer(default=0)})
    value, error = validator.validate_or_error({})
    assert value == {"example": 0}

    validator = typesystem.Schema(fields={"example": typesystem.Integer()})
    value, error = validator.validate_or_error({"example": "abc"})
    assert dict(error) == {"example": "Must be a number."}

    validator = typesystem.Schema(
        fields={"example": typesystem.Integer(read_only=True)}
    )
    value, error = validator.validate_or_error({"example": "123"})
    assert value == {}


person = typesystem.Schema(
    fields={
        "name": typesystem.String(max_length=100, allow_blank=False),
        "age": typesystem.Integer(),
    }
)


product = typesystem.Schema(
    fields={
        "name": typesystem.String(max_length=100, allow_blank=False),
        "rating": typesystem.Integer(default=None),
    }
)


def test_required():
    example = typesystem.Schema(fields={"field": typesystem.Integer()})

    value, error = example.validate_or_error({})
    assert dict(error) == {"field": "This field is required."}

    example = typesystem.Schema(fields={"field": typesystem.Integer(allow_null=True)})

    value, error = example.validate_or_error({})
    assert dict(value) == {"field": None}

    example = typesystem.Schema(fields={"field": typesystem.Integer(default=0)})

    value, error = example.validate_or_error({})
    assert dict(value) == {"field": 0}

    example = typesystem.Schema(
        fields={"field": typesystem.Integer(allow_null=True, default=0)}
    )

    value, error = example.validate_or_error({})
    assert dict(value) == {"field": 0}

    example = typesystem.Schema(fields={"field": typesystem.String()})

    value, error = example.validate_or_error({})
    assert dict(error) == {"field": "This field is required."}

    example = typesystem.Schema(fields={"field": typesystem.String(allow_blank=True)})

    value, error = example.validate_or_error({})
    assert dict(value) == {"field": ""}

    example = typesystem.Schema(
        fields={"field": typesystem.String(allow_null=True, allow_blank=True)}
    )

    value, error = example.validate_or_error({})
    assert dict(value) == {"field": None}


def test_schema_validation():
    value, error = person.validate_or_error({"name": "Tom", "age": "123"})
    assert not error
    assert value == {"name": "Tom", "age": 123}

    value, error = person.validate_or_error({"name": "Tom", "age": "123"})
    assert not error
    assert value == {"name": "Tom", "age": 123}

    value, error = person.validate_or_error({"name": "Tom", "age": "abc"})
    assert dict(error) == {"age": "Must be a number."}

    value, error = person.validate_or_error({"name": "Tom"})
    assert dict(error) == {"age": "This field is required."}


def test_schema_array_serialization():
    category = typesystem.Schema(fields={"title": typesystem.String()})

    definitions = typesystem.Definitions()
    definitions["Category"] = category

    blog_post = typesystem.Schema(
        fields={
            "categories": typesystem.Array(
                items=[typesystem.Reference(to="Category", definitions=definitions)],
                allow_null=True,
            ),
            "text": typesystem.String(),
        }
    )

    item = {"text": "Hi", "categories": [{"title": "Tech"}]}
    data = blog_post.serialize(item)
    assert data["categories"] == [{"title": "Tech"}]

    item = {"text": "Hi", "categories": None}
    data = blog_post.serialize(item)
    assert data["categories"] is None

    blog_post = typesystem.Schema(
        fields={
            "categories": typesystem.Array(allow_null=True),
            "text": typesystem.String(),
        }
    )

    item = {"text": "Hi", "categories": [{"title": 123}]}
    data = blog_post.serialize(item)
    assert data["categories"] == [{"title": 123}]

    blog_post = typesystem.Schema(
        fields={
            "categories": typesystem.Array(items=typesystem.Integer(), allow_null=True),
            "text": typesystem.String(),
        }
    )

    item = {"text": "Hi", "categories": [{"title": 123}]}
    data = blog_post.serialize(item)
    assert data["categories"] == [{"title": 123}]


def test_schema_date_serialization():
    blog_post = typesystem.Schema(
        fields={
            "text": typesystem.String(),
            "created": typesystem.Date(),
            "modified": typesystem.Date(allow_null=True),
        }
    )

    today = datetime.date.today()
    item = {"text": "Hi", "created": today, "modified": None}
    data = blog_post.serialize(item)

    assert data["text"] == "Hi"
    assert data["created"] == today.isoformat()
    assert data["modified"] is None


def test_schema_time_serialization():
    meal_schedule = typesystem.Schema(
        fields={
            "guest_id": typesystem.Integer(),
            "breakfast_at": typesystem.Time(),
            "dinner_at": typesystem.Time(allow_null=True),
        }
    )

    guest_id = 123
    breakfast_at = datetime.time(hour=10, minute=30)
    item = {"guest_id": guest_id, "breakfast_at": breakfast_at, "dinner_at": None}
    data = meal_schedule.serialize(item)

    assert typesystem.formats.TIME_REGEX.match(data["breakfast_at"])
    assert data["guest_id"] == guest_id
    assert data["breakfast_at"] == breakfast_at.isoformat()
    assert data["dinner_at"] is None


def test_schema_datetime_serialization():
    guest = typesystem.Schema(
        fields={
            "id": typesystem.Integer(),
            "name": typesystem.String(),
            "check_in": typesystem.DateTime(),
            "check_out": typesystem.DateTime(allow_null=True),
        }
    )

    guest_id = 123
    guest_name = "Bob"
    check_in = datetime.datetime.now(tz=datetime.timezone.utc)
    item = {"id": guest_id, "name": guest_name, "check_in": check_in, "check_out": None}
    data = guest.serialize(item)

    assert typesystem.formats.DATETIME_REGEX.match(data["check_in"])
    assert data["id"] == guest_id
    assert data["name"] == guest_name
    assert data["check_in"] == check_in.isoformat()[:-6] + "Z"
    assert data["check_out"] is None


def test_schema_decimal_serialization():
    inventory = typesystem.Schema(
        fields={
            "name": typesystem.String(),
            "price": typesystem.Decimal(precision="0.01", allow_null=True),
        }
    )

    item = {"name": "example", "price": 123.45}
    data = inventory.serialize(item)

    assert data["name"] == "example"
    assert data["price"] == 123.45

    item = {"name": "example", "price": None}
    assert inventory.serialize(item) == {"name": "example", "price": None}

    item = {"name": "example", "price": 0}
    assert inventory.serialize(item) == {"name": "example", "price": 0}


def test_schema_uuid_serialization():
    user = typesystem.Schema(
        fields={
            "id": typesystem.String(format="uuid"),
            "username": typesystem.String(),
        }
    )

    item = {"id": "b769df4a-18ec-480f-89ef-8ea961a82269", "username": "tom"}
    data = user.serialize(item)

    assert data["id"] == "b769df4a-18ec-480f-89ef-8ea961a82269"
    assert data["username"] == "tom"


def test_schema_reference_serialization():
    author = typesystem.Schema(fields={"username": typesystem.String()})

    definitions = typesystem.Definitions()
    definitions["Author"] = author

    blog_post = typesystem.Schema(
        fields={
            "author": typesystem.Reference(to="Author", definitions=definitions),
            "text": typesystem.String(),
        }
    )

    item = {"text": "sample", "author": {"username": "tom"}}
    data = blog_post.serialize(item)
    assert data["author"] == {"username": "tom"}

    item = {"text": "sample", "author": None}
    data = blog_post.serialize(item)
    assert data["author"] is None


def test_schema_with_callable_default():
    schema = typesystem.Schema(
        fields={"created": typesystem.Date(default=datetime.date.today)}
    )

    value, _ = schema.validate_or_error({})
    assert value["created"] == datetime.date.today()


def test_nested_schema():
    definitions = typesystem.Definitions()

    artist = typesystem.Schema(fields={"name": typesystem.String(max_length=100)})

    definitions["Artist"] = artist

    album = typesystem.Schema(
        fields={
            "title": typesystem.String(max_length=100),
            "release_year": typesystem.Integer(),
            "artist": typesystem.Reference("Artist", definitions=definitions),
        }
    )

    value = album.validate(
        {"title": "Double Negative", "release_year": "2018", "artist": {"name": "Low"}}
    )
    assert value == {
        "title": "Double Negative",
        "release_year": 2018,
        "artist": {"name": "Low"},
    }

    value, error = album.validate_or_error(
        {"title": "Double Negative", "release_year": "2018", "artist": None}
    )
    assert dict(error) == {"artist": "May not be null."}

    value, error = album.validate_or_error(
        {"title": "Double Negative", "release_year": "2018", "artist": "Low"}
    )
    assert dict(error) == {"artist": "Must be an object."}

    album = typesystem.Schema(
        fields={
            "title": typesystem.String(max_length=100),
            "release_year": typesystem.Integer(),
            "artist": typesystem.Reference(
                "artist", definitions=definitions, allow_null=True
            ),
        }
    )

    value = album.validate(
        {"title": "Double Negative", "release_year": "2018", "artist": None}
    )
    assert value == {
        "title": "Double Negative",
        "release_year": 2018,
        "artist": None,
    }


def test_nested_schema_array():
    artist = typesystem.Schema(fields={"name": typesystem.String(max_length=100)})

    definitions = typesystem.Definitions()
    definitions["Artist"] = artist

    album = typesystem.Schema(
        fields={
            "title": typesystem.String(max_length=100),
            "release_year": typesystem.Integer(),
            "artists": typesystem.Array(
                items=typesystem.Reference(to="Artist", definitions=definitions)
            ),
        }
    )

    value = album.validate(
        {
            "title": "Double Negative",
            "release_year": "2018",
            "artists": [{"name": "Low"}],
        }
    )
    assert value == {
        "title": "Double Negative",
        "release_year": 2018,
        "artists": [{"name": "Low"}],
    }

    value, error = album.validate_or_error(
        {"title": "Double Negative", "release_year": "2018", "artists": None}
    )
    assert dict(error) == {"artists": "May not be null."}

    value, error = album.validate_or_error(
        {"title": "Double Negative", "release_year": "2018", "artists": "Low"}
    )
    assert dict(error) == {"artists": "Must be an array."}

    album = typesystem.Schema(
        fields={
            "title": typesystem.String(max_length=100),
            "release_year": typesystem.Integer(),
            "artists": typesystem.Array(
                items=typesystem.Reference(to="Artist", definitions=definitions),
                allow_null=True,
            ),
        }
    )

    value = album.validate(
        {"title": "Double Negative", "release_year": "2018", "artists": None}
    )
    assert value == {
        "title": "Double Negative",
        "release_year": 2018,
        "artists": None,
    }


def test_nested_schema_to_json_schema():
    artist = typesystem.Schema(fields={"name": typesystem.String(max_length=100)})

    definitions = typesystem.Definitions()
    definitions["Artist"] = artist

    album = typesystem.Schema(
        fields={
            "title": typesystem.String(max_length=100),
            "release_date": typesystem.Date(),
            "artist": typesystem.Reference(to="Artist", definitions=definitions),
        }
    )

    schema = typesystem.to_json_schema(album)

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
    definitions = typesystem.Definitions()

    artist = typesystem.Schema(fields={"name": typesystem.String(max_length=100)})

    album = typesystem.Schema(
        fields={
            "title": typesystem.String(max_length=100),
            "release_date": typesystem.Date(),
            "artist": typesystem.Reference(to="Artist", definitions=definitions),
        }
    )

    definitions["Artist"] = artist
    definitions["Album"] = album

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


def test_schema_email_serialization():
    class User(typesystem.Schema):
        email = typesystem.Email()

    user = User(email="team@enocde.io")

    assert user.email == "team@enocde.io"
    assert user["email"] == "team@enocde.io"
