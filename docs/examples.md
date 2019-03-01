The following are examples of integrating `typesystem` against a Web framework.

## API validation & serialization

```python
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
import typesystem
import uvicorn

users = []


class User(typesystem.Schema):
    username = typesystem.String(max_length=100)
    is_admin = typesystem.Boolean(default=False)


async def list_users(request):
    return JSONResponse({"users": [dict(user) for user in users]})


async def add_user(request):
    data = await request.json()
    user, errors = User.validate_or_error(data)
    if errors:
        return JSONResponse(dict(errors), status_code=400)
    users.append(user)
    return JSONResponse(dict(user))


app = Starlette(routes=[
    Route('/', list_users, methods=["GET"]),
    Route('/', add_user, methods=["POST"]),
])


if __name__ == "__main__":
    uvicorn.run(app)
```

## Form rendering

**app.py**

```python
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
import typesystem
import uvicorn


forms = typesystem.Jinja2Forms(package="bootstrap4")
templates = Jinja2Templates(directory="templates")
statics = StaticFiles(packages=["bootstrap4"])

users = []


class User(typesystem.Schema):
    username = typesystem.String(max_length=100)
    is_admin = typesystem.Boolean(default=False)


async def homepage(request):
    form = forms.Form(User)
    return templates.TemplateResponse('index.html', {'users': users, 'form': form})


async def add_user(request):
    data = await request.form()
    user, errors = User.validate_or_error(data)
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


if __name__ == "__main__":
    uvicorn.run(app)
```

**templates/index.html**

```html
```
