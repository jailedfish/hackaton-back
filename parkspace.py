from aiohttp.web import RouteTableDef, Request, json_response
from aiohttp import web
import models as db
from datetime import datetime
from enums import Statuses
from models import session, redis

router = RouteTableDef()

@router.get('')
async def list_parkspaces(r: Request):
    data = [x.as_dict() for x in session.query(db.ParkingSpace).all()]
    return json_response(data)

@router.get('/{id:[0-9]*$}')
async def get_parkspace(r: Request):
    data = session.get(db.ParkingSpace, int(r.match_info['id']))
    if data is None:
        return json_response({}, status=404)
    return json_response(data.as_dict())

@router.patch('/{id:\\d{,4}}/book')
async def book_parkspace(r: Request):
    book_time = datetime.strptime("%Y%m%dT%H%M%S.%fZ", r.match_info['date'])
    affected = session.query(db.ParkingSpace).filter(db.ParkingSpace.id == int(r.match_info['id'])).update({db.ParkingSpace._status: Statuses.BOOKED})
    if affected == 0:
        return json_response({}, status=404)
    data = session.query(db.ParkingSpace).filter(db.ParkingSpace.id == int(r.match_info['id'])).one()
    redis.set('')
    return json_response(data.as_dict())

@router.get('/free')
async def list_free_parkspaces(r: Request):
    data = [x.as_dict() for x in session.query(db.ParkingSpace).filter(db.ParkingSpace._status == Statuses.FREE).all()]
    return json_response(data)


app = web.Application()
app.add_routes(router)