TypeSystem can convert Schema classes or Field instances to/from JSON Schema.

!!! note
    TypeSystem only supports `$ref` pointers that use the standard "definitions"
    namespace to store referenced schemas.

    All references should be of the style `{"$ref": "#/definitions/..."}`.

    Using hyperlinked references, relative references, or references to parts
    of the document other than "definitions" is not supported.

Let's define a schema, and dump it out into a JSON schema document:

```python
import json
import typesystem

class BookingSchema(typesystem.Schema):
    start_date = typesystem.Date(title="Start date")
    end_date = typesystem.Date(title="End date")
    room = typesystem.Choice(
        title="Room type",
        choices=[
            ("double", "Double room"),
            ("twin", "Twin room"),
            ("single", "Single room"),
        ],
    )
    include_breakfast = typesystem.Boolean(title="Include breakfast", default=False)

schema = typesystem.to_json_schema(BookingSchema)
print(json.dumps(schema, indent=4))
```

That will print the following JSON schema document:

```json
{
    "type": "object",
    "properties": {
        "start_date": {
            "type": "string",
            "minLength": 1,
            "format": "date"
        },
        "end_date": {
            "type": "string",
            "minLength": 1,
            "format": "date"
        },
        "room": {
            "enum": [
                "double",
                "twin",
                "single"
            ]
        },
        "include_breakfast": {
            "type": "boolean",
            "default": false
        }
    },
    "required": [
        "start_date",
        "end_date",
        "room"
    ]
}
```

We can also convert in the other direction:

```python
import typesystem

schema = {
    "type": "object",
    "properties": {
        "start_date": {
            "type": "string",
            "minLength": 1,
            "format": "date"
        },
        "end_date": {
            "type": "string",
            "minLength": 1,
            "format": "date"
        },
        "room": {
            "enum": [
                "double",
                "twin",
                "single"
            ]
        },
        "include_breakfast": {
            "type": "boolean",
            "default": False
        }
    },
    "required": [
        "start_date",
        "end_date",
        "room"
    ]
}

validator = typesystem.from_json_schema(schema)
validator.validate({
  'start_date': '2021-01-01',
  'end_date': '2021-01-03'
})
# raises `ValidationError: {'room': 'This field is required.'}`
```
