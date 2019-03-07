TypeSystem can convert it's validators to or from JSON Schema.

```python
import typesystem

data = {
    'type': 'string',
    'title': 'Username',
    'min_length': 1,
    'max_length': 100,
}
validator = typesystem.from_json_schema(data)
print(repr(validator))
```
