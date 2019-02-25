# TypeSystem

*IN PROGRESS.*

*TODO*

All: Switch allow_null.
String: Time. Nulls. allow_blank/allow_null coercions.
Boolean: Exact.
Time: Second/Millisecond/Microsecond precision.
DateTime: Timezone. Second/Millisecond/Microsecond precision.
Object: properties=Integer()


*Sketches*

```python
forms = Jinja2Forms(package="bootstrap4")
users = []


class User(TypeSchema):
    username = String(max_length=100)
    is_admin = Boolean()


async def list_users(request):
    form = forms.Form(User)
    return templates.TemplateResponse('index.html', {'users': users, 'form': form})


async def add_user(request):
    data = await request.form()
    user, errors = User.validate(data)
    if errors:
        form = forms.Form(User, values=data, errors=errors)
        return templates.TemplateResponse('index.html', {'form': form}, status_code=400)
    users.append(user)
    return RedirectResponse(url=request.url_for('list_users'))


app = Starlette(routes=[
    Route(path='/', func=list_users, method="GET"),
    Route(path='/', func=add_user, method="POST"),
])
```


```python
users = []


class User(TypeSchema):
    username = String(max_length=100)
    is_admin = Boolean()


async def list_users(request):
    return JSONResponse([{"user": dict(user) for user in users}])


async def add_user(request):
    data = await request.json()
    user, errors = User.validate(data)
    if errors:
        return JSONResponse({"errors": dict(errors)}, status_code=400)
    users.append(user)
    return JSONResponse({"user": dict(user)})


app = Starlette(routes=[
    Route(path='/', func=list_users, method="GET"),
    Route(path='/', func=add_user, method="POST"),
])
```
