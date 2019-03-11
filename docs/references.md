References are a special type of field used to interlink schemas.

The simplest way to use a reference, is with a schema class as a the target.

```python
import typesystem

class Artist(typesystem.Schema):
    name = typesystem.String(max_length=100)

class Album(typesystem.Schema):
    title = typesystem.String(max_length=100)
    release_date = typesystem.Date()
    artist = typesystem.Reference(to=Artist)
```

Using a schema class directly might not always be possible. If you need to
to support back-references or cyclical references, you can use a string-literal
reference and provide a `SchemaDefinitions` instance, which is a dictionary-like
object providing an index of reference lookups.

```python
import typesystem

definitions = typesystem.SchemaDefinitions()

class Artist(typesystem.Schema):
    name = typesystem.String(max_length=100)

class Person(typesystem.Schema):
    name = typesystem.String(max_length=100)
    release_date = typesystem.Date()
    artist = typesystem.Reference(to='Artist', definitions=definitions)

definitions['Artist'] = Artist
definitions['Person'] = Person
```

A shorthand for including a schema class in the definitions index, and for
setting the `definitions` on any Reference fields, is to declare schema
classes with the `definitions` keyword argument, like so:

```python
import typesystem

definitions = typesystem.SchemaDefinitions()

class Artist(typesystem.Schema, definitions=definitions):
    name = typesystem.String(max_length=100)

class Person(typesystem.Schema, definitions=definitions):
    name = typesystem.String(max_length=100)
    release_date = typesystem.Date()
    artist = typesystem.Reference(to='Artist')
```
