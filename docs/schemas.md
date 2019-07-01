Let's start by defining some schema classes.

```python
import typesystem

class Artist(typesystem.Schema):
    name = typesystem.String(max_length=100)

class Album(typesystem.Schema):
    title = typesystem.String(max_length=100)
    release_date = typesystem.Date()
    artist = typesystem.Reference(Artist)
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
album = Album.validate(data)
```

If validation succeeds, this will return an `Album` instance.

If validation fails, a `ValidationError` will be raised.

Alternatively we can use `.validate_or_error(data)`, which will return a
two-tuple of `(value, error)`. Either one of `value` or `error` will be `None`.

```python
album, error = Album.validate_or_error(data)
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
album, error = Album.validate_or_error(invalid_data)

print(dict(error))
# {'release_date': 'Must be a valid date format.', 'artist': {'name': 'Must have no more than 100 characters.'}}
print(list(error.keys()))
# ['release_date', 'artist']
```

If you want more precise information about exactly what error messages exist,
you can access each individual message with `error.messages()`:

```python
album, error = Album.validate_or_error(invalid_data)

for message in error.messages():
    print(f'{message.index!r}, {message.code!r}, {message.text!r})')
# ['release_date'], 'format', 'Must be a valid date format.'
# ['artist', 'name'], 'max_length', 'Must have no more than 100 characters.'
```

## Working with schema instances

Schema instances are returned by calls to `.validate()`.

```python
data = {
    'title': 'Double Negative',
    'release_date': '2018-09-14',
    'artist': {'name': 'Low'}
}
album = Album.validate(data)
print(album)
# Album(title='Double Negative', release_date=datetime.date(2018, 9, 14), artist=Artist(name='Low'))
```

Attributes on schemas return native python data types.

```python
print(type(album.release_date))
# <class 'datetime.date'>
```

Schema instances present a dict-like interface, allowing them to be easily serialized.

```python
print(dict(album))
# {'title': 'Double Negative', 'release_date': '2018-09-14', 'artist': {'name': 'Low'}}
```

Index lookup on schema instances returns serialized datatypes.

```python
print(type(album['release_date']))
# <class 'str'>
```

You can also instantiate schema instances directly.

```python
artist = Artist(name='Low')
album = Album(title='Double Negative', release_date='2018-09-14', artist=artist)
```

When instantiating with keyword arguments, each keyword argument will be validated.

If instantiated directly, schema instances may be sparsely populated. Any unused
attributes without a default will not be set on the instance.

```python
artist = Artist(name='Low')
album = Album(title='Double Negative', artist=artist)
print(album)
# Album(title='Double Negative', artist=Artist(name='Low')) [sparse]
album.release_date
# AttributeError: 'Album' object has no attribute 'release_date'
print(dict(album))
{'title': 'Double Negative', 'artist': {'name': 'Low'}}
```

Sparsely populated instances can be useful for cases of loading data from database,
when you do not need to retrieve all the fields, or for cases of loading nested
data where no database join has been made, and only the primary key of the relationship
is known.

You can also instantiate a schema from an object instance or dictionary.

```python
new_album = Album(album)
```

Note that data validation is not applied when instantiating a schema instance
directly from an instance or dictionary. This should be used when creating
instances against a data source that is already known to be validated, such as
when loading existing instances from a database.

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
on the `album` instance.

```python
album = Album.validate(data)
album.num_tracks
# AttributeError: 'Album' object has no attribute 'num_tracks'
```

If you use strict validation, additional properties becomes an error instead.

```python
album, error = Album.validate_or_error(data, strict=True)

print(dict(error))
# {'num_tracks': 'Invalid property name.'}
```
