import models as db
from hashlib import sha3_512
from models import redis
from models import session
from aiohttp import web

from uuid import uuid4
from aiohttp.web import Request, RouteTableDef, json_response

router = RouteTableDef()

def extract_token(r: Request) -> str:
    print(r.headers.get('Authorization', '').split(' ')[-1])
    return r.headers.get('Authorization', '').split(' ')[-1]


async def password_auth(user: db.User, password: str) -> bool:
    if user is None:
        return False
    
    return user.password_hash == sha3_512(password.encode()).hexdigest()

async def token_auth(user: db.User, token: str) -> bool:
    if user is None:
        return False
    return str(redis.get(f'token_{user.login}')) == token

