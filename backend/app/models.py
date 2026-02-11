from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import (
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    ARRAY,
)
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column


# API models


class BaseOut(BaseModel):
    model_config = {"from_attributes": True}


class GPSReadingCreate(BaseModel):
    vehicle_id: str
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
    vehicle_id: str


class RouteOut(BaseOut):
    id: str
    vehicle_id: str
    origin: str
    destination: str
    time_range: str
    days: list[str]


class RoutesOut(BaseOut):
    data: list[RouteOut]


class VehicleOut(BaseOut):
    id: str
    name: str


class VehiclesOut(BaseOut):
    data: list[VehicleOut]


# DB models


class BaseORM(DeclarativeBase):
    pass


class Vehicle(BaseORM):
    __tablename__ = "vehicle"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(50))


class GPSReading(BaseORM):
    __tablename__ = "gps_reading"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vehicle_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("vehicle.id"), nullable=False
    )
    timestamp_utc: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    speed_kmh: Mapped[float] = mapped_column(Float)
    course_deg: Mapped[float] = mapped_column(Float)
    num_satellites: Mapped[int] = mapped_column(Integer)
    hdop: Mapped[float] = mapped_column(Float)

    vehicle = relationship("Vehicle")


class Route(BaseORM):
    __tablename__ = "route"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vehicle_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("vehicle.id"), nullable=False
    )

    origin: Mapped[str] = mapped_column(String(100), nullable=False)
    destination: Mapped[str] = mapped_column(String(100), nullable=False)

    # Ex (24hr format): start_time=06:00, end_time=09:00
    start_time: Mapped[str] = mapped_column(String(5), nullable=False)
    end_time: Mapped[str] = mapped_column(String(5), nullable=False)

    # Ex: ["SEG", "TER"]
    days: Mapped[list[str]] = mapped_column(ARRAY(String(3)), nullable=False)

    vehicle = relationship("Vehicle")
