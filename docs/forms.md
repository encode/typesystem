TypeSystem gives you form rendering support, which you can either style and
customize yourself, or use together with a pre-packaged theme.

Let's take a look:

```python
import typesystem

forms = typesystem.Jinja2Forms(package="typesystem")  # Use the default templates.

class BookingSchema(typesystem.Schema):
    start_date = typesystem.Date()
    end_date = typesystem.Date()
    room = typesystem.Choice(choices=[
        ('double', 'Double room'),
        ('twin', 'Twin room'),
        ('single', 'Single room')
    ])
    include_breakfast = typesystem.Boolean(default=False)

form = forms.Form(BookingSchema)
print(form)
```

**app.py**

```python
from starlette import templating
import typesystem

forms = typesystem.Jinja2Forms(package="typesystem")
templates = templating.Jinja2Templates(directory="templates")

async def booking_page(request):
    message = request.session.get('message')
    request.session.clear()
    form = forms.Form(BookingSchema)
    context = {'request': request, 'form': form, 'message': message}
    return templates.TemplateResponse('index.html', context)


async def make_booking(request):
    data = await request.form()
    booking, errors = BookingSchema.validate(data)
    if errors:
        form = forms.Form(BookingSchema, values=data, errors=errors)
        context = {'request': request, 'form': form, 'message': None}
        return templates.TemplateResponse('index.html', context)

    request.session['message'] = f'Booking made: {booking}')
    return RedirectResponse(url='/')


app = Starlette(routes=[
    Route('/', booking_page, methods=['GET'])
    Route('/', make_booking, methods=['POST'])
])
```

**templates/index.html**:

```python
<html>
  <body>
    {% if message %}<div><p>{{message}}</p></div>{% endif %}
    <div>{{booking_form}}</div>
  </body>
</html>
```
