from aiohttp.web import RouteTableDef, Request, json_response
from aiohttp import web
import models as db
from datetime import datetime
from enums import Statuses
from models import session, redis
from auth import token_auth, extract_token

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



@router.get('/free')
async def list_free_parkspaces(r: Request):
    data = [x.as_dict() for x in session.query(db.ParkingSpace).filter(db.ParkingSpace._status == Statuses.FREE).all()]
    return json_response(data)


@router.get('/{id:\\d{,4}}/ex')
async def get_ex(r: Request):
    keys = redis.keys("booking_*_*")
    for i, key in enumerate(keys):
        if redis.get(key) == int(r.match_info['id']):
            return json_response({'ex': redis.expiretime(key[i])})
    return json_response({'message': 'Nothing was found, is it booked?'}, status=404)


