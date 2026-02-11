from fastapi import APIRouter

from app.api.routers import routes, vehicles

api_router = APIRouter()
api_router.include_router(routes.router)
api_router.include_router(vehicles.router)
