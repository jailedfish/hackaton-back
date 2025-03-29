from models import session
import models as db
from aiohttp.web import RouteTableDef, Request, json_response, Application
from hashlib import sha3_512
import re
from auth import password_auth, uuid4, redis, token_auth, extract_token
from datetime import timedelta
router = RouteTableDef()

@router.post('')
async def create_user(r: Request):
    try: 
        data = await r.json()
    except:
        return json_response({'message': 'error detected'}, status=400)
    
    if data.get('login') is None or data.get('password') is None or data.get('car_number') is None:
        return json_response({'message': 'wrong input signature'}, status=400)

    if not re.fullmatch('\\w{2}\\d{3}\\w\\d{2,3}', data.get('car_number')):
        return json_response({'message': 'wrong input signature'}, status=400)

    user = db.User(login=data.get('login'), password_hash=sha3_512(data.get('password').encode()).hexdigest(), car_number=data.get('car_number').lower())
    session.add(user)
    
    try:
        session.commit()
        return json_response(user.as_dict(), status=201)

    except Exception as e:
        session.rollback()
        print(e)
        return json_response({'message': 'error detected'}, status=500)
    

@router.get('/{id:\\d{1,}}')
async def get_user(r: Request):
    user = session.get(db.User, int(r.match_info['id']))

    if not await token_auth(user, extract_token(r)):
        return json_response({'message': 'Bearer Token Required'}, status=401)
    
    if user is None:
        return json_response({'message': 'user not found'}, status=404)
    return json_response(user.as_dict())

@router.delete('/{id:\\d{1,}}')
async def delete_user(r: Request):
    if not await token_auth(user, extract_token(r)):
        return json_response({'message': 'Bearer Token Required'}, status=401)
    
    user = session.get(db.User, int(r.match_info['id']))
    if user is None:
        return json_response({'message': 'user not found'}, status=404)
    session.delete(user)
    session.commit()
    redis.delete(f'login_{user.login}')
    return json_response(user.as_dict())

@router.patch('/{id:\\d{1,}}')
async def punch_user(r: Request):
    data = r.json()
    user = session.get(db.User, int(r.match_info['id']))

    if not await token_auth(user, extract_token(r)):
        return json_response({'message': 'Bearer Token Required'}, status=401)
    if user is None:
        return json_response({'message': 'user not found'}, status=404)
    
    if data.get('password') is not None:
        user.password_hash = sha3_512(data.get('password').encode()).hexdigest()
        return json_response(user.as_dict())
    
    if data.get('car_number') is not None:
        if re.fullmatch('\\w{2}\\d{3}\\w\\d{2,3}', data.get('car_number')):
            return json_response({'message': 'wrong input signature'})
        user.car_number = data.get('car_number')
        return json_response(user.as_dict())
    
    return json_response(user.as_dict(), status=203)

@router.get('/token')
async def get_token(r: Request):
    data = (await r.json())
    user = session.query(db.User).filter(db.User.login == data.get('login', '')).one_or_none()
    if user and await password_auth(user, data.get('password', '')):
        token = redis.get(f'token_{user.login}')
        if token is None:
            token = uuid4().hex
            redis.set(f'token_{user.login}', token, timedelta(hours=12))
        return json_response({'token': str(token)})
    else:
        return json_response({'message': 'Wrong password or user not found'}, status=401)
    
@router.patch('/balance/{id:\\d{1,}}')
async def free_money_mod(r: Request):
    try:
        data = await r.json()
    except:
        return json_response({'message': 'invalid input'}, status=400)
    
    user = session.get(db.User, r.match_info['id'])
    user.balance = int(data.get('balance', '0'))
    session.add(user)
    session.commit()
    return json_response(user.as_dict())


app = Application()
app.add_routes(router)