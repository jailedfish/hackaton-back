from aiohttp.web import RouteTableDef, Request, json_response
from aiohttp import web
import models as db
import asyncio
from enums import Statuses
from models import session
from parkspace import app as park_subapp


app = web.Application()
app.add_subapp('/parkspace/', park_subapp)

web.run_app(app)

