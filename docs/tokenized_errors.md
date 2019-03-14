For JSON and YAML content, TypeSystem can provide error messages with position
indicators showing exactly where the error occurred in the raw textual content.

```python
import typesystem

class Config(typesystem.Schema):
    num_worker_processes = typesystem.Integer()
    enable_auto_reload = typesystem.Boolean()

text = '''{
    "num_worker_processes": "x",
    "enable_auto_reload": "true"
}'''

try:
    typesystem.validate_json(text, validator=Config)
except (typesystem.ValidationError, typesystem.ParseError) as exc:
    for message in exc.messages():
        line_no = message.start_position.line_no
        column_no = message.start_position.column_no
        print(f"Error {message.text!r} at line {line_no}, column {column_no}.")
# Error 'Must be a number.' at line 2, column 29.
```

The two functions for parsing content and providing positional error messages are:

* `validate_json(text_or_bytes, validator)`
* `validate_yaml(text_or_bytes, validator)`

In both cases `validator` may either be a `Schema` class, or a `Field` instance.
