import typesystem
import uvicorn
from starlette.applications import Starlette
from starlette.responses import RedirectResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

forms = typesystem.Jinja2Forms(package="bootstrap4")
templates = Jinja2Templates(directory="templates")
statics = StaticFiles(directory="statics", packages=["bootstrap4"])
bookings = []


booking_schema = typesystem.Schema(
    fields={
        "start_date": typesystem.Date(title="Start date"),
        "end_date": typesystem.Date(title="End date"),
        "room": typesystem.Choice(
            title="Room type",
            choices=[
                ("double", "Double room"),
                ("twin", "Twin room"),
                ("single", "Single room"),
            ],
        ),
        "include_breakfast": typesystem.Boolean(
            title="Include breakfast", default=False
        ),
    }
)


async def homepage(request):
    form = forms.create_form(booking_schema)
    context = {"request": request, "form": form, "bookings": bookings}
    return templates.TemplateResponse("index.html", context)


async def make_booking(request):
    data = await request.form()
    booking, errors = booking_schema.validate_or_error(data)
    if errors:
        form = forms.create_form(booking_schema)
        context = {"request": request, "form": form, "bookings": bookings}
        return templates.TemplateResponse("index.html", context)

    bookings.append(booking)
    return RedirectResponse(request.url_for("homepage"), status_code=303)


app = Starlette(
    debug=True,
    routes=[
        Route("/", homepage, methods=["GET"]),
        Route("/", make_booking, methods=["POST"]),
        Mount("/statics", statics, name="static"),
    ],
)


if __name__ == "__main__":
    uvicorn.run(app)
