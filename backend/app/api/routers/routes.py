from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from app.core.database import SessionDep
from app.models import Route, RouteOut, RoutesOut, Position, PositionOut

router = APIRouter(
    prefix="/routes",
    tags=["routes"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("/", status_code=200, response_model=RoutesOut)
async def read_routes(session: SessionDep):
    stmt = select(Route).order_by(Route.id)
    routes = session.scalars(stmt).all()

    return {"data": routes}


@router.get("/{id}", status_code=200, response_model=RouteOut)
async def read_route(session: SessionDep, id: int):
    route = session.get(Route, id)

    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    return route


@router.get("/{id}/last-position", response_model=PositionOut)
async def read_route_last_position(session: SessionDep, id: int):

    route = session.get(Route, id)

    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    stmt = (
        select(Position)
        .where(Position.vehicle_id == route.vehicle_id)
        .order_by(Position.timestamp_utc.desc())
        .limit(1)
    )

    last_position = session.scalar(stmt)

    if not last_position:
        raise HTTPException(status_code=404, detail="No positions found")

    return last_position
