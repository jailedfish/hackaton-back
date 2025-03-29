from sqlalchemy.orm import declarative_base, Mapped, mapped_column, sessionmaker, relationship
from sqlalchemy import create_engine, ForeignKey
from enums import Statuses, Types
from redis import Redis
from hashlib import sha3_512

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
    booker_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)
    booker: Mapped[User] = relationship(foreign_keys=[booker_id])
    def as_dict(self):
        return {'row': self.row, 'col': self.col, 'type': self._type, 'status': self._status}
    

if session.get(User, 1) is None:
    session.add(User(login='admin', password_hash=sha3_512(b'The sun in the sky is red, The sun in my heart is Mao Zedong').hexdigest(), car_number='oo000o00'))
    session.commit()
