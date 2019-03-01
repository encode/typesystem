* `title`
* `description`
* `default`
* `allow_null`

### String

* `allow_blank`
* `max_length`
* `min_length`
* `pattern`
* `format`

### Text

### Boolean

## Numeric data types

### Number

* `minimum` - An integer representing the minimum allowed value. **Default: `None`**
* `maximum` - An integer representing the maximum allowed value. **Default: `None`**
* `exclusive_minimum` - An integer representing the minimum allowed value. **Default: `None`**
* `exclusive_maximum`
* `precision` - A string representing the decimal precision to truncate input with. Eg. `precision="0.001"`. **Default: `None`**
* `multiple_of`

### Integer

### Float

### Decimal

## Enumeration data types

### Choice

* `choices` - May be any of the following: A list of choices. A dict of `{choice: description}`. A list of two-tuples of `(choice, description)`. **Required**

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

* `properties`
* `pattern_properties`
* `additional_properties`
* `min_properties`
* `max_properties`
* `required`

### Nested

* `schema` - A schema class. **Required**

## Custom field types
