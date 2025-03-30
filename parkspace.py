from aiohttp.web import RouteTableDef, Request, json_response
from aiohttp import web
import models as db
from datetime import datetime
from enums import Statuses
from models import session, redis
from auth import token_auth, extract_token
from enums import BookingType

router = RouteTableDef()
PRICE = 2000
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
        if str(redis.get(key)) == int(r.match_info['id']):
            return json_response({'ex': redis.expiretime(key[i])})
    return json_response({'message': 'Nothing was found, is it booked?'}, status=404)


@router.patch('/{id:\\d{,4}}/book')
async def book_parkspace(r: Request): 
    try:
        data = await r.json()
        reserve_time = datetime.strptime(data.get('start_date', ''), "%d/%m/%y %H:%M")
        end_time = datetime.strptime(data.get('end_date', ''), "%d/%m/%y %H:%M")
        if reserve_time < datetime.now():
            raise ValueError
    except ValueError as e:
        print(e)
        return json_response({'message': 'wrong date recieved'}, status=400)
    
    guest = session.get(db.User, int(data.get('id', '')))
    if not token_auth(guest, extract_token(r)):
        return json_response({'message': 'Bearer Token Required'}, status=401)
    
    if guest.balance < 0:
        return json_response({'message': 'Balance is negative :('}, status=402)
    
    affected = session.query(db.ParkingSpace).filter(db.ParkingSpace.id == int(r.match_info['id'])).update({db.ParkingSpace._status: Statuses.BOOKED})

    if affected == 0:
        return json_response({}, status=404)
    data = session.query(db.ParkingSpace).filter(db.ParkingSpace.id == int(r.match_info['id'])).one()
    data._status = Statuses.BOOKED
    booking = db.Booking(landlord_id=1, _type=BookingType.BOOKING, booker_id=guest.id, start_at=reserve_time, end_at=end_time, price=PRICE)
    session.add(data)
    session.add(booking)
    session.commit()
    redis.set(f'booking_1_{guest.id}', int(r.match_info['id']), (end_time - datetime.now()).total_seconds())
    return json_response(data.as_dict())


@router.patch('/{id:\\d{,4}}/reserve')
async def reserve_parkspace(r: Request):
    try:
        data = await r.json()
        reserve_time: datetime = datetime.strptime(data.get('start_date', ''), "%d/%m/%y %H:%M")
        end_time = datetime.strptime(data.get('end_date', ''), "%d/%m/%y %H:%M")
        if reserve_time < datetime.now():
            raise ValueError
    except ValueError as e:
        print(e)
        return json_response({'message': 'wrong date recieved'}, status=400)
    
    owner = session.get(db.User, int(data.get('id', '')))
    guest = session.get(db.User, int(data.get('guest_id', '')))
    if not token_auth(owner, extract_token(r)):
        return json_response({'message': 'Bearer Token Required'}, status=401)
    
    affected = session.query(db.ParkingSpace).filter(db.ParkingSpace.id == int(r.match_info['id'])) \
        .filter(db.ParkingSpace.owner_id == owner.id).update({db.ParkingSpace._status: Statuses.BOOKED})

    if affected == 0:
        return json_response({'message': 'Parking space not found or place isn\'t your'}, status=404)
    
    data = session.query(db.ParkingSpace).filter(db.ParkingSpace.id == int(r.match_info['id'])).one()
    data._status = Statuses.BOOKED
    booking = db.Booking(landlord_id=owner.id, _type=BookingType.BOOKING, booker_id=guest.id, start_at=reserve_time, end_at=end_time, price=0)
    session.add(data)
    session.add(booking)
    session.commit()
    
    redis.set(f'booking_{owner.id}_{guest.id}', int(r.match_info['id']), (end_time - datetime.now()).total_seconds())
    return json_response(data.as_dict())

@router.get('/{id:\\d{,4}}/booking')
async def get_booking(r: Request):
    data = session.query(db.Booking).filter(db.Booking.parking_space_id == int(r.match_info['id'])).one_or_none()
    
    if data is None:
        return json_response({'message': 'booking not found, is it exists?'}, status=404)
    
    if not (await token_auth(data.booker, extract_token(r))) or not (await token_auth(data.landlord, extract_token(r))):
        return json_response({'message': 'Invalid token'}, status=401)
    
    return json_response(data.as_dict())

@router.delete('/{id:\\d{,4}}/booking')
async def cancel_booking(r: Request):
    data = session.query(db.Booking).filter(db.Booking.parking_space_id == int(r.match_info['id'])).one_or_none()

    if data is None:
        return json_response({'message': 'booking not found, is it exists?'}, status=404)
    
    if not (await token_auth(data.booker, extract_token(r))) or not (await token_auth(data.landlord, extract_token(r))):
        return json_response({'message': 'Invalid token'}, status=401)
    session.delete(data)
    session.commit()
    
    return json_response(data.as_dict())

@router.get('/{id:\\d{,4}}/available_numbers')
async def get_available_numbers(r: Request):
    data = session.query(db.Booking).filter(db.Booking.parking_space_id == int(r.match_info['id'])).one_or_none()

    if data is None:
        return json_response({'message': 'booking not found, is it exists?'}, status=404)
    
    if not (await token_auth(data.booker, extract_token(r))) or not (await token_auth(data.landlord, extract_token(r))):
        return json_response({'message': 'Invalid token'}, status=401)
    
    return json_response([{'num': data.booker.car_number}, {'num': data.landlord.car_number}])

app = web.Application()
app.add_routes(router)