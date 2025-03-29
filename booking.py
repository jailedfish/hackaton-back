from parkspace import *

@router.patch('/{id:\\d{,4}}/book')
async def reserve_parkspace(r: Request): 
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
    
    affected = session.query(db.ParkingSpace).filter(db.ParkingSpace.id == int(r.match_info['id'])).update({db.ParkingSpace._status: Statuses.BOOKED})

    if affected == 0:
        return json_response({}, status=404)
    data = session.query(db.ParkingSpace).filter(db.ParkingSpace.id == int(r.match_info['id'])).one()
    data.booker_id = guest.id
    data._status = Statuses.BOOKED
    session.add(data)
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
    data.booker_id = guest.id
    data._status = Statuses.BOOKED

    session.add(data)
    session.commit()
    
    redis.set(f'booking_{owner.id}_{guest.id}', int(r.match_info['id']), (end_time - datetime.now()).total_seconds())
    return json_response(data.as_dict())

@router.get('/{id:\\d{,4}}/booking')
async def get_booking(r: Request):
    
    

app = web.Application()
app.add_routes(router)