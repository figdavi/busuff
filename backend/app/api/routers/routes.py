from fastapi import APIRouter, HTTPException
from app.core.database import SessionDep
from app.models import (
    Route,
    Vehicle,
    Position,
    VehicleWithPositionOut,
    RouteOut,
    RouteDetailOut,
)
from app.crud import get_route, get_routes, get_vehicles_with_last_position

router = APIRouter(
    prefix="/routes",
    tags=["routes"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("", status_code=200, response_model=list[RouteOut] | list[RouteDetailOut])
async def read_routes(
    session: SessionDep, detailed: bool = False, is_active: bool | None = None
):
    """
    Get routes, filtered by 'is_active' query parameter. If is_active=True, returns only active routes, if is_active=False, returns only inactive routes, if no value is passed, returns all routes.
    """
    routes_orm = get_routes(session=session, detailed=detailed, is_active=is_active)
    routes: list[RouteOut | RouteDetailOut] = []

    if detailed:
        vp_list: list[tuple[Vehicle, Position]] = []
        for route_row in routes_orm:
            route_orm, is_active_value = route_row.tuple()
            vehicles_with_last_position = get_vehicles_with_last_position(
                session=session, route_id=route_orm.route_id
            )
            vp_list = [vp.tuple() for vp in vehicles_with_last_position]

            routes.append(RouteDetailOut.from_data(route_orm, vp_list, is_active_value))
    else:
        for route_row in routes_orm:
            route_value, is_active_value = route_row.tuple()
            routes.append(RouteOut.from_data(route_value, is_active_value))

    return routes


@router.get("/{route_id}", status_code=200, response_model=RouteDetailOut)
async def read_route(session: SessionDep, route_id: int):
    route_row = get_route(session=session, route_id=route_id)

    if not route_row:
        raise HTTPException(status_code=404, detail="Route not found")

    route_orm, is_active_value = route_row.tuple()

    vehicles_with_last_position = get_vehicles_with_last_position(
        session=session, route_id=route_orm.route_id
    )
    vp_list: list[tuple[Vehicle, Position]] = [
        vp.tuple() for vp in vehicles_with_last_position
    ]

    route = RouteDetailOut.from_data(route_orm, vp_list, is_active_value)

    return route


@router.get("/{route_id}/vehicles", response_model=list[VehicleWithPositionOut])
async def read_route_vehicles(session: SessionDep, route_id: int):
    """
    Get all vehicles in the current route + their last position
    """
    route_orm = session.get(Route, route_id)

    if not route_orm:
        raise HTTPException(status_code=404, detail="Route not found")

    vehicles_with_last_position = get_vehicles_with_last_position(
        session=session, route_id=route_orm.route_id
    )

    vp_out_list = [
        VehicleWithPositionOut.from_data(*vp.tuple())
        for vp in vehicles_with_last_position
    ]

    return vp_out_list
