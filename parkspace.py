from aiohttp.web import RouteTableDef, Request, json_response
from aiohttp import web
import models as db
from enums import Statuses
from models import session

router = RouteTableDef()

@router.get('')
async def list_parkspaces(r: Request):
    data = [x.as_dict() for x in session.query(db.ParkingSpace).all()]
    return json_response(data)

@router.get('/{id:int}')
async def get_parkspace(r: Request):
    data = session.get(db.ParkingSpace, int(r.match_info('id')))
    if data is None:
        return json_response({}, status=404)
    return json_response(data.as_dict())

@router.patch('/{id:int}/book')
async def book_parkspace(r: Request):
    affected = session.query(db.ParkingSpace).filter(db.ParkingSpace.id == int(r.match_info('id'))).update({db.ParkingSpace._status: Statuses.BOOKED})
    if affected == 0:
        return json_response({}, status=404)
    return json_response(data = session.get(db.ParkingSpace, int(r.match_info('id'))).as_dict())

app = web.Application()
app.add_routes(router)