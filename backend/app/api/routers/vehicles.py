from fastapi import APIRouter
from sqlalchemy import select
from app.core.database import SessionDep
from app.models import Vehicle, VehiclesOut


router = APIRouter(
    prefix="/vehicles",
    tags=["vehicles"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("/", status_code=200, response_model=VehiclesOut)
async def read_vehicles(session: SessionDep):
    """
    Retorna todas as rotas cadastradas no banco para preencher a Dashboard
    """
    stmt = select(Vehicle).order_by(Vehicle.id)
    vehicles = session.scalars(stmt).all()

    return {"data": vehicles}
