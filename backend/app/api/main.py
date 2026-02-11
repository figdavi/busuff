from fastapi import APIRouter

from app.api.routers import routes, vehicles
# from app.core.config import settings

api_router = APIRouter()
api_router.include_router(routes.router)
api_router.include_router(vehicles.router)

# TODO: Design more and review current API endpoints
# TODO: change sqlalchemy queries to modern approach
