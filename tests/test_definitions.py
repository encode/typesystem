import datetime

import typesystem


def test_reference():
    definitions = typesystem.Definitions()

    album = typesystem.Schema(
        fields={
            "title": typesystem.String(max_length=100),
            "release_date": typesystem.Date(),
            "artist": typesystem.Reference("Artist", definitions=definitions),
        }
    )

    artist = typesystem.Schema(fields={"name": typesystem.String(max_length=100)})

    definitions["Artist"] = artist

    value = album.validate(
        {
            "title": "Double Negative",
            "release_date": "2018-09-14",
            "artist": {"name": "Low"},
        }
    )
    assert value == {
        "title": "Double Negative",
        "release_date": datetime.date(2018, 9, 14),
        "artist": {"name": "Low"},
    }


def test_definitions_as_mapping():
    """
    Ensure that definitions support a mapping interface.
    """
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

    definitions["Album"] = album

    assert definitions["Album"] == album
    assert definitions["Artist"] == artist
    assert dict(definitions) == {"Album": album, "Artist": artist}
    assert len(definitions) == 2
    del definitions["Artist"]


def test_string_references():
    definitions = typesystem.Definitions()

    example_b = typesystem.Schema(
        fields={
            "field_on_b": typesystem.Integer(),
        }
    )

    definitions["ExampleB"] = example_b

    example_a = typesystem.Schema(
        fields={
            "field_on_a": typesystem.Integer(),
            "example_b": typesystem.Reference(to="ExampleB", definitions=definitions),
        }
    )

    value = example_a.validate(
        {"field_on_a": "123", "example_b": {"field_on_b": "456"}}
    )
    assert value == {"field_on_a": 123, "example_b": {"field_on_b": 456}}

    example_d = typesystem.Schema(fields={"field_on_d": typesystem.Integer()})

    definitions["ExampleD"] = example_d

    example_c = typesystem.Schema(
        fields={
            "field_on_c": typesystem.Integer(),
            "example_d": typesystem.Array(
                items=typesystem.Reference(to="ExampleD", definitions=definitions)
            ),
        }
    )

    value = example_c.validate(
        {"field_on_c": "123", "example_d": [{"field_on_d": "456"}]}
    )
    assert value == {"field_on_c": 123, "example_d": [{"field_on_d": 456}]}

    example_f = typesystem.Schema(fields={"field_on_f": typesystem.Integer()})

    definitions["ExampleF"] = example_f

    example_e = typesystem.Schema(
        fields={
            "field_on_e": typesystem.Integer(),
            "example_f": typesystem.Array(
                items=[typesystem.Reference(to="ExampleF", definitions=definitions)]
            ),
        }
    )

    value = example_e.validate(
        {"field_on_e": "123", "example_f": [{"field_on_f": "456"}]}
    )
    assert value == {"field_on_e": 123, "example_f": [{"field_on_f": 456}]}

    example_h = typesystem.Schema(fields={"field_on_h": typesystem.Integer()})

    definitions["ExampleH"] = example_h

    example_g = typesystem.Schema(
        fields={
            "field_on_g": typesystem.Integer(),
            "example_h": typesystem.Object(
                properties={
                    "h": typesystem.Reference(to="ExampleH", definitions=definitions)
                }
            ),
        }
    )

    value = example_g.validate(
        {"field_on_g": "123", "example_h": {"h": {"field_on_h": "456"}}}
    )
    assert value == {"field_on_g": 123, "example_h": {"h": {"field_on_h": 456}}}
