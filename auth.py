import models as db
async def password_auth(user: db.User, password: str):
    return True

async def token_auth(user. db.User, token: str):
    return True