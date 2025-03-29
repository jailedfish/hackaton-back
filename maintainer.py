import models as db
from models import redis, session

while True: 
    keys = redis.keys('booking_*_*')
    for i, key in enumerate(keys):
        booking = session.query(db.Booking).filter(session.get(db.ParkingSpace.id, int(redis.get(key))) == db.Booking.booker_id).one_or_none()
        if redis.exists(f'payment_{booking.booker_id}'): 
            continue
        booking.booker.balance -= booking.price
        session.add(booking.booker)
        session.commit()
        redis.set(f'payment_{booking.booker_id}', value=True, ex=3600)
