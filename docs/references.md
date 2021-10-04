References are a special type of field used to interlink schemas.

The simplest way to use a reference, is with a schema class as a the target.

```python
import typesystem

artist_schema = typesystem.Schema(
    fields={
        "name": typesystem.String(max_length=100)
    }
)

definitions = typesystem.Definitions()
definitions["Artist"] = artist_schema

album_schema = typesystem.Schema(
    fields={
        "title": typesystem.String(max_length=100),
        "release_date": typesystem.Date(),
        "artist": typesystem.Reference(to="Artist", definitions=definitions),
    }
)
```

Registering schema instances against a `Definitions` instance is particularly
useful if you're using JSON schema to document the input and output types of
a Web API, since you can easily dump all the type definitions:

```python
import json
import typesystem

definitions = typesystem.Definitions()

artist_schema = typesystem.Schema(
    fields={
        "name": typesystem.String(max_length=100)
    }
)

album_schema = typesystem.Schema(
    fields={
        "title": typesystem.String(max_length=100),
        "release_date": typesystem.Date(),
        "artist": typesystem.Reference(to="Artist", definitions=definitions),
    }
)

definitions["Artist"] = artist_schema
definitions["Album"] = album_schema

document = typesystem.to_json_schema(definitions)
print(json.dumps(document, indent=4))
# {
#     "definitions": {
#         "Artist": {
#             "type": "object",
#             "properties": {
#                 "name": {
#                     "type": "string",
#                     "minLength": 1,
#                     "maxLength": 100
#                 }
#             },
#             "required": [
#                 "name"
#             ]
#         },
#         "Album": {
#             "type": "object",
#             "properties": {
#                 "title": {
#                     "type": "string",
#                     "minLength": 1,
#                     "maxLength": 100
#                 },
#                 "release_date": {
#                     "type": "string",
#                     "minLength": 1,
#                     "format": "date"
#                 },
#                 "artist": {
#                     "$ref": "#/definitions/Artist"
#                 }
#             },
#             "required": [
#                 "title",
#                 "release_date",
#                 "artist"
#             ]
#         }
#     }
# }
```
