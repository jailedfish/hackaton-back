from sqlalchemy.orm import declarative_base, Mapped, mapped_column, sessionmaker
from sqlalchemy import create_engine
from enums import Statuses, Types
from dataclasses import dataclass

engine = create_engine("sqlite:///database.db")
session = sessionmaker(engine)()

class Base(declarative_base()):
    __abstract__ = True
    id: Mapped[int] = mapped_column(autoincrement=True, nullable=False, primary_key=True)

class User(Base):
    __tablename__ = 'user'
    login: Mapped[str] = mapped_column(nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    car_number: Mapped[str] = mapped_column(nullable=False, unique=True)


class ParkingSpace(Base):
    __tablename__ = 'parkspace'
    _status: Mapped[str] = mapped_column(name='status', nullable=False, server_default=Types.RENTING)
    _type: Mapped[str] = mapped_column(name='type', nullable=False, server_default=Statuses.FREE)
    row: Mapped[int] = mapped_column(nullable=False)
    col: Mapped[int] = mapped_column(nullable=False)
    owner_id: Mapped[User] = mapped_column(nullable=False)
    owner: Mapped[User]
    def as_dict(self):
        return {'row': self.row, 'col': self.col, 'type': self._type, 'status': self._status}
