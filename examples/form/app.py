from starlette.applications import Starlette
from starlette.responses import RedirectResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
import typesystem
import uvicorn

forms = typesystem.Jinja2Forms(package="bootstrap4")
templates = Jinja2Templates(directory="templates")
statics = StaticFiles(directory="statics", packages=["bootstrap4"])
bookings = []


class BookingSchema(typesystem.Schema):
    start_date = typesystem.Date(title="Start date")
    end_date = typesystem.Date(title="End date")
    room = typesystem.Choice(
        title="Room type",
        choices=[
            ("double", "Double room"),
            ("twin", "Twin room"),
            ("single", "Single room"),
        ],
    )
    include_breakfast = typesystem.Boolean(title="Include breakfast", default=False)

    def __str__(self):
        breakfast = (
            "(with breakfast)" if self.include_breakfast else "(without breakfast)"
        )
        return f"Booking for {self.room} from {self.start_date} to {self.end_date}"


async def homepage(request):
    form = forms.Form(BookingSchema)
    context = {"request": request, "form": form, "bookings": bookings}
    return templates.TemplateResponse("index.html", context)


async def make_booking(request):
    data = await request.form()
    booking, errors = BookingSchema.validate_or_error(data)
    if errors:
        form = forms.Form(BookingSchema, values=data, errors=errors)
        context = {"request": request, "form": form, "bookings": bookings}
        return templates.TemplateResponse("index.html", context)

    bookings.append(booking)
    return RedirectResponse(request.url_for("homepage"))


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
