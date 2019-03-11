import datetime

import typesystem


def test_reference():
    definitions = typesystem.SchemaDefinitions()

    class Album(typesystem.Schema, definitions=definitions):
        title = typesystem.String(max_length=100)
        release_date = typesystem.Date()
        artist = typesystem.Reference("Artist")

    class Artist(typesystem.Schema, definitions=definitions):
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

    # Identical class names in alternate definitions should not clash.
    definitions = typesystem.SchemaDefinitions()

    class Album(typesystem.Schema, definitions=definitions):
        renamed_title = typesystem.String(max_length=100)
        renamed_release_date = typesystem.Date()
        renamed_artist = typesystem.Reference("Artist")

    class Artist(typesystem.Schema, definitions=definitions):
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


def test_definitions_as_mapping():
    """
    Ensure that definitions support a mapping interface.
    """
    definitions = typesystem.SchemaDefinitions()

    class Album(typesystem.Schema, definitions=definitions):
        title = typesystem.String(max_length=100)
        release_date = typesystem.Date()
        artist = typesystem.Reference("Artist")

    class Artist(typesystem.Schema, definitions=definitions):
        name = typesystem.String(max_length=100)

    assert definitions["Album"] == Album
    assert definitions["Artist"] == Artist
    assert dict(definitions) == {"Album": Album, "Artist": Artist}
    assert len(definitions) == 2
    del definitions["Artist"]


def test_string_references():
    definitions = typesystem.SchemaDefinitions()

    class ExampleA(typesystem.Schema, definitions=definitions):
        field_on_a = typesystem.Integer()
        example_b = typesystem.Reference("ExampleB")

    class ExampleB(typesystem.Schema, definitions=definitions):
        field_on_b = typesystem.Integer()

    value = ExampleA.validate({"field_on_a": "123", "example_b": {"field_on_b": "456"}})
    assert value == ExampleA(field_on_a=123, example_b=ExampleB(field_on_b=456))

    class ExampleC(typesystem.Schema, definitions=definitions):
        field_on_c = typesystem.Integer()
        example_d = typesystem.Array(items=typesystem.Reference("ExampleD"))

    class ExampleD(typesystem.Schema, definitions=definitions):
        field_on_d = typesystem.Integer()

    value = ExampleC.validate(
        {"field_on_c": "123", "example_d": [{"field_on_d": "456"}]}
    )
    assert value == ExampleC(field_on_c=123, example_d=[ExampleD(field_on_d=456)])

    class ExampleE(typesystem.Schema, definitions=definitions):
        field_on_e = typesystem.Integer()
        example_f = typesystem.Array(items=[typesystem.Reference("ExampleF")])

    class ExampleF(typesystem.Schema, definitions=definitions):
        field_on_f = typesystem.Integer()

    value = ExampleE.validate(
        {"field_on_e": "123", "example_f": [{"field_on_f": "456"}]}
    )
    assert value == ExampleE(field_on_e=123, example_f=[ExampleF(field_on_f=456)])

    class ExampleG(typesystem.Schema, definitions=definitions):
        field_on_g = typesystem.Integer()
        example_h = typesystem.Object(
            properties={"h": typesystem.Reference("ExampleH")}
        )

    class ExampleH(typesystem.Schema, definitions=definitions):
        field_on_h = typesystem.Integer()

    value = ExampleG.validate(
        {"field_on_g": "123", "example_h": {"h": {"field_on_h": "456"}}}
    )
    assert value == ExampleG(field_on_g=123, example_h={"h": ExampleH(field_on_h=456)})
