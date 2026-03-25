from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from app.models import PositionCreate
from typing import Any

LOCAL_TZ = ZoneInfo("America/Sao_Paulo")


def get_local_datetime(datetime_utc: datetime | None = None) -> datetime:
    """Converts either datetime_utc to local timezone, if present, or returns datetime.now() in local timezone

    Args:
        datetime_utc (datetime | None, optional): Datetime to be converted. Defaults to None.

    Returns:
        datetime: returns datetime in local timezone
    """
    if datetime_utc is None:
        return datetime.now(LOCAL_TZ)

    if datetime_utc.tzinfo is None:
        datetime_utc = datetime_utc.replace(tzinfo=timezone.utc)

    return datetime_utc.astimezone(LOCAL_TZ)


def parse_position(position_json: dict[str, Any]) -> PositionCreate:
    position = PositionCreate.model_validate(position_json)
    return position
