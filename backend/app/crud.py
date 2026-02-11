from sqlalchemy.orm import Session
from app.models import Vehicle, Route, GPSReadingCreate, GPSReading


def save_gps_reading(session: Session, gps_reading: GPSReadingCreate) -> None:
    vehicle = get_or_create_vehicle(session, gps_reading.vehicle_id)
    gps_reading_dict = gps_reading.model_dump()
    gps_reading_db = GPSReading(**gps_reading_dict, vehicle=vehicle)

    session.add(gps_reading_db)


def get_or_create_vehicle(
    session: Session, vehicle_id: str, vehicle_name: str | None = None
):
    vehicle = session.get(Vehicle, vehicle_id)

    if vehicle is None:
        vehicle = Vehicle(id=vehicle_id, name=vehicle_name or f"Vehicle {vehicle_id}")
        session.add(vehicle)

    return vehicle


def save_route(
    session: Session,
    route_id: str,
    vehicle_id: str,
    origin: str,
    destination: str,
    days: list[str],
    time_range: str | None = None,
) -> None:
    new_route = Route(
        id=route_id,
        vehicle_id=vehicle_id,
        origin=origin,
        destination=destination,
        timeRange=time_range,
        days=days,
    )

    session.add(new_route)
