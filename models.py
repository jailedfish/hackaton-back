from sqlalchemy.orm import declarative_base, Mapped, mapped_column, sessionmaker
from enums import Statuses, Types
from redis import Redis

redis = Redis('localhost')
session = sessionmaker()()

class Base(declarative_base()):
    __abstract__ = True
    id: Mapped[int] = mapped_column(autoincrement=True, nullable=False, primary_key=True)

class User(Base):
    __tablename__ = 'user'
    login: Mapped[str] = mapped_column(nullable=False, unique=True)
    password_hash = mapped_column(nullable=False)
    


class ParkingSpace(Base):
    __tablename__ = 'parkspace'
    __status: Mapped[str] = mapped_column(name='status', nullable=False, server_default=Types.RENTING)
    __type: Mapped[str] = mapped_column(name='type', nullable=False, server_default=Statuses.FREE)
    row: Mapped[int] = mapped_column(nullable=False)
    col: Mapped[int] = mapped_column(nullable=False)