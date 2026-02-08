from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    ARRAY,
)
from sqlalchemy.orm import DeclarativeBase, relationship

# TODO: switch data type declaration to SQLAlchemy 2.0 ORM
# TODO: Redo db design


# API models


class BaseOut(BaseModel):
    model_config = {"from_attributes": True}


class GPSReadingCreate(BaseModel):
    device_id: str
    timestamp_utc: datetime
    latitude: float | None
    longitude: float | None
    speed_kmh: float | None
    course_deg: float | None
    num_satellites: int | None
    hdop: float | None


class PresenceCreate(BaseModel):
    user_name: str
    route_id: str
    device_id: str


class RouteOut(BaseOut):
    id: str
    device_id: str
    origin: str
    destination: str
    time_range: str
    days: list[str]


class RoutesOut(BaseOut):
    data: list[RouteOut]


class DeviceOut(BaseOut):
    id: str
    name: str


# TODO: add count
class DevicesOut(BaseOut):
    data: list[DeviceOut]


# DB models


class BaseORM(DeclarativeBase):
    pass


class Device(BaseORM):
    __tablename__ = "device"

    id = Column(String(50), primary_key=True, unique=True, nullable=False)
    name = Column(String(100))


class GPSReading(BaseORM):
    __tablename__ = "gps_reading"

    id = Column(Integer, primary_key=True, autoincrement=True)

    device_id = Column(String(50), ForeignKey("device.id"), nullable=False)

    timestamp_utc = Column(DateTime, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    speed_kmh = Column(Float)
    course_deg = Column(Float)
    num_satellites = Column(Integer)
    hdop = Column(Float)
    # Permite acessar o objeto Device(leitura.device)
    device = relationship("Device")


class Route(BaseORM):
    __tablename__ = "route"
    bd_id = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(String(50), nullable=False, unique=True)

    device_id = Column(String(50), ForeignKey("device.id"), nullable=False)

    origin = Column(String(150), nullable=False)
    destination = Column(String(150), nullable=False)

    time_range = Column(String(150), nullable=False)

    # days é um array de strings (Ex: ["SEG", "TER"])
    days = Column(ARRAY(String(150)), nullable=False)

    # Permite acessar o objeto Device(leitura.device)
    device = relationship("Device")
