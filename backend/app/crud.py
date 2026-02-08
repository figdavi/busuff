from sqlalchemy.orm import Session
from app.models import Device, Route, GPSReadingCreate, GPSReading


def save_gps_reading(session: Session, gps_reading: GPSReadingCreate) -> None:
    device = get_or_create_device(session, gps_reading.device_id)
    gps_reading_dict = gps_reading.model_dump()
    gps_reading_db = GPSReading(**gps_reading_dict, device=device)

    session.add(gps_reading_db)


def get_or_create_device(
    session: Session, device_id: str, device_name: str | None = None
):
    device = session.get(Device, device_id)

    if device is None:
        device = Device(id=device_id, name=device_name or f"Device {device_id}")
        session.add(device)

    return device


def save_route(
    session: Session,
    route_id: str,
    device_id: str,
    origin: str,
    destination: str,
    days: list[str],
    time_range: str | None = None,
) -> None:
    new_route = Route(
        id=route_id,
        device_id=device_id,
        origin=origin,
        destination=destination,
        timeRange=time_range,
        days=days,
    )

    session.add(new_route)
