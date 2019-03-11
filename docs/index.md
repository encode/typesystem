# TypeSystem

<p>
<a href="https://travis-ci.org/encode/typesystem">
    <img src="https://travis-ci.org/encode/typesystem.svg?branch=master" alt="Build Status">
</a>
<a href="https://codecov.io/gh/encode/typesystem">
    <img src="https://codecov.io/gh/encode/typesystem/branch/master/graph/badge.svg" alt="Coverage">
</a>
<a href="https://pypi.org/project/typesystem/">
    <img src="https://badge.fury.io/py/typesystem.svg" alt="Package version">
</a>
</p>

TypeSystem is a comprehensive data validation library that gives you:

* Data validation.
* Object serialization & deserialization.
* Form rendering.
* Marshaling validators to/from JSON schema.
* Tokenizing JSON or YAML to provide positional error messages.
* 100% type annotated codebase.
* 100% test coverage.
* Zero hard dependencies.

## Requirements

Python 3.6+

## Installation

```shell
$ pip3 install typesystem
```

If you'd like you use the form rendering you'll also want to install `jinja2`.

```shell
$ pip3 install jinja2
```

## Quickstart

```python
import typesystem

class Artist(typesystem.Schema):
    name = typesystem.String(max_length=100)

class Album(typesystem.Schema):
    title = typesystem.String(max_length=100)
    release_date = typesystem.Date()
    artist = typesystem.Reference(Artist)

album = Album.validate({
    "title": "Double Negative",
    "release_date": "2018-09-14",
    "artist": {"name": "Low"}
})

print(album)
# Album(title='Double Negative', release_date=datetime.date(2018, 9, 14), artist=Artist(name='Low'))

print(album.release_date)
# datetime.date(2018, 9, 14)

print(album['release_date'])
# '2018-09-14'

print(dict(album))
# {'title': 'Double Negative', 'release_date': '2018-09-14', 'artist': {'name': 'Low'}}
```

## Alternatives

There are plenty of other great validation libraries for Python out there,
including [Marshmallow](https://github.com/marshmallow-code/marshmallow),
[Schematics](https://github.com/schematics/schematics),
[Voluptuous](https://github.com/alecthomas/voluptuous), and many others.

TypeSystem exists because I want a data validation library that offers
first-class support for:

* Rendering validation classes into HTML forms.
* Marshaling to/from JSON Schema.
* Obtaining positional errors within JSON or YAML documents.

<p align="center">&mdash; ⭐️ &mdash;</p>
<p align="center"><i>TypeSystem is <a href="https://github.com/encode/typesystem/blob/master/LICENSE.md">BSD licensed</a> code. Designed & built in Brighton, England.</i></p>
