from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from app.core.database import SessionDep
from app.models import Vehicle, VehicleOut, VehiclesOut, Position, PositionOut


router = APIRouter(
    prefix="/vehicles",
    tags=["vehicles"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("/", status_code=200, response_model=VehiclesOut)
async def read_vehicles(session: SessionDep):
    stmt = select(Vehicle).order_by(Vehicle.id)
    vehicles = session.scalars(stmt).all()

    return {"data": vehicles}


@router.get("/{id}", status_code=200, response_model=VehicleOut)
async def read_vehicle(session: SessionDep, id: str):
    vehicle = session.get(Vehicle, id)

    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    return vehicle


@router.get("/{id}/last-position", status_code=200, response_model=PositionOut)
async def read_last_position(session: SessionDep, id: str):
    vehicle = session.get(Vehicle, id)

    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    # limit(1): Database will sort only one row instead of whole table (even though ORM is using .scalar())
    stmt = (
        select(Position)
        .where(Position.vehicle_id == id)
        .order_by(Position.timestamp_utc.desc())
        .limit(1)
    )
    last_position = session.scalar(stmt)

    if not last_position:
        raise HTTPException(status_code=404, detail="No positions found")

    return last_position
