import datetime

import typesystem


def test_namespace():
    schemas = typesystem.SchemaNamespace()

    class Album(schemas.Schema):
        title = typesystem.String(max_length=100)
        release_date = typesystem.Date()
        artist = typesystem.Nested("Artist")

    class Artist(schemas.Schema):
        name = typesystem.String(max_length=100)

    album = Album.validate(
        {
            "title": "Double Negative",
            "release_date": "2018-09-14",
            "artist": {"name": "Low"},
        }
    )
    assert album == Album(
        title="Double Negative",
        release_date=datetime.date(2018, 9, 14),
        artist=Artist(name="Low"),
    )

    # Identical class names in an alternate namespace should not clash.
    schemas = typesystem.SchemaNamespace()

    class Album(schemas.Schema):
        renamed_title = typesystem.String(max_length=100)
        renamed_release_date = typesystem.Date()
        renamed_artist = typesystem.Nested("Artist")

    class Artist(schemas.Schema):
        renamed_name = typesystem.String(max_length=100)

    album = Album.validate(
        {
            "renamed_title": "Double Negative",
            "renamed_release_date": "2018-09-14",
            "renamed_artist": {"renamed_name": "Low"},
        }
    )
    assert album == Album(
        renamed_title="Double Negative",
        renamed_release_date=datetime.date(2018, 9, 14),
        renamed_artist=Artist(renamed_name="Low"),
    )


def test_namespace_as_mapping():
    """
    Ensure that namespaces support a mapping interface.
    """
    schemas = typesystem.SchemaNamespace()

    class Album(schemas.Schema):
        title = typesystem.String(max_length=100)
        release_date = typesystem.Date()
        artist = typesystem.Nested("Artist")

    class Artist(schemas.Schema):
        name = typesystem.String(max_length=100)

    assert schemas["Album"] == Album
    assert schemas["Artist"] == Artist
    assert dict(schemas) == {"Album": Album, "Artist": Artist}
    assert len(schemas) == 2
    del schemas["Artist"]


def test_string_references():
    schemas = typesystem.SchemaNamespace()

    class ExampleA(schemas.Schema):
        field_on_a = typesystem.Integer()
        example_b = typesystem.Nested("ExampleB")

    class ExampleB(schemas.Schema):
        field_on_b = typesystem.Integer()

    value = ExampleA.validate({"field_on_a": "123", "example_b": {"field_on_b": "456"}})
    assert value == ExampleA(field_on_a=123, example_b=ExampleB(field_on_b=456))

    class ExampleC(schemas.Schema):
        field_on_c = typesystem.Integer()
        example_d = typesystem.Array(items=typesystem.Nested("ExampleD"))

    class ExampleD(schemas.Schema):
        field_on_d = typesystem.Integer()

    value = ExampleC.validate(
        {"field_on_c": "123", "example_d": [{"field_on_d": "456"}]}
    )
    assert value == ExampleC(field_on_c=123, example_d=[ExampleD(field_on_d=456)])

    class ExampleE(schemas.Schema):
        field_on_e = typesystem.Integer()
        example_f = typesystem.Array(items=[typesystem.Nested("ExampleF")])

    class ExampleF(schemas.Schema):
        field_on_f = typesystem.Integer()

    value = ExampleE.validate(
        {"field_on_e": "123", "example_f": [{"field_on_f": "456"}]}
    )
    assert value == ExampleE(field_on_e=123, example_f=[ExampleF(field_on_f=456)])

    class ExampleG(schemas.Schema):
        field_on_g = typesystem.Integer()
        example_h = typesystem.Object(properties={"h": typesystem.Nested("ExampleH")})

    class ExampleH(schemas.Schema):
        field_on_h = typesystem.Integer()

    value = ExampleG.validate(
        {"field_on_g": "123", "example_h": {"h": {"field_on_h": "456"}}}
    )
    assert value == ExampleG(field_on_g=123, example_h={"h": ExampleH(field_on_h=456)})
