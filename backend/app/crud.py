from sqlalchemy.orm import Session, selectinload, aliased
from sqlalchemy import select, and_, or_, exists, Row, func
from typing import Sequence
from datetime import datetime, timezone, timedelta
from app.models import (
    Vehicle,
    Route,
    PositionCreate,
    Position,
    Service,
    ServiceDay,
    Itinerary,
    ItineraryStop,
)
from app.utils import get_local_datetime


def create_position(*, session: Session, position: PositionCreate) -> Position:
    vehicle = get_or_create_vehicle(session=session, vehicle_id=position.vehicle_id)
    position_dict = position.model_dump()
    position_db = Position(**position_dict, vehicle=vehicle)

    session.add(position_db)

    return position_db


def get_or_create_vehicle(
    *, session: Session, vehicle_id: str, vehicle_label: str | None = None
):
    vehicle = session.get(Vehicle, vehicle_id)

    if vehicle is None:
        vehicle = Vehicle(id=vehicle_id, label=vehicle_label or f"Bus {vehicle_id}")
        session.add(vehicle)

    return vehicle


def create_route(
    *,
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


def get_routes(
    *,
    session: Session,
    datetime_utc: datetime | None = None,
    is_active: bool | None = None,
    detailed: bool = False,
) -> Sequence[Row[tuple[Route, bool]]]:
    """
    Returns routes, filtered by 'is_active' parameter. If is_active=True, returns only active routes, if is_active=False, returns only inactive routes, if no value is passed, returns all routes.
    A route is active if its service is currently active, where datetime_utc parameter is used determine it or, if not present, datetime.now()

    Args:
        session (Session): Database session to run queries.
        datetime_utc (datetime | None, optional): The datetime used to check if service is currently active. If not passed, datetime.now() is used. Defaults to None.
        is_active (bool | None, optional): Used to select routes which meet the given status value. Defaults to None.

    Returns:
        Sequence[Row[tuple[Route, bool]]]: list of (Route, is_active) that meet the parameters conditions.
    """

    # is_active logic:

    # 1. service starts and ends in the same day
    # 1.1 (0) no service today
    # 1.2 (0) service today and has not started or has ended already
    # 1.3 (1) service today and matches current datetime

    # 2. service crosses midnight
    # 2.1 (0) no service today and the day before
    # 2.2 (0) service today and has not started or has ended already
    # 2.3 (1) service today and still currently running
    # 2.4 (0) service yesterday and has already ended
    # 2.5 (1) service yesterday and still currently running

    datetime_local = get_local_datetime(datetime_utc)

    today_weekday = datetime_local.weekday()
    yesterday_weekday = (today_weekday - 1) % 7
    current_local_time = datetime_local.time()

    # 1.1, 1.2, 1.3
    same_day = and_(
        Service.start_time <= Service.end_time,
        exists().where(
            and_(
                ServiceDay.service_id == Service.service_id,
                ServiceDay.weekday == today_weekday,
            )
        ),
        Service.start_time <= current_local_time,
        current_local_time <= Service.end_time,
    )

    # 2.1 (overnight_today and overnight_yesterday)

    # 2.2, 2.3
    overnight_today = and_(
        Service.start_time > Service.end_time,
        exists().where(
            and_(
                ServiceDay.service_id == Service.service_id,
                ServiceDay.weekday == today_weekday,
            )
        ),
        current_local_time >= Service.start_time,
    )

    # 2.4, 2.5
    overnight_yesterday = and_(
        Service.start_time > Service.end_time,
        exists().where(
            and_(
                ServiceDay.service_id == Service.service_id,
                ServiceDay.weekday == yesterday_weekday,
            )
        ),
        current_local_time <= Service.end_time,
    )

    is_active_expr = or_(same_day, overnight_today, overnight_yesterday)

    stmt = (
        select(Route, is_active_expr.label("is_active"))
        .join(Route.service)
        .order_by(Route.route_id)
    )

    if detailed:
        stmt = stmt.options(
            selectinload(Route.vehicles),
            selectinload(Route.service).selectinload(Service.days),
            selectinload(Route.itinerary)
            .selectinload(Itinerary.stops)
            .selectinload(ItineraryStop.stop),
        )

    if is_active is True:
        stmt = stmt.where(is_active_expr)
    elif is_active is False:
        stmt = stmt.where(~is_active_expr)

    return session.execute(stmt).all()


def get_route(
    *,
    session: Session,
    route_id: int,
    datetime_utc: datetime | None = None,
):

    # is_active logic:

    # 1. service starts and ends in the same day
    # 1.1 (0) no service today
    # 1.2 (0) service today and has not started or has ended already
    # 1.3 (1) service today and matches current datetime

    # 2. service crosses midnight
    # 2.1 (0) no service today and the day before
    # 2.2 (0) service today and has not started or has ended already
    # 2.3 (1) service today and still currently running
    # 2.4 (0) service yesterday and has already ended
    # 2.5 (1) service yesterday and still currently running

    datetime_local = get_local_datetime(datetime_utc)

    today_weekday = datetime_local.weekday()
    yesterday_weekday = (today_weekday - 1) % 7
    current_local_time = datetime_local.time()

    # 1.1, 1.2, 1.3
    same_day = and_(
        Service.start_time <= Service.end_time,
        exists().where(
            and_(
                ServiceDay.service_id == Service.service_id,
                ServiceDay.weekday == today_weekday,
            )
        ),
        Service.start_time <= current_local_time,
        current_local_time <= Service.end_time,
    )

    # 2.1 (overnight_today and overnight_yesterday)

    # 2.2, 2.3
    overnight_today = and_(
        Service.start_time > Service.end_time,
        exists().where(
            and_(
                ServiceDay.service_id == Service.service_id,
                ServiceDay.weekday == today_weekday,
            )
        ),
        current_local_time >= Service.start_time,
    )

    # 2.4, 2.5
    overnight_yesterday = and_(
        Service.start_time > Service.end_time,
        exists().where(
            and_(
                ServiceDay.service_id == Service.service_id,
                ServiceDay.weekday == yesterday_weekday,
            )
        ),
        current_local_time <= Service.end_time,
    )

    is_active_expr = or_(same_day, overnight_today, overnight_yesterday)

    stmt = (
        select(Route, is_active_expr.label("is_active"))
        .where(Route.route_id == route_id)
        .join(Route.service)
        .order_by(Route.route_id)
        .options(
            selectinload(Route.vehicles),
            selectinload(Route.service).selectinload(Service.days),
            selectinload(Route.itinerary)
            .selectinload(Itinerary.stops)
            .selectinload(ItineraryStop.stop),
        )
    )

    route_row = session.execute(stmt).one_or_none()

    return route_row


def get_vehicles_with_last_position(*, session: Session, route_id: int | None = None):
    ten_minutes_ago_utc = datetime.now(timezone.utc) - timedelta(minutes=10)

    # recency_rank_table: (Position.position_id, Position.timestamp_utc, ..., "recency_rn")
    # "recency_rn": represents recency row number (how recent is a row, from 1 to n, based on timestamp)
    recency_rank_table = (
        select(
            Position,
            func.row_number()
            .over(
                partition_by=Position.vehicle_id,
                order_by=Position.timestamp_utc.desc(),
            )
            .label("recency_rn"),
        )
        .where(Position.timestamp_utc >= ten_minutes_ago_utc)
        .subquery()
    )

    last_position_subq = (
        select(recency_rank_table)
        .where(recency_rank_table.c.recency_rn == 1)
        .subquery()
    )

    # recency_alias_position wraps recency_rank_table (they're linked) and is treated as a Position-like object
    recency_alias_position = aliased(Position, last_position_subq)

    # outerjoin will allow every vehicle to be returned even if they don't have a valid last position
    stmt = select(Vehicle, recency_alias_position).outerjoin(
        recency_alias_position,
        recency_alias_position.vehicle_id == Vehicle.vehicle_id,
    )

    if route_id:
        stmt = stmt.join(Vehicle.routes).where(Route.route_id == route_id)

    return session.execute(stmt).all()


def get_last_position(*, session: Session, vehicle_id: str):

    ten_minutes_ago_utc = datetime.now(timezone.utc) - timedelta(minutes=10)

    # recency_rank_table: (Position.position_id, Position.timestamp_utc, ..., "recency_rn")
    # "recency_rn": represents recency row number (how recent is a row, from 1 to n, based on timestamp)
    recency_rank_table = (
        select(
            Position,
            func.row_number()
            .over(
                partition_by=Position.vehicle_id,
                order_by=Position.timestamp_utc.desc(),
            )
            .label("recency_rn"),
        )
        .where(Position.timestamp_utc >= ten_minutes_ago_utc)
        .subquery()
    )

    last_position_subq = (
        select(recency_rank_table)
        .where(recency_rank_table.c.recency_rn == 1)
        .subquery()
    )

    # recency_alias_position wraps recency_rank_table (they're linked) and is treated as a Position-like object
    recency_alias_position = aliased(Position, last_position_subq)

    # outerjoin and the or_(1, None) *will allow every vehicle to be returned even if they don't have a valid last position

    stmt = select(recency_alias_position).outerjoin(
        Vehicle,
        recency_alias_position.vehicle_id == Vehicle.vehicle_id,
    )

    return session.execute(stmt).scalar()
