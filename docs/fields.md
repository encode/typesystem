Fields are usually declared as attributes on schema classes:

```python
class Organisation(typesystem.Schema):
    name = typesystem.String(title="Name", max_length=100)
    date_created = typesystem.Date(title="Date created", default=datetime.date.today)
    owner = typesystem.Reference(to=User, allow_null=True)
```

Fields are always *required* in inputs, unless a *default* value is set.

* Setting `allow_null` to `True` will set the default to `None`. (Unless `default` is already set.)
* Setting `allow_blank` to `True` will set the default to `""`. (Unless `default` or `allow_null` is already set.)

All fields support the following arguments.

**Arguments**:

* `title` - A string to use when labelling the input. **Default: `None`**
* `description` - A string describing the input. **Default: `None`**
* `default` - A value to be used if no input is provided for this field. May be a callable, such as `datetime.datetime.now`. **Default: `NO_DEFAULT`**
* `allow_null` - A boolean determining if `None` values are valid. **Default: `False`**

## Using fields directly

You can use fields to validate data directly, rather than using them on a schema
class. This is useful if you have a general datastructure that requires validation.

For instance, we could validate a dictionary of integers, like so:

```python
validator = typesystem.Object(properties=typesystem.Integer())
value = validator.validate(data)  # May raise `ValidationError`
```

Or returning a two-tuple of `(value, ValidationError)`:

```python
validator = typesystem.Object(properties=typesystem.Integer())
value, error = validator.validate_or_error(data)
if error:
    ...
else:
    ...
```

## Textual data types

### String

Validates single-line text inputs.

For example: `username = typesystem.String(max_length=100)`

**Arguments**:

* `allow_blank` - A boolean indicating if the empty string should validate. **Default: `False`**
* `trim_whitespace` - A boolean indicating if leading/trailing whitespace should be removed on validation. **Default: `True`**
* `max_length` - A maximum number of characters that valid input stings may contain. **Default: `None`**
* `min_length` - A minimum number of characters that valid input stings may contain. **Default: `None`**
* `pattern` - A regular expression that must match. This can be either a string or a compiled regular expression. E.g. `pattern="^[A-Za-z]+$"` **Default: `None`**
* `format` - A string used to indicate a semantic type, such as `"email"`, `"url"`, or `"color"`. **Default: `None`**

### Text

Validates multi-line strings. Takes the same arguments as `String`.
Represented in HTML forms as a `<textarea>`.

## Boolean data types

### Boolean

Represented in HTML forms as a `<checkbox>`.

For example:

```python
is_admin = typesystem.Boolean(default=False)
```

Because all fields are required unless a `default` is given, you'll typically
want to use `default=False`. This is particularly true if you want to render
boolean fields as HTML checkboxes, since they do not submit any input if unchecked.

## Numeric data types

### Number

The base class for `Integer`, `Float`, and `Decimal`.

You won't typically want to use this class directly, since the subclasses
provide more precise behaviour.

**Arguments**:

* `minimum` - A number representing the minimum allowed value. Inputs must be greater than or equal to this to validate. **Default: `None`**
* `maximum` - A number representing the maximum allowed value. Inputs must be less than or equal to this to validate. **Default: `None`**
* `exclusive_minimum` - A number representing an exclusive minimum. Inputs must be greater than this to validate. **Default: `None`**
* `exclusive_maximum` - A number representing an exclusive maximum. Inputs must be less than this to validate. **Default: `None`**
* `precision` - A string representing the decimal precision to truncate input with. E.g. `precision="0.001"`. **Default: `None`**
* `multiple_of` - A number giving a value that inputs must be a strict multiple of in order to validate. E.g. `multiple_of=2` will only validate even integers. **Default: `None`**

### Integer

Takes the same arguments as `Number`. Returns instances of `int`.

### Float

Takes the same arguments as `Number`. Returns instances of `float`.

### Decimal

Takes the same arguments as `Number`. Returns instances of `decimal.Decimal`.

## Enumeration data types

### Choice

Provides a fixed set of options to select from.

Represented in HTML forms as a `<select>`.

**Arguments**:

* `choices` - A list of two-tuples of `(choice, description)`. **Default: None**

## Date and time data types

### DateTime

Validates ISO 8601 formatted datetimes. For example `"2020-02-29T12:34:56Z"`.

Returns `datetime.datetime` instances.

### Date

Validates ISO 8601 formatted dates. For example `"2020-02-29"`.

Returns `datetime.date` instances.

### Time

Validates ISO 8601 formatted times. For example `"12:34:56"`.

Returns `datetime.time` instances.

## Composite data types

### Array

Used to validate a list of data. For example:

```python
# Validates data like `[8, 7, 0, 8, 4, 5]`
ratings = typesystem.Array(items=typesystem.Integer(min_value=0, max_value=10))
```

**Arguments**:

* `items` - Either a `Field`, used to validate each item in the list. Or a list of `Field` instances, used to validate each item in the list, positionally.  **Default: `None`**
* `additional_items` - Only valid if `items` is a list. Either `True` or `False`, or a `Field`. Used to validate each additional item in the list. **Default: `False`**
* `min_items` - An integer, indicating the minimum number of items that must be present in the list. **Default: `None`**
* `max_items` - An integer, indicating the maximum number of items that may be present in the list. **Default: `None`**
* `exact_items` - An integer, indicating the exact number of items that must be present in the list. **Default: `None`**
* `unique_items` - A boolean. Used to determine if duplicate items are allowed in the list. **Default: `False`**

### Object

Used to validate a dictionary of data.

```python
# Validates data like `{"address": "12 Steeple close", "delivery note": "Leave by porch"}`
extra_metadata = typesystem.Object(properties=typesystem.String(max_length=100))
```

Schema classes implement their validation behaviour by generating an `Object`
field, and automatically determining the `properties` and `required` attributes.

You'll typically want to use `typesystem.Reference(to=SomeSchema)` rather than
using the `Object` field directly, but it can be useful if you have a more
complex data structure that you need to validate.

**Arguments**:

* `properties` - Either a `Field`, used to validate each value in the object. Or a dictionary of `Field` instances, used to validate each item in the list, by field name.  **Default: `None`**
* `pattern_properties` - A dictionary mapping regex-style strings to field instances. Used to validate any items not in `properties` that have a key matching the regex. **Default: `None`**
* `additional_properties` - Either a boolean, used to indicate if additional properties are allowed, or a `Field` used to validate any items not in `properties` or `pattern_properties`. If `None` then additional properties are allowed, but are not included in the validated value. **Default: `None`**
* `min_properties` - An integer representing the minimum number of properties that must be included.
* `max_properties` - An integer representing the maximum number of properties that may be included.
* `required` - A list of strings indicating any fields that are strictly required in the input.

### Reference

Used to reference a nested schema.

For example:

```python
owner = typesystem.Reference(to=User, allow_null=True)
```

**Arguments**:

* `to` - A schema class or field instance. **Required**
