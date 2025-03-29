from aiohttp.web import RouteDef, Request, json_response
from aiohttp import web
import models as db
import asyncio
from enums import Statuses
from models import session
from parkspace import app as park_subapp
from booking import app as booking_app
from users import app as user_subapp
import logging
from aiohttp.web import middleware

@middleware
async def logging_middleware(r: Request, handler):
    res = await handler(r)
    print(f'{r.path}, code: {res.status}')
    return res

app = web.Application(middlewares=[logging_middleware])
app.add_subapp('/parkspace/', park_subapp)
app.add_subapp('/user/', user_subapp)
app.add_subapp('/booking/', booking_app)

web.run_app(app)

