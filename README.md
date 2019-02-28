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

*IN PROGRESS.*

*Sketches*

### API

```python
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
import typesystem

users = []  # Mock datastore. This'll only work if running a single instance.


class User(typesystem.Schema):
    username = typesystem.String(max_length=100)
    is_admin = typesystem.Boolean(default=False)


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
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
import typesystem


forms = typesystem.Jinja2Forms(package="bootstrap4")
templates = Jinja2Templates(directory="templates")
statics = StaticFiles(directory="statics", packages=["bootstrap4"])

users = []


class User(typesystem.Schema):
    username = typesystem.String(max_length=100)
    is_admin = typesystem.Boolean(default=False)


async def homepage(request):
    form = forms.Form(User)
    return templates.TemplateResponse('index.html', {'users': users, 'form': form})


async def add_user(request):
    data = await request.form()
    user, errors = User.validate(data)
    if errors:
        form = forms.Form(User, values=data, errors=errors)
        return templates.TemplateResponse('index.html', {'form': form}, status_code=400)
    users.append(user)
    return RedirectResponse(url=request.url_for('homepage'))


app = Starlette(routes=[
    Route('/', homepage, methods=['GET']),
    Route('/', add_user, methods=['POST']),
    Mount('/static', app=statics, name='static')
])
```
