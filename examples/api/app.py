import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

import typesystem

users = []


user_schema = typesystem.Schema(
    fields={
        "username": typesystem.String(max_length=100),
        "is_admin": typesystem.Boolean(default=False),
    }
)


async def list_users(request):
    return JSONResponse({"users": [dict(user) for user in users]})


async def add_user(request):
    data = await request.json()
    user, errors = user_schema.validate_or_error(data)
    if errors:
        return JSONResponse(dict(errors), status_code=400)
    users.append(user)
    return JSONResponse(dict(user))


app = Starlette(
    routes=[
        Route("/", list_users, methods=["GET"]),
        Route("/", add_user, methods=["POST"]),
    ]
)


if __name__ == "__main__":
    uvicorn.run(app)
