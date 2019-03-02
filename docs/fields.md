Fields are usually declared as attributes on schema classes:

```python
class Organisation(typesystem.Schema):
    name = typesystem.String(title="Name", max_length=100)
    date_created = typesystem.Date(title="Date created", default=datetime.date.today)
    owner = typesystem.Nested(title="Owner", schema=User, allow_null=True)
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
* `pattern` - A string to be used as a regex that must match. Eg. `patern="^[A-Za-z]+$"` **Default: `None`**
* `format` - **TODO**

### Text

Validates multi-line strings. Takes the same arguments as `String`.
Represented in HTML forms as a `<textarea>`.

## Boolean data types

### Boolean

Represented in HTML forms as a `<checkbox>`.

For example: `is_admin = typesystem.Boolean(default=False)`

Because all fields are required unless a `default` is given, you'll typically
want to use `default=False`. This is particularly true if you want to render
boolean fields as HTML checkboxes, since they do not submit any input if unchecked.

## Numeric data types

### Number

A base class for `Integer`, `Float`, and `Decimal`. If used directly, `Number`
will validate *either* int or float instances.

**Arguments**:

* `minimum` - A number representing the minimum allowed value. Inputs must be greater than or equal to this to validate. **Default: `None`**
* `maximum` - A number representing the maximum allowed value. Inputs must be less than or equal to this to validate. **Default: `None`**
* `exclusive_minimum` - A number representing an exclusive minimum. Inputs must be greater than this to validate. **Default: `None`**
* `exclusive_maximum` - A number representing an exclusive maximum. Inputs must be less than this to validate. **Default: `None`**
* `precision` - A string representing the decimal precision to truncate input with. Eg. `precision="0.001"`. **Default: `None`**
* `multiple_of` - A number giving a value that inputs must be a strict multiple of in order to validate. Eg. `multiple_of=2` will only validate even integers. **Default: `None`**

### Integer

Takes the same arguments as `Number`. Returns instances of `int`.

### Float

Takes the same arguments as `Number`. Returns instances of `float`.

### Decimal

Takes the same arguments as `Number`. Returns instances of `decimal.Decimal`.

## Enumeration data types

### Choice

**Arguments**:

* `choices` - A list of two-tuples of `(choice, description)`. **Default: None**

## Date and time data types

### Date

### Time

### DateTime

## Composite data types

### Array

Used to validate a list of data. For example:

```python
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

**Arguments**:

* `properties`
* `pattern_properties`
* `additional_properties`
* `min_properties`
* `max_properties`
* `required`

### Nested

* `schema` - A schema class. **Required**

## Custom field types
