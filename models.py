from sqlalchemy.orm import declarative_base, Mapped, mapped_column, sessionmaker, relationship
from sqlalchemy import create_engine, ForeignKey
from enums import Statuses, Types, BookingType
from redis import Redis
from hashlib import sha3_512
from datetime import datetime
redis = Redis('localhost')
engine = create_engine("postgresql://bot:bot@localhost/bot_db")
session = sessionmaker(engine)()

class Base(declarative_base()):
    __abstract__ = True
    id: Mapped[int] = mapped_column(autoincrement=True, nullable=False, primary_key=True)

class User(Base):
    __tablename__ = 'user'
    login: Mapped[str] = mapped_column(nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    car_number: Mapped[str] = mapped_column(nullable=False, unique=True)

    def as_dict(self):
        return {'id': self.id, 'login': self.login, 'password_hash': self.password_hash, 'car_number': self.car_number}

class ParkingSpace(Base):
    __tablename__ = 'parkspace'
    _status: Mapped[str] = mapped_column(name='status', nullable=False, server_default=Statuses.FREE)
    _type: Mapped[str] = mapped_column(name='type', nullable=False, server_default=Types.RENTING)
    row: Mapped[int] = mapped_column(nullable=False)
    col: Mapped[int] = mapped_column(nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    owner: Mapped[User] = relationship(foreign_keys=[owner_id])
    
    def as_dict(self):
        return {'row': self.row, 'col': self.col, 'type': self._type, 'status': self._status}
    
class Booking(Base):
    __tablename__ = 'booking'
    parking_space_id: Mapped[int] = mapped_column(ForeignKey('parkspace.id'), nullable=False)
    parking_space: Mapped[ParkingSpace] = relationship(foreign_keys=[parking_space_id])
    booker_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    booker: Mapped[User] = relationship(foreign_keys=[booker_id])
    landlord_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    landlord: Mapped[User] = relationship(foreign_keys=[landlord_id])
    _type: Mapped[str] = mapped_column(nullable=False, server_default=BookingType.BOOKING)
    start_at: Mapped[datetime] = mapped_column(nullable=False)
    end_at: Mapped[datetime] = mapped_column(nullable=False)

    def as_dict(self):
        return {'type': self._type, 'booker': self.booker.as_dict(), 'landlord': self.landlord.as_dict(), 'start_at': self.start_at, 'end_at': self.end_at, 'parking_space': self.parking_space.as_dict()}

if session.get(User, 1) is None:
    session.add(User(login='admin', password_hash=sha3_512(b'The sun in the sky is red, The sun in my heart is Mao Zedong').hexdigest(), car_number='oo000o00'))
    session.commit()
