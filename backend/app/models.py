from datetime import datetime, time
from pydantic import BaseModel
from sqlalchemy import Integer, String, Float, DateTime, ForeignKey, ARRAY, Index, Time
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column


# API models


class BaseOut(BaseModel):
    model_config = {"from_attributes": True}


class PositionCreate(BaseModel):
    vehicle_id: str
    timestamp_utc: datetime
    latitude: float | None
    longitude: float | None
    speed_kmh: float | None
    course_deg: float | None
    num_satellites: int | None
    hdop: float | None


class PositionOut(BaseOut):
    id: int
    timestamp_utc: datetime
    latitude: float
    longitude: float
    speed_kmh: float
    course_deg: float
    num_satellites: int
    hdop: float


class PositionsOut(BaseOut):
    data: list[PositionOut]


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


# Ref: https://docs.sqlalchemy.org/en/21/orm/basic_relationships.html


class Vehicle(BaseORM):
    __tablename__ = "vehicle"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(50))

    routes: Mapped[list["Route"]] = relationship(back_populates="vehicle")
    positions: Mapped[list["Position"]] = relationship(
        back_populates="vehicle", cascade="all, delete-orphan"
    )


class Position(BaseORM):
    __tablename__ = "position"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    vehicle_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("vehicle.id", ondelete="CASCADE"), nullable=False
    )
    vehicle: Mapped["Vehicle"] = relationship(back_populates="positions")

    timestamp_utc: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    speed_kmh: Mapped[float] = mapped_column(Float)
    course_deg: Mapped[float] = mapped_column(Float)
    num_satellites: Mapped[int] = mapped_column(Integer)
    hdop: Mapped[float] = mapped_column(Float)


Index("ix_position_vehicle_timestamp", Position.vehicle_id, Position.timestamp_utc)


class Route(BaseORM):
    __tablename__ = "route"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    vehicle_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("vehicle.id", ondelete="CASCADE"), nullable=False
    )
    vehicle: Mapped["Vehicle"] = relationship(back_populates="routes")

    origin: Mapped[str] = mapped_column(String(100), nullable=False)
    destination: Mapped[str] = mapped_column(String(100), nullable=False)

    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    # Ex: ["SEG", "TER"]
    days: Mapped[list[str]] = mapped_column(ARRAY(String(3)), nullable=False)
