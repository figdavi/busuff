from fastapi import APIRouter
from sqlalchemy import select
from app.core.database import SessionDep
from app.models import Device, DevicesOut


router = APIRouter(
    prefix="/devices",
    tags=["devices"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("/", status_code=200, response_model=DevicesOut)
async def read_devices(session: SessionDep):
    """
    Retorna todas as rotas cadastradas no banco para preencher a Dashboard
    """
    stmt = select(Device).order_by(Device.id)
    devices = session.scalars(stmt).all()

    return {"data": devices}
