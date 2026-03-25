from datetime import datetime, time
from pydantic import BaseModel
from sqlalchemy import (
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Time,
    Column,
    Table,
    Index,
)
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column

# API models


class BaseOut(BaseModel):
    model_config = {"from_attributes": True}


class PositionBase(BaseModel):
    vehicle_id: str
    timestamp_utc: datetime
    lat: float
    lng: float
    speed_kmh: float | None
    course_deg: float | None
    num_satellites: int | None
    hdop: float | None


class PositionCreate(PositionBase):
    pass


class PositionOut(PositionBase, BaseOut):
    @classmethod
    def from_data(cls, position: "Position"):
        return cls(
            vehicle_id=position.vehicle_id,
            timestamp_utc=position.timestamp_utc,
            lat=position.lat,
            lng=position.lng,
            speed_kmh=position.speed_kmh,
            course_deg=position.course_deg,
            num_satellites=position.num_satellites,
            hdop=position.hdop,
        )


class VehicleOut(BaseOut):
    vehicle_id: str
    vehicle_label: str

    @classmethod
    def from_data(cls, vehicle: "Vehicle"):
        return cls(vehicle_id=vehicle.vehicle_id, vehicle_label=vehicle.vehicle_label)


class VehicleWithPositionOut(BaseOut):
    vehicle_id: str
    vehicle_label: str
    position: PositionOut | None

    @classmethod
    def from_data(cls, vehicle: "Vehicle", position: "Position | None"):
        return cls(
            vehicle_id=vehicle.vehicle_id,
            vehicle_label=vehicle.vehicle_label,
            position=PositionOut.from_data(position) if position else None,
        )


class ServiceDayOut(BaseOut):
    service_id: int
    weekday: int  # 0–6


class ServiceOut(BaseOut):
    service_id: int
    service_name: str
    start_time: time
    end_time: time
    days: list[ServiceDayOut]


class StopOut(BaseOut):
    stop_id: int
    stop_name: str
    lat: float
    lng: float


class ItineraryOut(BaseOut):
    itinerary_id: int
    origin: str
    destination: str

    stops: list[StopOut]


class RouteOut(BaseOut):
    route_id: int
    route_short_name: str
    route_long_name: str
    service_id: int
    itinerary_id: int
    is_active: bool  # Computed in endpoint

    @classmethod
    def from_data(cls, route: "Route", is_active: bool):
        return cls(
            route_id=route.route_id,
            route_short_name=route.route_short_name,
            route_long_name=route.route_long_name,
            service_id=route.service_id,
            itinerary_id=route.itinerary_id,
            is_active=is_active,
        )


class RouteDetailOut(BaseOut):
    route_id: int
    route_short_name: str
    route_long_name: str
    vehicles: list[VehicleWithPositionOut]
    service: ServiceOut
    itinerary: ItineraryOut
    is_active: bool  # Computed in endpoint

    @classmethod
    def from_data(
        cls,
        route: "Route",
        vehicles_with_position: list[tuple["Vehicle", "Position"]],
        is_active: bool,
    ):
        return cls(
            route_id=route.route_id,
            route_short_name=route.route_short_name,
            route_long_name=route.route_long_name,
            vehicles=[
                VehicleWithPositionOut.from_data(vehicle=v, position=p)
                for v, p in vehicles_with_position
            ],
            service=ServiceOut.model_validate(route.service),
            itinerary=ItineraryOut(
                itinerary_id=route.itinerary.itinerary_id,
                origin=route.itinerary.origin,
                destination=route.itinerary.destination,
                stops=[
                    StopOut.model_validate(itinerary_stop.stop)
                    for itinerary_stop in route.itinerary.stops
                ],
            ),
            is_active=is_active,
        )


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
        ForeignKey("vehicle.vehicle_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "route_id",
        Integer,
        ForeignKey("route.route_id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


# Ref: https://gtfs.org/documentation/realtime/feed-entities/vehicle-positions/#vehicledescriptor
class Vehicle(BaseORM):
    __tablename__ = "vehicle"
    vehicle_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    vehicle_label: Mapped[str] = mapped_column(String(50))

    routes: Mapped[list["Route"]] = relationship(
        secondary=vehicle_route_association, back_populates="vehicles"
    )

    positions: Mapped[list["Position"]] = relationship(
        back_populates="vehicle", cascade="all, delete-orphan"
    )


# Ref: https://gtfs.org/documentation/realtime/feed-entities/vehicle-positions/#position
class Position(BaseORM):
    __tablename__ = "position"
    position_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    vehicle_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("vehicle.vehicle_id", ondelete="CASCADE"), nullable=False
    )
    vehicle: Mapped["Vehicle"] = relationship(back_populates="positions")

    timestamp_utc: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)
    speed_kmh: Mapped[float] = mapped_column(Float)
    course_deg: Mapped[float] = mapped_column(Float)
    num_satellites: Mapped[int] = mapped_column(Integer)
    hdop: Mapped[float] = mapped_column(Float)


Index(
    "ix_position_vehicle_timestamp", Position.vehicle_id, Position.timestamp_utc.desc()
)


# Ref: https://gtfs.org/documentation/schedule/reference/#routestxt
class Route(BaseORM):
    __tablename__ = "route"
    route_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    route_short_name: Mapped[str] = mapped_column(String(16), nullable=False)
    route_long_name: Mapped[str] = mapped_column(String(50), nullable=False)

    service_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("service.service_id", ondelete="CASCADE"), nullable=False
    )
    service: Mapped["Service"] = relationship(back_populates="routes")

    itinerary_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("itinerary.itinerary_id", ondelete="CASCADE"),
        nullable=False,
    )
    itinerary: Mapped["Itinerary"] = relationship(back_populates="routes")

    vehicles: Mapped[list["Vehicle"]] = relationship(
        secondary=vehicle_route_association, back_populates="routes"
    )


# Ref: https://gtfs.org/documentation/schedule/reference/#calendartxt
class Service(BaseORM):
    __tablename__ = "service"
    service_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    service_name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    days: Mapped[list["ServiceDay"]] = relationship(
        back_populates="service", cascade="all, delete-orphan"
    )

    routes: Mapped[list["Route"]] = relationship(back_populates="service")


class ServiceDay(BaseORM):
    __tablename__ = "service_day"
    service_id: Mapped[int] = mapped_column(
        ForeignKey("service.service_id"), primary_key=True
    )
    weekday: Mapped[int] = mapped_column(Integer, primary_key=True)  # 0–6
    service: Mapped["Service"] = relationship(back_populates="days")


Index("ix_service_day_service_weekday", ServiceDay.service_id, ServiceDay.weekday)


# Ref: https://api-doc.transitapp.com/v3.html#model/itinerary
class Itinerary(BaseORM):
    __tablename__ = "itinerary"
    itinerary_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    origin: Mapped[str] = mapped_column(String(100), nullable=False)
    destination: Mapped[str] = mapped_column(String(100), nullable=False)

    stops: Mapped[list["ItineraryStop"]] = relationship(
        back_populates="itinerary",
        cascade="all, delete-orphan",
        order_by="ItineraryStop.stop_sequence",
    )

    routes: Mapped[list["Route"]] = relationship(back_populates="itinerary")


# Ref: https://gtfs.org/documentation/schedule/reference/#stop_timestxt,
# https://docs.sqlalchemy.org/en/21/orm/basic_relationships.html#association-object
class ItineraryStop(BaseORM):
    __tablename__ = "itinerary_stop"
    itinerary_id: Mapped[int] = mapped_column(
        ForeignKey("itinerary.itinerary_id", ondelete="CASCADE"), primary_key=True
    )
    itinerary: Mapped["Itinerary"] = relationship(back_populates="stops")

    stop_sequence: Mapped[int] = mapped_column(Integer, primary_key=True)

    stop_id: Mapped[int] = mapped_column(
        ForeignKey("stop.stop_id", ondelete="CASCADE"), nullable=False
    )
    stop: Mapped["Stop"] = relationship(back_populates="itineraries")


# Ref: https://api-doc.transitapp.com/v4.html#model/stop
class Stop(BaseORM):
    __tablename__ = "stop"
    stop_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stop_name: Mapped[str] = mapped_column(String(16))
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)

    itineraries: Mapped[list["ItineraryStop"]] = relationship(back_populates="stop")
