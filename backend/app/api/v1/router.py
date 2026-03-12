from fastapi import APIRouter

from app.api.v1.endpoints import admin, addresses, auth, org, projects

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(org.router)
api_router.include_router(projects.router)
api_router.include_router(addresses.router)
api_router.include_router(admin.router)
