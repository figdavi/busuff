from fastapi import APIRouter, HTTPException
from app.crud import get_vehicles_with_last_position, get_last_position
from app.core.database import SessionDep
from app.models import Vehicle, VehicleWithPositionOut


router = APIRouter(
    prefix="/vehicles",
    tags=["vehicles"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("", status_code=200, response_model=list[VehicleWithPositionOut])
async def read_vehicles(session: SessionDep):
    vehicles_with_last_position = get_vehicles_with_last_position(session=session)

    vehicle_with_position_list: list[VehicleWithPositionOut] = [
        VehicleWithPositionOut.from_data(*vp.tuple())
        for vp in vehicles_with_last_position
    ]

    return vehicle_with_position_list


@router.get("/{vehicle_id}", status_code=200, response_model=VehicleWithPositionOut)
async def read_vehicle(session: SessionDep, vehicle_id: str):
    vehicle = session.get(Vehicle, vehicle_id)

    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    last_position = get_last_position(session=session, vehicle_id=vehicle_id)

    if not last_position:
        return VehicleWithPositionOut.from_data(vehicle, None)

    return VehicleWithPositionOut.from_data(vehicle, last_position)
