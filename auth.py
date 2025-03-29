import models as db
from hashlib import sha3_512
from models import redis
from models import session
from aiohttp import web
from datetime import timedelta
from uuid import uuid4
from aiohttp.web import Request, RouteTableDef, json_response

router = RouteTableDef()

async def password_auth(user: db.User, password: str) -> bool:
    if user is None:
        return False
    return user.password_hash == sha3_512(password.encode()).hexdigest()

async def token_auth(user: db.User, token: str) -> bool:
    if user is None:
        return False
    return redis.get(f'token_{user.login}') == token

@router.get('/token')
async def get_token(r: Request):
    data = (await r.json())
    user = session.query(db.User).filter(db.User.login == data.get('login', '')).one_or_none()
    if user and password_auth(user, data.get('password', '')):
        token = redis.get(f'token_{user.login}')
        if token is None:
            token = uuid4()
            redis.set(f'token_{user.login}', token, timedelta(hours=12))
        return token
    else:
        return json_response({'message': 'Wrong password or user not found'}, status=402)
    
