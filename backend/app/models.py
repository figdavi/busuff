from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import (
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    ARRAY,
    Table,
    Column,
)
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


# Ref: https://docs.sqlalchemy.org/en/21/orm/basic_relationships.html#many-to-many

vehicle_route_association = Table(
    "vehicle_route",
    BaseORM.metadata,
    Column(
        "vehicle_id",
        String(32),
        ForeignKey("vehicle.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "route_id",
        Integer,
        ForeignKey("route.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Vehicle(BaseORM):
    __tablename__ = "vehicle"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(50))

    routes: Mapped[list["Route"]] = relationship(
        secondary=vehicle_route_association, back_populates="vehicles"
    )

    positions: Mapped[list["Position"]] = relationship(
        back_populates="vehicle", cascade="all, delete-orphan"
    )


class Position(BaseORM):
    __tablename__ = "position"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    vehicle_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("vehicle.id", ondelete="CASCADE"), nullable=False
    )

    timestamp_utc: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    speed_kmh: Mapped[float] = mapped_column(Float)
    course_deg: Mapped[float] = mapped_column(Float)
    num_satellites: Mapped[int] = mapped_column(Integer)
    hdop: Mapped[float] = mapped_column(Float)

    vehicle: Mapped["Vehicle"] = relationship(back_populates="positions")


class Route(BaseORM):
    __tablename__ = "route"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    origin: Mapped[str] = mapped_column(String(100), nullable=False)
    destination: Mapped[str] = mapped_column(String(100), nullable=False)

    # Ex (24hr format): start_time=06:00, end_time=09:00
    start_time: Mapped[str] = mapped_column(String(5), nullable=False)
    end_time: Mapped[str] = mapped_column(String(5), nullable=False)

    # Ex: ["SEG", "TER"]
    days: Mapped[list[str]] = mapped_column(ARRAY(String(3)), nullable=False)

    vehicles: Mapped[list["Vehicle"]] = relationship(
        secondary=vehicle_route_association, back_populates="routes"
    )
