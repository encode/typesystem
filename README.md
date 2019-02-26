# TypeSystem

*IN PROGRESS.*

*TODO*

* All: Switch allow_null.
* String: Time. Nulls. allow_blank/allow_null coercions.
* Boolean: Exact.
* Time: Second/Millisecond/Microsecond precision.
* DateTime: Timezone. Second/Millisecond/Microsecond precision.
* Object: properties=Integer()


*Sketches*

### API

```python
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
import typesystem

users = []


class User(typesystem.Schema):
    username = typesystem.String(max_length=100)
    is_admin = typesystem.Boolean()


async def list_users(request):
    return JSONResponse([dict(user) for user in users])


async def add_user(request):
    data = await request.json()
    user, errors = User.validate(data)
    if errors:
        return JSONResponse(dict(errors), status_code=400)
    users.append(user)
    return JSONResponse(dict(user))


app = Starlette(routes=[
    Route('/', list_users, methods=["GET"]),
    Route('/', add_user, methods=["POST"]),
])
```

### Forms

```python
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.templating import Jinja2Templates
import typesystem


forms = typesystem.Jinja2Forms(package="bootstrap4")
templates = Jinja2Templates(directory="templates")
users = []


class User(typesystem.Schema):
    username = typesystem.String(max_length=100)
    is_admin = typesystem.Boolean()


class UserForm(forms.Form):
    schema = User


async def list_users(request):
    form = UserForm()
    return templates.TemplateResponse('index.html', {'users': users, 'form': form})


async def add_user(request):
    data = await request.form()
    user, errors = User.validate(data)
    if errors:
        form = UserForm(values=data, errors=errors)
        return templates.TemplateResponse('index.html', {'form': form}, status_code=400)
    users.append(user)
    return RedirectResponse(url=request.url_for('list_users'))


app = Starlette(routes=[
    Route(path='/', func=list_users, method="GET"),
    Route(path='/', func=add_user, method="POST"),
    Mount(path='/static', app=StaticFiles(packages=["bootstrap4"]), name="static")
])
```
