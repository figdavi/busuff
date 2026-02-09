from fastapi import APIRouter
from sqlalchemy import select
from app.core.database import SessionDep
from app.models import Route, RoutesOut

router = APIRouter(
    prefix="/routes",
    tags=["routes"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("/", status_code=200, response_model=RoutesOut)
async def read_routes(session: SessionDep):
    """
    Retorna todas as rotas cadastradas no banco para preencher a Dashboard
    """
    stmt = select(Route).order_by(Route.id)
    routes = session.scalars(stmt).all()

    return {"data": routes}
