from aiohttp.web import RouteTableDef, Request, json_response
from aiohttp import web
import models as db
from datetime import datetime
from enums import Statuses
from models import session, redis
from auth import token_auth, extract_token

router = RouteTableDef()

@router.get('/{id:\\d{,4}}')
async def get_booking(r: Request):
    data = session.query(db.Booking).filter(db.Booking.id == int(r.match_info['id']) or (db.Booking.booker_id == int(r.match_info['id']) or int(r.match_info['id']) == 1)).one_or_none()
    
    if data is None:
        return json_response({'message': 'booking not found, is it exists?'}, status=404)
    
    if not (await token_auth(data.booker, extract_token(r))) or not (await token_auth(data.landlord, extract_token(r))):
        return json_response({'message': 'Invalid token'}, status=401)
    
    return json_response(data.as_dict())

@router.delete('/{id:\\d{,4}}')
async def cancel_booking(r: Request):
    data = session.query(db.Booking).filter(db.Booking.id == int(r.match_info['id'])).one_or_none()

    if data is None:
        return json_response({'message': 'booking not found, is it exists?'}, status=404)
    
    if not (await token_auth(data.booker, extract_token(r))) or not (await token_auth(data.landlord, extract_token(r))):
        return json_response({'message': 'Invalid token'}, status=401)
    session.delete(data)
    session.commit()
    
    return json_response(data.as_dict())
    

@router.get('/by_user/{id:\\d{,4}}')
async def get_booking(r: Request):
    data = session.query(db.Booking).filter(db.Booking.landlord_id == int(r.match_info['id']) \
                                            or (db.Booking.booker_id == int(r.match_info['id']) or int(r.match_info['id']) == 1)).one_or_none()
    
    if data is None:
        return json_response({'message': 'booking not found, is it exists?'}, status=404)
    
    if not (await token_auth(data.booker, extract_token(r))) or not (await token_auth(data.landlord, extract_token(r))):
        return json_response({'message': 'Invalid token'}, status=401)
    
    return json_response(data.as_dict())

app = web.Application()
app.add_routes(router)