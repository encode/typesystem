Let's start by defining some schemas.

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
        "artist": typesystem.Reference("Artist", definitions=definitions)
    }
)
```

We've got some incoming user data that we'd like to validate against our schema.

```python
data = {
    'title': 'Double Negative',
    'release_date': '2018-09-14',
    'artist': {'name': 'Low'}
}
```

We can validate the data against a Schema by using `.validate(data)`.

```python
album = album_schema.validate(data)
```

If validation succeeds, this will return an `dict`.

If validation fails, a `ValidationError` will be raised.

Alternatively we can use `.validate_or_error(data)`, which will return a
two-tuple of `(value, error)`. Either one of `value` or `error` will be `None`.

```python
album, error = album_schema.validate_or_error(data)
if error:
    ...
else:
    ...
```

## Working with validation errors

The `ValidationError` class presents a dict-like interface:

```python
invalid_data = {
    'title': 'Double Negative',
    'release_date': '2018.09.14',
    'artist': {'name': 'x' * 1000}
}
album, error = album_schema.validate_or_error(invalid_data)

print(dict(error))
# {'release_date': 'Must be a valid date format.', 'artist': {'name': 'Must have no more than 100 characters.'}}
print(list(error.keys()))
# ['release_date', 'artist']
```

If you want more precise information about exactly what error messages exist,
you can access each individual message with `error.messages()`:

```python
album, error = album_schema.validate_or_error(invalid_data)

for message in error.messages():
    print(f'{message.index!r}, {message.code!r}, {message.text!r})')
# ['release_date'], 'format', 'Must be a valid date format.'
# ['artist', 'name'], 'max_length', 'Must have no more than 100 characters.'
```

## Working with schema instances

Python dictionaries are returned by calls to `.validate()`.

```python
data = {
    'title': 'Double Negative',
    'release_date': '2018-09-14',
    'artist': {'name': 'Low'}
}
album = album_schema.validate(data)

print(album)
# {'title': 'Double Negative', 'release_date': '2018-09-14', 'artist': {'name': 'Low'}}
```

You can also `serialize` data using the schema instance:

```python
artist = artist_schema.serialize({'name': 'Low'})
album = album_schema.serialize({'title': 'Double Negative', 'artist': artist})
```

If `serialize` directly, validation is not done and data returned may be sparsely populated.
Any unused attributes without a default will not be returned.

```python
artist = artist_schema.serialize({'name': 'Low'})
album = album_schema.serialize({'title': 'Double Negative', 'artist': artist})

print(album)
# {'title': 'Double Negative', 'artist': {'name': 'Low'}} [sparse]

album['release_date']
# KetError: 'release_date'
```

Sparsely serialized data can be useful for cases of loading data from database,
when you do not need to retrieve all the fields, or for cases of loading nested
data where no database join has been made, and only the primary key of the relationship
is known.

## Using strict validation

By default, additional properties in the incoming user data is ignored.

```python
data = {
    'title': 'Double Negative',
    'release_date': '2018-09-14',
    'artist': {'name': 'Low'},
    'num_tracks': 11
}
```

After validating against the schema, the `num_tracks` property is not present
in the returned data.

```python
album = album_schema.validate(data)
album['num_tracks]
# KeyError: 'num_tracks'
```
